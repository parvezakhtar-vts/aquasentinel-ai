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

REM ---------- 1. Locate or install Python ----------
call :find_python
if defined PYEXE goto have_python

echo Python was not found. Downloading it directly now...
echo.

REM Choose the right installer for this PC (64-bit or ARM).
set "PYVER=3.12.7"
set "PYARCH=amd64"
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "PYARCH=arm64"
set "PYURL=https://www.python.org/ftp/python/%PYVER%/python-%PYVER%-%PYARCH%.exe"
set "PYINST=%TEMP%\aqua-python-%PYVER%-%PYARCH%.exe"
set "PYTARGET=%LocalAppData%\Programs\Python\AquaSentinelPy312"

echo Downloading %PYURL%
echo ^(about 25 MB - please wait^)
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -UseBasicParsing -Uri '%PYURL%' -OutFile '%PYINST%' } catch { Write-Host $_.Exception.Message; exit 1 }"

if not exist "%PYINST%" goto try_winget

echo Installing Python ^(silent, no admin needed^)...
"%PYINST%" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 Include_pip=1 TargetDir="%PYTARGET%"

REM We told the installer exactly where to go, so use that path directly.
if exist "%PYTARGET%\python.exe" set "PYEXE=%PYTARGET%\python.exe"
if defined PYEXE goto have_python

REM Fallbacks: re-detect, then scan common install folders.
call :find_python
if defined PYEXE goto have_python
for /d %%D in ("%LocalAppData%\Programs\Python\Python3*") do if exist "%%D\python.exe" set "PYEXE=%%D\python.exe"
if defined PYEXE goto have_python

:try_winget
where winget >nul 2>&1
if errorlevel 1 goto manual_python
echo Direct download unavailable - trying winget as a backup...
winget install -e --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements
call :find_python
if defined PYEXE goto have_python
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
