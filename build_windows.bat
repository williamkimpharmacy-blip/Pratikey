@echo off
echo ============================================
echo   Pratikey — Windows Build
echo ============================================

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    pause
    exit /b 1
)

:: Install / upgrade dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet

:: Clean previous build
if exist dist\Pratikey rmdir /s /q dist\Pratikey
if exist build rmdir /s /q build

:: Build
echo Building Pratikey.exe ...
pyinstaller pratikey.spec --noconfirm

if errorlevel 1 (
    echo BUILD FAILED. Check the output above.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Build complete!
echo   Your app is in:  dist\Pratikey\
echo   Share the whole Pratikey folder with users
echo   They double-click Pratikey.exe to launch
echo ============================================
pause
