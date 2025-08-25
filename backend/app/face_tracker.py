from datetime import datetime, timedelta
from threading import Lock

class FaceTracker:
    def __init__(self, timeout_seconds=5):
        self.active_faces = {}
        self.events = []
        self.timeout = timedelta(seconds=timeout_seconds)
        self.lock = Lock()

    def update_face(self, name):
        with self.lock:
            now = datetime.now()
            if name not in self.active_faces:
                self.active_faces[name] = {
                    "first_seen": now,
                    "last_seen": now
                }
            else:
                self.active_faces[name]["last_seen"] = now

    def cleanup(self):
        """Check for faces that have disappeared"""
        with self.lock:
            now = datetime.now()
            to_remove = []
            for name, times in self.active_faces.items():
                if now - times["last_seen"] > self.timeout:
                    event = {
                        "name": name,
                        "first_seen": times["first_seen"],
                        "left_at": times["last_seen"],
                        "duration": str(times["last_seen"] - times["first_seen"])
                    }
                    self.events.append(event)
                    to_remove.append(name)
            for name in to_remove:
                del self.active_faces[name]

    def get_active(self):
        with self.lock:
            return [
                {
                    "name": name,
                    "first_seen": times["first_seen"].strftime("%Y-%m-%d %H:%M:%S")
                }
                for name, times in self.active_faces.items()
            ]

    def get_events(self):
        with self.lock:
            return [
                {
                    "name": event["name"],
                    "first_seen": event["first_seen"].strftime("%Y-%m-%d %H:%M:%S"),
                    "left_at": event["left_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    "duration": event["duration"]
                }
                for event in self.events
            ]

    def clear_events(self):
        with self.lock:
            self.events.clear()