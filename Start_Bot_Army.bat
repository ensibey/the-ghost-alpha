@echo off
title The Ghost Alpha - Bot Army Commander
color 0A

echo ===================================================
echo     THE GHOST ALPHA - BULK DATA INGestion START
echo ===================================================
echo.
echo [1] Checking Virtual Environment...
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment 'venv' not found!
    echo Please make sure you are running this from the project root.
    pause
    exit /b
)

echo [2] Activating Environment...
call venv\Scripts\activate.bat

echo [3] Starting the Bot Army (main.py)...
echo ===================================================
echo Make sure Ollama is running in the background!
echo ===================================================
echo.

python main.py

echo.
echo ===================================================
echo    TASK COMPLETED OR TERMINATED
echo ===================================================
pause
