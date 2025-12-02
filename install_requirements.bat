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

echo [0/4] Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip/setuptools, continuing anyway...
)

echo.
echo [1/4] Installing pygame (using pre-built wheel)...
python -m pip install --only-binary :all: pygame
if errorlevel 1 (
    echo Attempting to install pygame (may take longer if building from source)...
    python -m pip install pygame
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install pygame
        echo.
        echo This usually means you need Microsoft Visual C++ Build Tools.
        echo Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
        echo Or try: python -m pip install --upgrade setuptools wheel
        pause
        exit /b 1
    )
)

echo.
echo [2/4] Installing numpy...
python -m pip install numpy
if errorlevel 1 (
    echo ERROR: Failed to install numpy
    pause
    exit /b 1
)

echo.
echo [3/4] Installing moviepy for video playback...
python -m pip install "moviepy>=2.0.0"
if errorlevel 1 (
    echo ERROR: Failed to install moviepy
    pause
    exit /b 1
)

echo.
echo [4/4] Verifying installation...
python -c "import pygame; import numpy; import moviepy; print('All packages installed successfully!')"
if errorlevel 1 (
    echo WARNING: Installation verification failed, but packages may still work.
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
