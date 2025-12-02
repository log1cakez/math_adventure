#!/bin/bash

echo "========================================"
echo "Math Adventure Game - Setup Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed!"
    echo "Please install Python 3.7 or higher from https://www.python.org/"
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    PIP_CMD=pip3
else
    PYTHON_CMD=python
    PIP_CMD=pip
fi

echo "Python found! Installing dependencies..."
echo ""

echo "[0/4] Upgrading pip and setuptools..."
$PIP_CMD install --upgrade pip setuptools wheel
if [ $? -ne 0 ]; then
    echo "WARNING: Failed to upgrade pip/setuptools, continuing anyway..."
fi

echo ""
echo "[1/4] Installing pygame..."
$PIP_CMD install pygame
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install pygame"
    echo ""
    echo "On Linux, you may need to install system dependencies:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-dev libsdl2-dev"
    echo "  Fedora: sudo dnf install python3-devel SDL2-devel"
    exit 1
fi

echo ""
echo "[2/4] Installing numpy..."
$PIP_CMD install numpy
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install numpy"
    exit 1
fi

echo ""
echo "[3/4] Installing moviepy for video playback..."
$PIP_CMD install "moviepy>=2.0.0"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install moviepy"
    exit 1
fi

echo ""
echo "[4/4] Verifying installation..."
$PYTHON_CMD -c "import pygame; import numpy; import moviepy; print('All packages installed successfully!')"
if [ $? -ne 0 ]; then
    echo "WARNING: Installation verification failed, but packages may still work."
fi

echo ""
echo "========================================"
echo "Installation complete!"
echo "========================================"
echo ""
echo "You can now run the game with:"
echo "  $PYTHON_CMD main.py"
echo ""
echo "NOTE: For video playback, you may also need FFmpeg:"
echo "  macOS: brew install ffmpeg"
echo "  Linux: sudo apt install ffmpeg"
echo ""

