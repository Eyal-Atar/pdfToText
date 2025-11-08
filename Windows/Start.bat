@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title PDF Processor

echo Starting... Please wait.

REM Try to find Python
set "PY_EXE="
for /f "delims=" %%P in ('where python 2^>nul') do (
  set "PY_EXE=%%P"
  goto :have_python
)

echo Python not found. Installing... (this may take a few minutes)
set "PY_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
set "PY_TMP=%TEMP%\python_installer.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest '%PY_URL%' -OutFile '%PY_TMP%'" 2>nul
if not exist "%PY_TMP%" (
  echo Failed to download Python. Please check your internet connection.
  pause
  exit /b 1
)
start /wait "" "%PY_TMP%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
del /q "%PY_TMP%" 2>nul

REM Locate installed Python (common locations)
for %%D in (
  "%LocalAppData%\Programs\Python\Python311\python.exe"
  "%LocalAppData%\Programs\Python\Python312\python.exe"
  "%ProgramFiles%\Python311\python.exe"
  "%ProgramFiles%\Python312\python.exe"
) do (
  if exist "%%~fD" set "PY_EXE=%%~fD"
)

if not defined PY_EXE (
  for /f "delims=" %%P in ('where python 2^>nul') do set "PY_EXE=%%P"
)
if not defined PY_EXE (
  echo Python installation did not complete. Please restart your PC and run again.
  pause
  exit /b 1
)

:have_python
REM Ensure pip is available and up to date
"%PY_EXE%" -m ensurepip --upgrade >nul 2>&1
"%PY_EXE%" -m pip install --quiet --upgrade pip >nul 2>&1

echo Preparing environment...
"%PY_EXE%" -m pip install --user --quiet --disable-pip-version-check --no-warn-script-location pdfplumber python-bidi Pillow

echo Launching application...
"%PY_EXE%" "%~dp0pdf_batch_gui.py"

if errorlevel 1 (
  echo Application failed to start.
  pause
)

exit /b 0

