@echo off
chcp 65001 >nul 2>&1
title PDF Processor

echo.
echo ════════════════════════════════════
echo      PDF Processor - Starting
echo ════════════════════════════════════
echo.

REM Check if Python exists
python --version >nul 2>&1
if errorlevel 1 (
    cls
    echo.
    echo ════════════════════════════════════════════════════════
    echo   Python NOT FOUND - Installation Required
    echo ════════════════════════════════════════════════════════
    echo.
    echo Please install Python first:
    echo.
    echo 1. Go to: https://www.python.org/downloads/
    echo 2. Download Python 3.9 or newer
    echo 3. During installation - CHECK "Add Python to PATH"
    echo 4. After installation - run this file again
    echo.
    echo ════════════════════════════════════════════════════════
    echo.
    echo Opening Python download page in your browser...
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/2] Python found - checking packages...

REM Install required packages silently
python -c "import pdfplumber" >nul 2>&1
if errorlevel 1 (
    echo Installing pdfplumber...
    pip install --quiet --disable-pip-version-check pdfplumber
)

python -c "import bidi" >nul 2>&1
if errorlevel 1 (
    echo Installing python-bidi...
    pip install --quiet --disable-pip-version-check python-bidi
)

python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing Pillow...
    pip install --quiet --disable-pip-version-check Pillow
)

echo [2/2] Starting application...
echo.

REM Run the application
python pdf_batch_gui.py

REM Only show error if application crashed
if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    echo.
    pause
)

exit /b 0

