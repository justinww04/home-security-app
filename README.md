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

-add a homepage --complete - changed-  new remodel done
-add admin controls --complete --added account deletetion page --- complete
-add profile management --complete
-add account creation and login page --complete -adding 2fa --currently adding sms verification for the 2 factor authentification. complete



-working on frontend design -- complete --remodeled
-adding a verified guests card - complete 
-In verified guests I want active and un active guests tab  - complete
-trying to figure out best way for phone alerts  - complete
-working on an app home screen - finished -- updated


-working on facial feature tracking -complete
-figuring out faster way to process user facial data to realtime camera view - complete
-realtime facial feature racognition -complete
-working on new facial recogniton script - complete - re working -- complete 

-still fine tuning facial feature recognition - complete
-fixing camera speed - complete
-fixing sms notifications -complete --updated
-fixing real time alerts via sms complete --- updated
-working on mobile version- complete
-fixing sudden errors - complete


-working on real time Ai Chat bot, it will be able to answer any questions needed for users
-using zapier to connect the chat bot to automate certain functions

