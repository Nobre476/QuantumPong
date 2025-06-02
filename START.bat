@echo off
cd /d N:\Quantum_Pong\api
start cmd /k "uvicorn main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5
start http://127.0.0.1:8000/docs
start N:\Quantum_Pong\frontend\index.html