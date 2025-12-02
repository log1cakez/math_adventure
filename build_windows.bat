@echo off
echo ========================================
echo Math Adventure Game - Windows Build
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.7 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
    echo PyInstaller installed successfully!
    echo.
)

echo Building Windows executable...
echo This may take a few minutes...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build using spec file
python -m PyInstaller math_adventure.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build complete!
echo ========================================
echo.
echo Your executable is located at:
echo   dist\MathAdventure.exe
echo.
echo File size: 
for %%A in (dist\MathAdventure.exe) do echo   %%~zA bytes
echo.
echo You can now distribute this single .exe file!
echo.
echo NOTE: The executable includes all assets (images, sounds, videos).
echo       No additional files are needed to run the game.
echo.
pause

