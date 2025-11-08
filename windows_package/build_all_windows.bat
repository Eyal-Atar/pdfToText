@echo off
REM Complete Windows Build Script
REM Builds EXE and Installer automatically

echo ============================================================
echo   PDF Processor - Complete Windows Build
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r requirements_windows.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo DONE
echo.

echo [2/4] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec
echo DONE
echo.

echo [3/4] Building EXE with PyInstaller...
pyinstaller --name=PDF_Processor --onefile --windowed --clean ^
    --add-data="pdf_batch_processor.py;." ^
    --hidden-import=pdfplumber ^
    --hidden-import=PIL ^
    --hidden-import=bidi ^
    --hidden-import=tkinter ^
    pdf_batch_gui.py

if errorlevel 1 (
    echo ERROR: PyInstaller build failed!
    pause
    exit /b 1
)
echo DONE
echo.

echo [4/4] Checking output...
if exist "dist\PDF_Processor.exe" (
    echo ============================================================
    echo   SUCCESS!
    echo ============================================================
    echo.
    echo EXE Location: dist\PDF_Processor.exe
    echo.
    echo Next steps:
    echo 1. Test the EXE: cd dist ^&^& PDF_Processor.exe
    echo 2. Build installer with Inno Setup (optional)
    echo.
) else (
    echo ERROR: EXE not created!
)

echo [OPTIONAL] Build installer with Inno Setup?
echo If you have Inno Setup installed, press Y
choice /c YN /n /m "Build installer? (Y/N): "
if errorlevel 2 goto :skip_installer
if errorlevel 1 goto :build_installer

:build_installer
echo.
echo Building installer...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_setup.iss
    if errorlevel 1 (
        echo WARNING: Installer build failed
    ) else (
        echo Installer created: installer_output\PDF_Processor_Setup.exe
    )
) else (
    echo Inno Setup not found at default location
    echo Install from: https://jrsoftware.org/isdl.php
)

:skip_installer
echo.
echo Build complete!
pause

