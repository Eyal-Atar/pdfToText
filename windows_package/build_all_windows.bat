@echo off
chcp 65001 >nul
REM ============================================================
REM   בונה קובץ התקנה מלא לWindows
REM   PDF Processor - Build Complete Installer
REM ============================================================

title PDF Processor - Building Installer

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         PDF Processor - Windows Installer Builder         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM ====== בדיקת Python ======
echo [שלב 1/5] בודק Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ שגיאה: Python לא מותקן!
    echo.
    echo הורד והתקן Python מ: https://www.python.org/downloads/
    echo ☑ סמן "Add Python to PATH" בהתקנה
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VER=%%i
echo ✓ Python %PYTHON_VER% נמצא
echo.

REM ====== התקנת תלויות ======
echo [שלב 2/5] מתקין חבילות נדרשות...
pip install --quiet -r requirements_windows.txt
if errorlevel 1 (
    echo ❌ שגיאה בהתקנת חבילות
    pause
    exit /b 1
)
echo ✓ חבילות הותקנו
echo.

REM ====== ניקוי ======
echo [שלב 3/5] מנקה קבצים ישנים...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist installer_output rmdir /s /q installer_output
echo ✓ ניקוי הושלם
echo.

REM ====== בניית EXE ======
echo [שלב 4/5] בונה קובץ הפעלה (EXE)...
echo אנא המתן - זה יכול לקחת 2-5 דקות...
echo.
pyinstaller --name=PDF_Processor ^
    --onefile ^
    --windowed ^
    --clean ^
    --add-data="pdf_batch_processor.py;." ^
    --hidden-import=pdfplumber ^
    --hidden-import=PIL ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=bidi ^
    --hidden-import=bidi.algorithm ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.filedialog ^
    --hidden-import=tkinter.scrolledtext ^
    --hidden-import=tkinter.messagebox ^
    --noupx ^
    pdf_batch_gui.py >nul 2>&1

if errorlevel 1 (
    echo ❌ שגיאה בבניית EXE
    pause
    exit /b 1
)

if not exist "dist\PDF_Processor.exe" (
    echo ❌ קובץ EXE לא נוצר!
    pause
    exit /b 1
)
echo ✓ EXE נבנה בהצלחה
echo.

REM ====== בניית Installer ======
echo [שלב 5/5] בונה קובץ התקנה...

set INNO_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe

if "%INNO_PATH%"=="" (
    echo.
    echo ⚠ Inno Setup לא נמצא!
    echo.
    echo ניתן להוריד את ה-EXE ידנית מ: dist\PDF_Processor.exe
    echo.
    echo או להתקין Inno Setup מ: https://jrsoftware.org/isdl.php
    echo ואז להריץ שוב את הסקריפט הזה.
    echo.
    goto :end
)

"%INNO_PATH%" installer_setup.iss /Q
if errorlevel 1 (
    echo ❌ שגיאה בבניית Installer
    pause
    exit /b 1
)

if not exist "installer_output\PDF_Processor_Setup.exe" (
    echo ❌ קובץ התקנה לא נוצר!
    pause
    exit /b 1
)

REM ====== סיום מוצלח ======
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    ✓ בנייה הושלמה!                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📦 קובץ ההתקנה מוכן:
echo    installer_output\PDF_Processor_Setup.exe
echo.
echo 💾 גודל הקובץ:
for %%A in ("installer_output\PDF_Processor_Setup.exe") do echo    %%~zA bytes
echo.
echo ✅ מה עכשיו?
echo    1. הפץ את הקובץ PDF_Processor_Setup.exe למשתמשים
echo    2. משתמשים פשוט יריצו אותו - ההתקנה אוטומטית
echo    3. לא צריך Python או שום דבר נוסף!
echo.

:end
pause

