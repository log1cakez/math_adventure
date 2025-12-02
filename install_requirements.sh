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

echo "[1/3] Installing pygame..."
$PIP_CMD install --upgrade pip
$PIP_CMD install pygame
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install pygame"
    exit 1
fi

echo ""
echo "[2/3] Installing moviepy for video playback..."
$PIP_CMD install "moviepy>=2.0.0"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install moviepy"
    exit 1
fi

echo ""
echo "[3/3] Installing numpy..."
$PIP_CMD install numpy
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install numpy"
    exit 1
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

