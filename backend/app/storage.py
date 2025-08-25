import os
import sqlite3
from typing import List, Optional, Tuple
from datetime import datetime
from .settings import settings

os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.SNAP_DIR, exist_ok=True)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    angle TEXT NOT NULL,
    vec BLOB NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(person_id) REFERENCES people(id)
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER,
    label TEXT NOT NULL,
    confidence REAL,
    camera TEXT NOT NULL,
    snapshot_path TEXT,
    ts TEXT NOT NULL,
    FOREIGN KEY(person_id) REFERENCES people(id)
);
"""

def _conn():
    return sqlite3.connect(settings.DB_PATH)

def init_db():
    with _conn() as c:
        c.executescript(_SCHEMA)

def add_person(name: str) -> int:
    with _conn() as c:
        cur = c.cursor()
        cur.execute("INSERT INTO people(name, created_at) VALUES (?, ?)", (name, datetime.utcnow().isoformat()+"Z"))
        c.commit()
        return cur.lastrowid

def list_people() -> List[Tuple[int, str]]:
    with _conn() as c:
        rows = c.execute("SELECT id, name FROM people ORDER BY id").fetchall()
        return [(r[0], r[1]) for r in rows]

def delete_person(pid: int):
    with _conn() as c:
        c.execute("DELETE FROM embeddings WHERE person_id=?", (pid,))
        c.execute("DELETE FROM people WHERE id=?", (pid,))
        c.commit()

def add_embedding(person_id: int, angle: str, vec: bytes):
    with _conn() as c:
        c.execute("""INSERT INTO embeddings(person_id, angle, vec, created_at)
                     VALUES (?, ?, ?, ?)""",
                  (person_id, angle, vec, datetime.utcnow().isoformat()+"Z"))
        c.commit()

def get_embeddings() -> List[Tuple[int, str, bytes]]:
    with _conn() as c:
        rows = c.execute("SELECT person_id, angle, vec FROM embeddings").fetchall()
        return rows

def add_event(person_id: Optional[int], label: str, confidence: Optional[float], camera: str, snapshot_path: Optional[str]) -> int:
    with _conn() as c:
        cur = c.cursor()
        cur.execute("""INSERT INTO events(person_id, label, confidence, camera, snapshot_path, ts)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (person_id, label, confidence, camera, snapshot_path, datetime.utcnow().isoformat()+"Z"))
        c.commit()
        return cur.lastrowid

def recent_events(limit: int = 50):
    with _conn() as c:
        rows = c.execute("""SELECT e.id, e.ts, e.label, e.confidence, e.camera, e.snapshot_path, p.name
                            FROM events e
                            LEFT JOIN people p ON p.id = e.person_id
                            ORDER BY e.id DESC
                            LIMIT ?""", (limit,)).fetchall()
        out = []
        for (eid, ts, label, conf, cam, snap, pname) in rows:
            out.append({
                "id": eid,
                "timestamp": ts,
                "label": label,
                "confidence": conf,
                "camera": cam,
                "snapshot_path": snap,
                "person": pname
            })
        return out