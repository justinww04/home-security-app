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

run.bat                  # creates venv, installs deps, runs FastAPI on :8000# home-security-app

#TODO

-add a homepage --complete
-add admin controls --complete
-add profile management --partially complete
-add account creation and login page --partially complete



-working on frontend design -- complete
-adding a verified guests card - complete almost
-In verified guests I want active and un active guests tab
-trying to figure out best way for phone alerts
-working on an app home screen
