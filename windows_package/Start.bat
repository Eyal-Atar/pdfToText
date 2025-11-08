@echo off
chcp 65001 >nul 2>&1
title PDF Processor - הפעלה

echo.
echo ═══════════════════════════════════════════
echo         PDF Processor - מתחיל...
echo ═══════════════════════════════════════════
echo.

REM ===== בדיקת Python =====
echo [1/3] בודק Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠ Python לא מותקן - מוריד ומתקין אוטומטית...
    echo.
    
    REM הורדת Python installer
    echo מוריד Python 3.11...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python_installer.exe'}"
    
    if not exist "%TEMP%\python_installer.exe" (
        echo.
        echo ❌ שגיאה בהורדת Python
        echo.
        echo בבקשה הורד ידנית מ: https://www.python.org/downloads/
        echo ואז הרץ את הקובץ הזה שוב.
        echo.
        pause
        exit /b 1
    )
    
    REM התקנת Python
    echo מתקין Python...
    "%TEMP%\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    
    REM המתן לסיום התקנה
    timeout /t 5 /nobreak >nul
    
    REM רענון משתני סביבה
    call refreshenv >nul 2>&1
    
    REM בדיקה שנית
    python --version >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ⚠ Python הותקן אבל נדרש להפעיל מחדש את המחשב
        echo בבקשה הפעל מחדש והרץ שוב את הקובץ הזה.
        echo.
        pause
        exit /b 1
    )
    
    echo ✓ Python הותקן בהצלחה!
    echo.
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✓ Python %%i נמצא
    echo.
)

REM ===== התקנת חבילות =====
echo [2/3] בודק חבילות נדרשות...

python -c "import pdfplumber" >nul 2>&1
if errorlevel 1 (
    echo מתקין pdfplumber...
    pip install --quiet pdfplumber
)

python -c "import bidi" >nul 2>&1
if errorlevel 1 (
    echo מתקין python-bidi...
    pip install --quiet python-bidi
)

python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo מתקין Pillow...
    pip install --quiet Pillow
)

echo ✓ כל החבילות מותקנות
echo.

REM ===== הרצת התוכנית =====
echo [3/3] מפעיל את התוכנית...
echo.
echo ═══════════════════════════════════════════
echo.

python pdf_batch_gui.py

if errorlevel 1 (
    echo.
    echo.
    echo ═══════════════════════════════════════════
    echo ❌ שגיאה בהרצת התוכנית
    echo ═══════════════════════════════════════════
    pause
    exit /b 1
)

exit /b 0

