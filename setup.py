"""
Setup script for Math Adventure Game
This helps ensure all dependencies are installed correctly.
"""

import sys
import subprocess
import os

def check_python_version():
    """Check if Python version is 3.7 or higher"""
    if sys.version_info < (3, 7):
        print("ERROR: Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("=" * 50)
    print("Math Adventure Game - Setup")
    print("=" * 50)
    print()
    
    if not check_python_version():
        sys.exit(1)
    
    # Upgrade pip, setuptools, and wheel first
    print("\n[0/4] Upgrading pip, setuptools, and wheel...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
        print("✓ pip, setuptools, and wheel upgraded")
    except subprocess.CalledProcessError:
        print("⚠ Warning: Failed to upgrade pip/setuptools, continuing anyway...")
    
    # Required packages (order matters - numpy before moviepy)
    packages = [
        ("pygame", "pygame"),
        ("numpy", "numpy"),
        ("moviepy", "moviepy>=2.0.0")
    ]
    
    print("\n[1/4] Installing pygame...")
    # Try to use pre-built wheel first (Windows)
    if sys.platform == "win32":
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--only-binary", ":all:", "pygame"])
            print("✓ pygame installed (pre-built wheel)")
        except subprocess.CalledProcessError:
            print("Attempting to install pygame (may build from source)...")
            if install_package("pygame"):
                print("✓ pygame installed successfully")
            else:
                print("✗ Failed to install pygame")
                print("\nOn Windows, you may need Microsoft Visual C++ Build Tools:")
                print("Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
                print("Or try: python -m pip install --upgrade setuptools wheel")
                sys.exit(1)
    else:
        if install_package("pygame"):
            print("✓ pygame installed successfully")
        else:
            print("✗ Failed to install pygame")
            print("\nOn Linux, you may need system dependencies:")
            print("  Ubuntu/Debian: sudo apt-get install python3-dev libsdl2-dev")
            print("  Fedora: sudo dnf install python3-devel SDL2-devel")
            sys.exit(1)
    
    print("\n[2/4] Installing numpy...")
    if install_package("numpy"):
        print("✓ numpy installed successfully")
    else:
        print("✗ Failed to install numpy")
        sys.exit(1)
    
    print("\n[3/4] Installing moviepy...")
    if install_package("moviepy>=2.0.0"):
        print("✓ moviepy installed successfully")
    else:
        print("✗ Failed to install moviepy")
        sys.exit(1)
    
    print("\n[4/4] Verifying installation...")
    try:
        import pygame
        import numpy
        import moviepy
        print("✓ All packages verified successfully!")
    except ImportError as e:
        print(f"⚠ Warning: Verification failed - {e}")
        print("Packages may still work, but there may be an issue.")
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)
    print("\nYou can now run the game with:")
    print("  python main.py")
    print("\nNOTE: For video playback, you may also need FFmpeg:")
    print("  Windows: Download from https://ffmpeg.org/download.html")
    print("  macOS: brew install ffmpeg")
    print("  Linux: sudo apt install ffmpeg")
    print()

if __name__ == "__main__":
    main()

