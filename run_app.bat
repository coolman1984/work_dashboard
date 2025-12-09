@echo off
REM Robust startup script for Work Dashboard
REM Points directly to the virtual environment python.exe to bypass PowerShell execution policies

set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"
set "MAIN_SCRIPT=%~dp0work_dashboard.py"

if exist "%VENV_PYTHON%" (
    echo Starting Work Dashboard...
    "%VENV_PYTHON%" "%MAIN_SCRIPT%"
) else (
    echo Error: Virtual environment not found at .venv\
    echo Please ensure dependencies are installed.
    pause
)
