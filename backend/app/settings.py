import os

class Settings:
        #Camera settings
    
    # Camera index for OpenCV (0 is default webcam). For GoPro in Webcam Mode, it should appear as a normal camera.
    CAMERA_INDEX: int = int(os.getenv("CAMERA_INDEX", "0"))
    # MJPEG frame rate for the HTTP stream
    MJPEG_FPS: int = int(os.getenv("MJPEG_FPS", "20"))

    # Recognition thresholds
    MIN_FACE_PX: int = int(os.getenv("MIN_FACE_PX", "120"))   # min face width in pixels
    SIMILARITY_THRESH: float = float(os.getenv("SIMILARITY_THRESH", "0.7"))  # cosine similarity
    MULTI_FRAME_N: int = int(os.getenv("MULTI_FRAME_N", "6"))
    MULTI_FRAME_REQUIRED: int = int(os.getenv("MULTI_FRAME_REQUIRED", "3"))
    PERSON_COOLDOWN_SEC: int = int(os.getenv("PERSON_COOLDOWN_SEC", "180"))  # 3 minutes

    # Storage paths
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    SNAP_DIR: str = os.path.join(DATA_DIR, "snaps")
    DB_PATH: str = os.path.join(DATA_DIR, "storage.db")

    # CORS / Frontend
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

settings = Settings()
