@echo off
setlocal
cd %~dp0
if not exist venv (
  py -3 -m venv venv
)
call venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
set "PYTHONPATH=%cd%"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload