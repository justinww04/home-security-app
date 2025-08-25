# Home Security App (MVP)

Backend: FastAPI + InsightFace (GPU if available)  
Frontend: React + Vite

## Prereqs
- Windows 10/11 with Python 3.11+
- NVIDIA drivers + CUDA (optional but recommended)
- Node.js LTS (v20+)

## 1) Backend
```bash
cd backend
copy .env.example .env   # (optional) tweak values
run.bat                  # creates venv, installs deps, runs FastAPI on :8000