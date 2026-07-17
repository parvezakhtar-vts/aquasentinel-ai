@echo off
cd /d "%~dp0"
title AquaSentinel AI - Setup

echo ==================================================
echo    AquaSentinel AI  -  One-time Windows Setup
echo ==================================================
echo.
echo This installs everything the dashboard needs.
echo It can take 5-15 minutes and needs an internet connection.
echo You only have to run this ONCE.
echo.

REM ---------- 1. Locate Python ----------
call :find_python
if defined PYEXE goto have_python

echo Python was not found. Trying to install it automatically...
echo.
where winget >nul 2>&1
if errorlevel 1 (
    echo winget not available - downloading the official Python installer...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe' -OutFile \"$env:TEMP\python-setup.exe\" } catch { exit 1 }"
    if errorlevel 1 (
        echo Download failed.
        goto manual_python
    )
    echo Installing Python ^(please wait, this is silent^)...
    "%TEMP%\python-setup.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1
) else (
    echo Installing Python via winget ^(please wait^)...
    winget install -e --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements
)

echo.
echo Finishing Python installation...
call :find_python
if defined PYEXE goto have_python

REM Last resort: scan the usual per-user install folders
for /d %%D in ("%LocalAppData%\Programs\Python\Python3*") do if exist "%%D\python.exe" set "PYEXE=%%D\python.exe"
if defined PYEXE goto have_python

:manual_python
echo.
echo ---------------------------------------------------
echo  Could not install Python automatically.
echo  Please do this once, by hand:
echo    1^) Open  https://www.python.org/downloads/
echo    2^) Download Python 3.12 and run the installer.
echo    3^) On the FIRST screen, TICK "Add python.exe to PATH".
echo    4^) Click Install. When done, double-click setup.bat again.
echo ---------------------------------------------------
echo.
pause
exit /b 1

:have_python
echo Found Python:
"%PYEXE%" --version
echo.

REM ---------- 2. Create the private environment ----------
if not exist ".venv\Scripts\python.exe" (
    echo Creating a private Python environment ^(.venv^)...
    "%PYEXE%" -m venv .venv
)
set "VENVPY=.venv\Scripts\python.exe"
if not exist "%VENVPY%" (
    echo Could not create the environment. Please re-run setup.bat.
    pause
    exit /b 1
)

REM ---------- 3. Install the packages ----------
echo Installing packages ^(numpy, pandas, pillow, streamlit^)...
"%VENVPY%" -m pip install --upgrade pip
"%VENVPY%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Package install failed. Check the internet connection and re-run setup.bat.
    pause
    exit /b 1
)

REM ---------- 4. Warm up: make demo data + model cache ----------
echo Preparing demo samples...
"%VENVPY%" -c "from aqua import mock_data, classifier; mock_data.generate_pendrive('data/pendrive', per_class=3); classifier.classify('data/pendrive/images/sample_001.png')"

echo.
echo ==================================================
echo    Setup complete!  You are ready for the demo.
echo.
echo    To start the dashboard:  double-click  start.bat
echo ==================================================
echo.
pause
exit /b 0

REM ================= helper: find python =================
:find_python
set "PYEXE="
for /f "delims=" %%P in ('py -3 -c "import sys;print(sys.executable)" 2^>nul') do set "PYEXE=%%P"
if not defined PYEXE for /f "delims=" %%P in ('python -c "import sys;print(sys.executable)" 2^>nul') do set "PYEXE=%%P"
goto :eof
