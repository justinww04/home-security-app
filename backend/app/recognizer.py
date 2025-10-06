import time
import base64
import io
from typing import Dict, Optional, Tuple, List
import numpy as np
import cv2
from collections import deque, defaultdict
from datetime import datetime

# InsightFace for detection+embedding
from insightface.app import FaceAnalysis
import numpy.typing as npt

from .settings import settings
from . import storage

# Initialize models once
_face_app: Optional[FaceAnalysis] = None

def init_models():
    global _face_app
    if _face_app is not None:
        return
    _face_app = FaceAnalysis(name="buffalo_l")  # good default pack (det + rec)
    _face_app.prepare(ctx_id=0, det_size=(640, 640))  # ctx_id=0 uses GPU if available

def _cosine_sim(a: npt.NDArray[np.float32], b: npt.NDArray[np.float32]) -> float:
    a = a / (np.linalg.norm(a) + 1e-8)
    b = b / (np.linalg.norm(b) + 1e-8)
    return float(np.dot(a, b))

def _decode_dataurl_jpeg(b64: str) -> Optional[np.ndarray]:
    # Accepts "data:image/jpeg;base64,XXXX"
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    try:
        raw = base64.b64decode(b64)
    except Exception:
        return None
    arr = np.frombuffer(raw, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img

def current_people_centroids() -> Dict[int, Tuple[str, np.ndarray]]:
    # returns {person_id: (name, centroid_vec)}
    rows = storage.get_embeddings()
    per_person: Dict[int, List[np.ndarray]] = defaultdict(list)
    id_to_name = {pid: name for pid, name in storage.list_people()}
    for pid, _angle, vecblob in rows:
        vec = np.frombuffer(vecblob, dtype=np.float32)
        per_person[pid].append(vec)
    out: Dict[int, Tuple[str, np.ndarray]] = {}
    for pid, vecs in per_person.items():
        mat = np.vstack(vecs) if len(vecs) > 1 else vecs[0][None, :]
        centroid = mat.mean(axis=0)
        out[pid] = (id_to_name.get(pid, f"#{pid}"), centroid.astype(np.float32))
    return out

def embed_face(bgr: np.ndarray) -> Optional[np.ndarray]:
    assert _face_app is not None
    # detect the biggest face and produce its normed embedding
    faces = _face_app.get(bgr)
    if not faces:
        return None
    # choose largest by bbox size
    faces.sort(key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1]), reverse=True)
    f = faces[0]
    # gate on size
    w = f.bbox[2]-f.bbox[0]
    if w < settings.MIN_FACE_PX:
        return None
    return f.normed_embedding.astype(np.float32)

def detect_and_recognize(bgr: np.ndarray, person_centroids: Dict[int, Tuple[str, np.ndarray]]) -> Tuple[str, Optional[int], Optional[float]]:
    """Returns (label, person_id, confidence(similarity))"""
    assert _face_app is not None
    faces = _face_app.get(bgr)
    if not faces:
        return ("no_face", None, None)
    faces.sort(key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1]), reverse=True)
    f = faces[0]
    w = f.bbox[2]-f.bbox[0]
    if w < settings.MIN_FACE_PX:
        return ("face_too_small", None, None)
    emb = f.normed_embedding.astype(np.float32)

    best_pid, best_name, best_sim = None, None, -1.0
    for pid, (name, centroid) in person_centroids.items():
        sim = _cosine_sim(emb, centroid)
        if sim > best_sim:
            best_pid, best_name, best_sim = pid, name, sim

    if best_sim >= settings.SIMILARITY_THRESH:
        return (best_name, best_pid, best_sim)
    else:
        return ("Unknown", None, None)

def jpeg_bytes(bgr: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".jpg", bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    return buf.tobytes() if ok else b""

class Debouncer:
    def __init__(self):
        self.history = deque(maxlen=settings.MULTI_FRAME_N)
        self.cooldowns = {}  # label -> until timestamp

    def _on_cooldown(self, label: str) -> bool:
        until = self.cooldowns.get(label)
        return until is not None and time.time() < until

    def update(self, label: str) -> Optional[str]:
        # record label
        self.history.append((label, time.time()))

        # count most recent window
        labels = [l for (l, _) in self.history]
        # pick the most frequent label in the window
        candidate = max(set(labels), key=labels.count)
        count = labels.count(candidate)

        if count >= settings.MULTI_FRAME_REQUIRED and not self._on_cooldown(candidate):
            # set cooldown
            self.cooldowns[candidate] = time.time() + settings.PERSON_COOLDOWN_SEC
            return candidate
        return None
