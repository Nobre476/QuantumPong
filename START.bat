@echo off
echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Instalando dependências necessárias...
pip install --upgrade pip
pip install fastapi uvicorn qiskit qiskit-aer

echo Iniciando o servidor...
start http://127.0.0.1:8000/docs
cd api
uvicorn main:app --reload

pause
