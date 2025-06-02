@echo off
color 0a
title Quantum Pong v5.0 - Iniciando Tudo!

echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo  INICIANDO QUANTUM PONG v5.0
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo.

echo [1/3] 🐍 Ativando Ambiente Python...
rem Remove o venv existente e cria um novo
rmdir /s /q venv 2>nul
python -m venv venv || (
    echo ❌ ERRO: Falha ao criar venv. Verifique se o Python est� instalado!
    pause
    exit /b
)

echo [2/3] 📦 Instalando Pacotes (incluindo Qiskit)...
call venv\Scripts\activate || (
    echo ❌ ERRO: Falha ao ativar venv!
    pause
    exit /b
)

rem Atualiza pip e instala pacotes ESSENCIAIS
venv\Scripts\python -m pip install --upgrade pip --quiet || (
    echo ❌ ERRO: Falha ao atualizar pip!
    pause
    exit /b
)

pip install qiskit fastapi uvicorn --quiet || (
    echo ❌ ERRO: Falha ao instalar pacotes Python!
    pause
    exit /b
)

echo [3/3] 🚀 Iniciando API e Navegador...
echo.
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo  TUDO PRONTO! Abrindo navegador...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo.

timeout /t 5 /nobreak >nul
start "" "http://127.0.0.1:8000/docs"

uvicorn api.main:app --reload || (
    echo ❌ ERRO: Falha ao iniciar a API!
    echo Verifique se o arquivo main.py existe e est� correto.
    pause
    exit /b
)

pause