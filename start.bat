@echo off
cd /d "%~dp0"
title AquaSentinel AI - Dashboard

if not exist ".venv\Scripts\python.exe" (
    echo ---------------------------------------------------
    echo  Setup has not been run yet.
    echo  Please double-click  setup.bat  first ^(one time^).
    echo ---------------------------------------------------
    echo.
    pause
    exit /b 1
)

echo Starting the AquaSentinel AI dashboard...
echo.
echo  * A browser tab will open automatically ^(http://localhost:8501^)
echo  * KEEP THIS WINDOW OPEN during your demo
echo  * Close this window when you are finished
echo.
".venv\Scripts\python.exe" -m streamlit run dashboard.py
echo.
echo Dashboard stopped.
pause
