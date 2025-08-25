import io
import time
import base64
from typing import Dict, List
import os
import threading
import json

import numpy as np
import cv2

from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from starlette.responses import StreamingResponse
from starlette.websockets import WebSocketState

from .settings import settings
from . import storage
from .camera import CameraStream
from .recognizer import (
    init_models,
    current_people_centroids,
    detect_and_recognize,
    jpeg_bytes,
    Debouncer,
    _decode_dataurl_jpeg,
    embed_face
)
from .schemas import *
from .schemas import PersonOut, EventOut, ActivePerson
from . import notifier
from .face_tracker import FaceTracker

app = FastAPI(title="Home Security Backend")

# ✅ FIXED CORS HERE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow frontend at localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tracker = FaceTracker()

@app.on_event("startup")
@repeat_every(seconds=1)
def cleanup_inactive_faces():
    tracker.cleanup()

# Init subsystems
storage.init_db()
init_models()
camera = CameraStream(index=settings.CAMERA_INDEX)
camera.start()
debouncer = Debouncer()

# WebSocket clients
ws_clients: set[WebSocket] = set()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/snapshot", responses={200: {"content": {"image/jpeg": {}}}}, response_class=Response)
def snapshot():
    frame = camera.get_frame()
    if frame is None:
        return Response(status_code=503)
    return Response(content=jpeg_bytes(frame), media_type="image/jpeg")

@app.get("/video.mjpg")
def video_mjpg():
    def gen():
        while True:
            frame = camera.get_frame()
            if frame is None:
                time.sleep(0.02)
                continue
            jpg = jpeg_bytes(frame)
            boundary = b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
            yield boundary + jpg + b"\r\n"
            time.sleep(1.0 / settings.MJPEG_FPS)
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/people", response_model=list[PersonOut])
def people():
    return [PersonOut(id=pid, name=name) for (pid, name) in storage.list_people()]

@app.delete("/people/{pid}")
def delete_person(pid: int):
    storage.delete_person(pid)
    return {"ok": True}

# Enrollment
_sessions: Dict[str, int] = {}

@app.post("/enroll/start", response_model=StartEnrollOut)
def enroll_start(payload: StartEnrollIn):
    pid = storage.add_person(payload.name)
    sid = base64.urlsafe_b64encode(os.urandom(9)).decode().rstrip("=")
    _sessions[sid] = pid
    return StartEnrollOut(session_id=sid, person_id=pid)

@app.post("/enroll/capture")
def enroll_capture(payload: CaptureIn):
    sid = payload.session_id
    pid = _sessions.get(sid)
    if not pid:
        return {"ok": False, "error": "invalid_session"}

    bgr = _decode_dataurl_jpeg(payload.image_b64)
    if bgr is None:
        return {"ok": False, "error": "bad_image"}

    vec = embed_face(bgr)
    if vec is None:
        return {"ok": False, "error": "no_face_or_small"}

    storage.add_embedding(pid, payload.angle, vec.tobytes())
    return {"ok": True}

@app.post("/enroll/finish")
def enroll_finish(payload: FinishEnrollIn):
    sid = payload.session_id
    if sid in _sessions:
        del _sessions[sid]
    return {"ok": True}

@app.get("/events", response_model=list[EventOut])
def events(limit: int = 50):
    return storage.recent_events(limit=limit)

# ✅ THIS IS THE "ACTIVE" ROUTE USED IN YOUR React APP
@app.get("/active", response_model=List[ActivePerson])
def get_active_faces():
    active = tracker.get_active()
    return [{"name": name, "first_seen": ts} for name, ts in active.items()]

@app.websocket("/ws/events")
async def ws_events(ws: WebSocket):
    await ws.accept()
    ws_clients.add(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        ws_clients.discard(ws)

def _broadcast_event(json_obj: dict):
    dead = []
    for ws in list(ws_clients):
        try:
            if ws.client_state == WebSocketState.CONNECTED:
                ws._send({"type": "websocket.send", "text": json.dumps(json_obj)})
        except Exception:
            dead.append(ws)
    for ws in dead:
        ws_clients.discard(ws)

# Recognition loop
def _recognition_loop():
    while True:
        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.02)
            continue
        centroids = current_people_centroids()
        label, pid, conf = detect_and_recognize(frame, centroids)

        if label not in ("no_face", "face_too_small"):
            tracker.update_face("Unknown" if pid is None else label)

            fired = debouncer.update("Unknown" if pid is None else label)
            if fired:
                snap_name = f"{int(time.time())}.jpg"
                snap_path = os.path.join(settings.SNAP_DIR, snap_name)
                with open(snap_path, "wb") as f:
                    f.write(jpeg_bytes(frame))

                eid = storage.add_event(pid, fired, conf if pid is not None else None, "Front Door", snap_path)
                notifier.notify(fired if pid is not None else "Unknown person at front door", conf)

                payload = {
                    "id": eid,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "label": fired if pid is not None else "Unknown",
                    "confidence": conf if pid is not None else None,
                    "camera": "Front Door",
                    "snapshot_path": snap_path
                }
                _broadcast_event(payload)

        time.sleep(0.05)

threading.Thread(target=_recognition_loop, daemon=True).start()

@app.get("/")
def root():
    return {"ok": True, "msg": "Backend running"}