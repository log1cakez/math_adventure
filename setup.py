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
    
    # Upgrade pip first
    print("\n[1/4] Upgrading pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Required packages
    packages = [
        "pygame",
        "moviepy>=2.0.0",
        "numpy"
    ]
    
    print("\n[2/4] Installing dependencies...")
    for i, package in enumerate(packages, 2):
        print(f"\n[{i}/4] Installing {package}...")
        if install_package(package):
            print(f"✓ {package} installed successfully")
        else:
            print(f"✗ Failed to install {package}")
            print("Please install manually: pip install", package)
            sys.exit(1)
    
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

