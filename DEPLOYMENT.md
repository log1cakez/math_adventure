# Windows Deployment Guide

This guide explains how to build a standalone Windows executable (.exe) that includes all sounds, images, and assets.

## Prerequisites

1. **Python 3.7 or higher** installed
2. **All dependencies installed:**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. **FFmpeg** (optional but recommended for video playback)
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Extract and add to PATH

## Building the Windows Executable

### Method 1: Using the Spec File (Recommended)

The project includes a pre-configured `math_adventure.spec` file that includes all assets.

1. **Build the executable:**
   ```bash
   pyinstaller math_adventure.spec
   ```

2. **Find your executable:**
   - The executable will be in the `dist/` folder
   - File name: `MathAdventure.exe`
   - This is a single-file executable with all assets bundled

3. **Test the executable:**
   - Run `dist/MathAdventure.exe`
   - All sounds, images, and videos should work

### Method 2: Quick Build Command

If you prefer a one-liner:

```bash
pyinstaller --onefile --windowed --add-data "assets;assets" --add-data "videos;videos" --hidden-import=pygame --hidden-import=moviepy --hidden-import=numpy --name=MathAdventure main.py
```

### Method 3: Custom Build

For more control, you can modify `math_adventure.spec`:

1. **Edit `math_adventure.spec`:**
   - Adjust `console=False` to `console=True` if you want to see debug output
   - Add an icon: `icon='path/to/icon.ico'`
   - Modify compression settings

2. **Build:**
   ```bash
   pyinstaller math_adventure.spec
   ```

## What Gets Included

The spec file automatically includes:
- ✅ All assets from `assets/` folder (images, audio, videos)
- ✅ All videos from `videos/` folder
- ✅ All Python dependencies (pygame, moviepy, numpy)
- ✅ All required DLLs and libraries

## File Structure After Build

```
dist/
└── MathAdventure.exe    # Single executable (all assets bundled inside)

build/                   # Temporary build files (can be deleted)
└── MathAdventure/
```

## Distribution

### Single File Distribution

The `MathAdventure.exe` is a standalone file. You can:
- Copy it to any Windows computer
- Run it without installing Python
- No additional files needed

### Optional: Create Installer

To create a professional installer:

1. **Use Inno Setup** (free):
   - Download from [jrsoftware.org](https://jrsoftware.org/isinfo.php)
   - Create installer script
   - Include `MathAdventure.exe` and optional FFmpeg

2. **Use NSIS** (free):
   - Download from [nsis.sourceforge.io](https://nsis.sourceforge.io/)
   - Create installer script

## Troubleshooting

### "Failed to execute script"

**Solution:**
- Build with `console=True` in spec file to see error messages
- Check that all assets are included
- Verify FFmpeg is available (if using videos)

### "Assets not found" error

**Solution:**
- Make sure `assets/` folder exists in project root
- Verify spec file includes `('assets', 'assets')`
- Rebuild: `pyinstaller --clean math_adventure.spec`

### Large file size

The executable will be large (50-200MB) because it includes:
- Python interpreter
- All dependencies
- All assets (images, audio, videos)

**To reduce size:**
- Compress videos before including
- Use UPX compression (already enabled in spec)
- Remove unused assets

### Video playback issues

**Solution:**
- Install FFmpeg on target system
- Or bundle FFmpeg with the executable
- Check that video files are in correct format (MP4 recommended)

### Antivirus false positives

Some antivirus software may flag PyInstaller executables.

**Solution:**
- Sign the executable with a code signing certificate
- Submit to antivirus vendors for whitelisting
- Use `--key` option with PyInstaller (requires PyCrypto)

## Advanced Options

### Add Application Icon

1. Create or download an `.ico` file
2. Edit `math_adventure.spec`:
   ```python
   icon='path/to/icon.ico',
   ```
3. Rebuild

### Include FFmpeg

To bundle FFmpeg with your executable:

1. Download FFmpeg Windows build
2. Add to spec file:
   ```python
   binaries=[
       ('path/to/ffmpeg.exe', '.'),
   ],
   ```
3. Modify code to use bundled FFmpeg path

### Debug Build

For debugging, build with console:

1. Edit `math_adventure.spec`:
   ```python
   console=True,  # Change from False
   ```
2. Rebuild
3. Run executable to see console output

### Version Information

Add Windows version info:

1. Create `version_info.txt`:
   ```
   VSVersionInfo(
     ffi=FixedFileInfo(
       filevers=(1, 0, 0, 0),
       prodvers=(1, 0, 0, 0),
       ...
     ),
     ...
   )
   ```
2. Add to spec file:
   ```python
   version='version_info.txt',
   ```

## Testing the Build

Before distributing:

1. ✅ Test on a clean Windows machine (without Python installed)
2. ✅ Verify all images load correctly
3. ✅ Test all audio playback
4. ✅ Test video playback (if applicable)
5. ✅ Test all game features
6. ✅ Check file size is reasonable
7. ✅ Test on Windows 10 and Windows 11

## Quick Reference

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller math_adventure.spec

# Clean build and rebuild
pyinstaller --clean math_adventure.spec

# Build with debug console
# (Edit spec file: console=True, then rebuild)

# Test executable
dist/MathAdventure.exe
```

## Notes

- The first run may be slower as PyInstaller extracts files to temp directory
- Antivirus may scan the executable on first run (this is normal)
- File size will be large due to bundled Python and assets
- All assets are embedded in the executable - no external files needed

