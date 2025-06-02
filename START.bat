@echo off
color 0a
title Quantum Pong v5.0 - Iniciando!

echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo  INICIANDO QUANTUM PONG v5.0
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo.

echo [1/3] 🐍 Ativando Ambiente Python...
call python -m venv venv 2>nul || (
    echo ❌ Python não encontrado! Instale Python 3.10+ primeiro.
    pause
    exit /b
)
call venv\Scripts\activate

echo [2/3] 📦 Instalando Pacotes...
rem Atualiza o pip corretamente
venv\Scripts\python -m pip install --upgrade pip --quiet
pip install fastapi uvicorn --quiet

echo [3/3] 🚀 Iniciando API e Navegador...
echo.
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo  TUDO PRONTO! Abrindo navegador...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo.

timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8000/docs"

uvicorn api.main:app --reload
pause