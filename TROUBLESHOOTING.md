# Troubleshooting Guide

Quick solutions to common installation and runtime errors.

## 🚨 Critical Errors

### "Failed to build 'pygame' when getting requirements to build wheel"

**Error Message:**
```
ModuleNotFoundError: No module named 'setuptools._distutils.msvccompiler'
ERROR: Failed to build 'pygame' when getting requirements to build wheel
```

**What it means:**
Pygame is trying to build from source but can't find the required C++ compiler on Windows.

**Quick Fix (Try in order):**

1. **Use pre-built wheel (Fastest):**
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   python -m pip install --only-binary :all: pygame
   ```

2. **Upgrade setuptools:**
   ```bash
   python -m pip install --upgrade setuptools wheel
   python -m pip install pygame
   ```

3. **Install Visual C++ Build Tools:**
   - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Install "Desktop development with C++" workload
   - Restart terminal and try again

4. **Use pre-release version:**
   ```bash
   python -m pip install pygame --pre
   ```

## 📦 Installation Errors

### "Python is not recognized"

**Windows:**
- Reinstall Python and check "Add Python to PATH"
- Or manually add Python to PATH in System Properties

**Linux/Mac:**
- Use `python3` instead of `python`
- Install Python if missing: `sudo apt install python3` (Linux)

### "pip is not recognized"

**Solution:**
```bash
python -m pip install <package>
```

Or on Linux/Mac:
```bash
python3 -m pip install <package>
```

### "ModuleNotFoundError" for any package

**Solution:**
```bash
python -m pip install <package-name>
```

For example:
- `python -m pip install pygame`
- `python -m pip install numpy`
- `python -m pip install moviepy`

## 🎮 Runtime Errors

### "No module named 'pygame'" when running game

**Solution:**
```bash
python -m pip install pygame
```

### "MoviePy import error"

**Solution:**
```bash
python -m pip install --upgrade moviepy
python -m pip install "moviepy>=2.0.0"
```

### "FFmpeg not found"

**This is optional but recommended for video playback.**

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH
4. Restart terminal

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

### Game window doesn't open / Black screen

**Possible causes:**
1. Missing assets - Check that `assets/` folder exists
2. Missing images - Verify image files are in correct locations
3. Python version too old - Need Python 3.7+

**Solution:**
- Check console for error messages
- Verify all files from repository are present
- Try running: `python main.py` and read error output

### Audio not playing

**Possible causes:**
1. System volume muted
2. Audio files missing
3. FFmpeg not installed (for video audio)

**Solution:**
- Check system volume
- Verify audio files exist in `assets/audio/`
- Install FFmpeg (see above)

## 🔧 Platform-Specific Issues

### Windows

**Issue: "Access Denied" when installing packages**
- Run terminal as Administrator
- Or use: `python -m pip install --user <package>`

**Issue: Long path names causing errors**
- Enable long paths in Windows settings
- Or move project to shorter path (e.g., `C:\math_adventure`)

### macOS

**Issue: "Permission denied"**
- May need: `sudo pip3 install <package>`
- Or use: `pip3 install --user <package>`

**Issue: "Command not found: python"**
- Use `python3` instead of `python`
- Install Python from python.org or use Homebrew

### Linux

**Issue: "python3-dev not found"**
```bash
sudo apt-get install python3-dev
```

**Issue: "SDL2 not found" (for pygame)**
```bash
sudo apt-get install libsdl2-dev
```

**Issue: "pip3 not found"**
```bash
sudo apt-get install python3-pip
```

## 🆘 Still Having Issues?

1. **Check Python version:**
   ```bash
   python --version
   ```
   Should be 3.7 or higher

2. **Verify all files are present:**
   - `main.py` exists
   - `assets/` folder exists
   - `requirements.txt` exists

3. **Try clean installation:**
   ```bash
   python -m pip uninstall pygame moviepy numpy -y
   python -m pip install --upgrade pip setuptools wheel
   python -m pip install -r requirements.txt
   ```

4. **Check error messages:**
   - Read the full error message
   - Look for specific module names
   - Search error message online

5. **Use the setup scripts:**
   - Windows: `install_requirements.bat`
   - Linux/Mac: `./install_requirements.sh`
   - Or: `python setup.py`

## 📝 Getting Help

When asking for help, include:
- Your operating system (Windows/Mac/Linux)
- Python version (`python --version`)
- Full error message
- What you've already tried

