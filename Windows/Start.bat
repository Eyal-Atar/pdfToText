@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
set "APP_HOME=%LocalAppData%\PDFProcessor"
set "VENV=%APP_HOME%\venv"
set "PYTHONUTF8=1"
title PDF Processor

echo Starting...

REM -------- Find Python (prefer launcher) --------
set "PY_EXE="
for /f "delims=" %%E in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PY_EXE=%%E"
if not defined PY_EXE (
  for /f "delims=" %%P in ('where python 2^>nul') do set "PY_EXE=%%P"
)

REM -------- Install Python if missing --------
if not defined PY_EXE (
  echo Installing Python... (first time only)
  where winget >nul 2>&1
  if %errorlevel%==0 (
    winget install --id Python.Python.3.11 -e --silent --accept-package-agreements --accept-source-agreements >nul 2>&1
    for /f "delims=" %%E in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PY_EXE=%%E"
  )
)

if not defined PY_EXE (
  set "PY_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
  set "PY_TMP=%TEMP%\python_installer.exe"
  powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest '%PY_URL%' -OutFile '%PY_TMP%'" >nul 2>&1
  if exist "%PY_TMP%" (
    start /wait "" "%PY_TMP%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    del /q "%PY_TMP%" >nul 2>&1
    for /f "delims=" %%E in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PY_EXE=%%E"
    if not defined PY_EXE for /f "delims=" %%P in ('where python 2^>nul') do set "PY_EXE=%%P"
  )
)

if not defined PY_EXE (
  echo Could not install Python. Please restart and try again.
  pause
  exit /b 1
)

REM -------- Create cached venv (once) --------
if not exist "%VENV%\Scripts\python.exe" (
  echo Preparing environment... (first time only)
  "%PY_EXE%" -m venv "%VENV%" >nul 2>&1
  if not exist "%VENV%\Scripts\python.exe" (
    echo Failed to create environment.
    pause
    exit /b 1
  )
  "%VENV%\Scripts\python.exe" -m ensurepip --upgrade >nul 2>&1
  "%VENV%\Scripts\python.exe" -m pip install --quiet --upgrade pip >nul 2>&1
  "%VENV%\Scripts\python.exe" -m pip install --quiet --disable-pip-version-check --no-warn-script-location pdfplumber python-bidi Pillow >nul 2>&1
)

REM -------- Verify tkinter exists --------
"%VENV%\Scripts\python.exe" -c "import tkinter" >nul 2>&1
if errorlevel 1 (
  echo Your Python is missing tkinter. Reinstall Python from python.org.
  pause
  exit /b 1
)

REM -------- Launch GUI (no console) --------
start "" "%VENV%\Scripts\pythonw.exe" "%~dp0pdf_batch_gui.py"
exit /b 0

