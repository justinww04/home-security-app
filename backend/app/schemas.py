from pydantic import BaseModel
from typing import Optional, List

class StartEnrollIn(BaseModel):
    name: str

class StartEnrollOut(BaseModel):
    session_id: str
    person_id: int

class CaptureIn(BaseModel):
    session_id: str
    angle: str          # "left", "right", "up", "down", "center"
    image_b64: str      # data:image/jpeg;base64,...

class FinishEnrollIn(BaseModel):
    session_id: str

class PersonOut(BaseModel):
    id: int
    name: str

class EventOut(BaseModel):
    id: int
    timestamp: str
    label: str
    confidence: Optional[float]
    camera: str
    snapshot_path: Optional[str]
    person: Optional[str]

class ActivePerson(BaseModel):
    name: str
    first_seen: str
    left_at: Optional[str] = None