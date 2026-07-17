@echo off
cd /d "%~dp0"
title AquaSentinel AI - Terminal

REM Backup demo that needs NO browser and NO streamlit -- if start.bat ever
REM misbehaves at the demo table, double-click this instead.

if not exist ".venv\Scripts\python.exe" (
    echo Please run setup.bat first ^(one time^).
    echo.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" run.py
echo.
pause
