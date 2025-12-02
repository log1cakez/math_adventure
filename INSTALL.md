# Installation Guide

This guide will help you set up the Math Adventure Game on your computer.

## Prerequisites

- **Python 3.7 or higher** - [Download Python](https://www.python.org/downloads/)
- **FFmpeg** (optional) - For video/audio playback support

## Step-by-Step Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd math_adventure
```

### Step 2: Install Python Dependencies

Choose one of the following methods:

#### Option A: Automated Script (Easiest)

**Windows:**
```bash
install_requirements.bat
```

**Linux/Mac:**
```bash
chmod +x install_requirements.sh
./install_requirements.sh
```

#### Option B: Python Setup Script

```bash
python setup.py
```

#### Option C: Manual Installation

```bash
pip install -r requirements.txt
```

This will install:
- `pygame` - Game engine
- `moviepy>=2.0.0` - Video playback
- `numpy` - Numerical operations

### Step 3: Install FFmpeg (Optional but Recommended)

FFmpeg is needed for video playback and audio conversion.

**Windows:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add to PATH:
   - Open System Properties → Environment Variables
   - Add `C:\ffmpeg\bin` to PATH
   - Restart terminal

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install ffmpeg
```

### Step 4: Verify Installation

Run the game to test:
```bash
python main.py
```

If you see the game window, installation was successful!

## Common Issues and Solutions

### Issue: "Python is not recognized"

**Solution:**
- Make sure Python is installed
- Add Python to your system PATH
- On Windows: Check "Add Python to PATH" during installation
- Try using `python3` instead of `python` on Linux/Mac

### Issue: "pip is not recognized"

**Solution:**
- Use `python -m pip` instead of `pip`
- On Linux/Mac, try `pip3`
- Reinstall Python with "Add to PATH" option

### Issue: "ModuleNotFoundError: No module named 'pygame'"

**Solution:**
```bash
python -m pip install pygame
```

### Issue: "Failed to build 'pygame' when getting requirements to build wheel"

**This error occurs on Windows when pygame tries to build from source but can't find the required build tools.**

**Solution 1: Use pre-built wheel (Recommended)**
```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install --only-binary :all: pygame
```

**Solution 2: Install Microsoft Visual C++ Build Tools**
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++" workload
3. Restart your terminal
4. Try installing again: `python -m pip install pygame`

**Solution 3: Upgrade setuptools**
```bash
python -m pip install --upgrade setuptools wheel
python -m pip install pygame
```

**Solution 4: Use pre-compiled pygame**
If the above doesn't work, try installing a specific pre-built version:
```bash
python -m pip install pygame --pre
```

**Note:** The installation scripts now handle this automatically by trying pre-built wheels first.

### Issue: "MoviePy import error"

**Solution:**
```bash
python -m pip install --upgrade moviepy
```

Make sure you have MoviePy 2.0.0 or higher:
```bash
python -m pip install "moviepy>=2.0.0"
```

### Issue: "setuptools._distutils.msvccompiler" error (Windows)

**This is the same as the pygame build error above. Follow those solutions.**

### Issue: "FFmpeg not found"

**Solution:**
- Install FFmpeg (see Step 3 above)
- Add FFmpeg to your system PATH
- The game will still work without FFmpeg, but video playback may be limited

### Issue: "No audio playing"

**Solution:**
- Check system volume
- Make sure audio files exist in `assets/audio/` directory
- Install FFmpeg for better audio support
- Check browser/OS audio permissions

## Platform-Specific Notes

### Windows
- Use `python` command (not `python3`)
- May need to run terminal as Administrator for some installations
- Use `.bat` scripts for automated setup

### macOS
- May need to use `python3` instead of `python`
- Install Homebrew first for FFmpeg: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- May need to allow terminal to install packages

### Linux
- Use `python3` and `pip3` commands
- May need `sudo` for system-wide installations
- Different package managers for different distributions:
  - Ubuntu/Debian: `apt`
  - Fedora/RHEL: `dnf` or `yum`
  - Arch: `pacman`

## Verification Checklist

After installation, verify:

- [ ] Python 3.7+ is installed (`python --version`)
- [ ] pygame is installed (`python -c "import pygame; print(pygame.version.ver)"`)
- [ ] moviepy is installed (`python -c "import moviepy; print(moviepy.__version__)"`)
- [ ] numpy is installed (`python -c "import numpy; print(numpy.__version__)"`)
- [ ] Game runs without errors (`python main.py`)
- [ ] Assets folder exists (`assets/` directory)

## Getting Help

If you're still having issues:

1. Check the error message carefully
2. Make sure all prerequisites are installed
3. Try the troubleshooting steps above
4. Check that you're using the correct Python version
5. Verify all files from the repository are present

## Next Steps

Once installed, see the main [README.md](README.md) for:
- How to run the game
- Game controls
- Customization options
- Troubleshooting gameplay issues

