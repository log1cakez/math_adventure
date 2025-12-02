@echo off
echo ========================================
echo Math Adventure Game - Setup Script
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

echo Python found! Installing dependencies...
echo.

echo [1/3] Installing pygame...
python -m pip install --upgrade pip
python -m pip install pygame
if errorlevel 1 (
    echo ERROR: Failed to install pygame
    pause
    exit /b 1
)

echo.
echo [2/3] Installing moviepy for video playback...
python -m pip install moviepy>=2.0.0
if errorlevel 1 (
    echo ERROR: Failed to install moviepy
    pause
    exit /b 1
)

echo.
echo [3/3] Installing numpy...
python -m pip install numpy
if errorlevel 1 (
    echo ERROR: Failed to install numpy
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo You can now run the game with:
echo   python main.py
echo.
echo NOTE: For video playback, you may also need FFmpeg:
echo   Download from: https://ffmpeg.org/download.html
echo   Add to your system PATH
echo.
pause
