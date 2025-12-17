@echo off
chcp 65001 >nul
echo ========================================
echo Library Management System - Build
echo ========================================
echo.

REM Update pip first
echo Updating pip...
python -m pip install --upgrade pip

REM Install dependencies one by one
echo.
echo Installing dependencies (this may take a few minutes)...
pip install PyQt5==5.15.10
pip install SQLAlchemy==2.0.23
pip install bcrypt==4.1.2
pip install pyinstaller==6.3.0

echo.
echo Dependencies installed successfully!

REM Clean old builds
echo.
echo Cleaning old builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "*.spec" del /q *.spec

echo.
echo ========================================
echo Starting build (this may take 2-3 minutes)...
echo ========================================
echo.

REM Build application
pyinstaller --onedir ^
            --windowed ^
            --name="Library Management" ^
            --hidden-import=PyQt5 ^
            --hidden-import=PyQt5.QtCore ^
            --hidden-import=PyQt5.QtGui ^
            --hidden-import=PyQt5.QtWidgets ^
            --hidden-import=sqlalchemy ^
            --hidden-import=sqlalchemy.ext.declarative ^
            --hidden-import=bcrypt ^
            --collect-all PyQt5 ^
            --collect-all sqlalchemy ^
            --clean ^
            main.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Ready: dist\Library Management\Library Management.exe
    echo.
    echo You can run the program or share "dist\Library Management" folder
    echo.
) else (
    echo.
    echo ========================================
    echo BUILD ERROR!
    echo ========================================
    echo.
    echo Try:
    echo 1. Reinstall dependencies: pip install --force-reinstall PyQt5
    echo 2. Use library.spec file: pyinstaller library.spec
    echo.
)

pause