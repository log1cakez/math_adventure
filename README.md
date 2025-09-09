# Math Adventure Game

An immersive Python game built with Pygame featuring interactive photo slideshows, video playback, and level selection with audio narration.

## 🎮 Features

- **Interactive Splash Screen**: Click anywhere to start or use gear icon for mechanics
- **Intro Sequence**: Multi-image introduction with synchronized audio
- **Video Playback**: Full MP4 video support with MoviePy integration
- **Level Selection**: Choose from 3 different levels after video
- **Photo Slideshow**: Navigate through photos with keyboard/mouse controls
- **Audio Support**: MP4 audio playback with automatic conversion
- **Fullscreen Mode**: Toggle between windowed and fullscreen
- **Mechanics Guide**: Interactive tutorial screens

## 🚀 Installation

1. **Install Python 3.7 or higher**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg (for audio conversion):**
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

## 🎯 How to Use

1. **Run the game:**
   ```bash
   python main.py
   ```

2. **Game Flow:**
   - **First Page** → Click anywhere → **Intro Sequence** → **Map Video** → **Level Selection** → **Slideshow**
   - **First Page** → **TAB** → **Map Video** → **Level Selection** → **Slideshow** (Quick Access)
   - **First Page** → Click gear → **Mechanics** → Back to First Page

3. **Add your content:**
   - Place `FIRST PAGE.jpg` in `assets/photos/`
   - Add intro images `5.png` and `6.png` in `assets/photos/intro/`
   - Add mechanics images `mechanics_1.png` and `mechanics_2.png` in `assets/photos/mechanics/`
   - Add map video `MAP 1 (VID).mp4` in `assets/photos/level_1/LEVEL 1.1/`
   - Add intro audio files in `assets/photos/intro/`
   - Add photos to level folders: `photos/level_1/`, `photos/level_2/`, `photos/level_3/`

## 🎮 Controls

### **Splash Screen:**
- **Click anywhere** → Start intro sequence
- **Click gear icon** → Show mechanics
- **TAB** → Direct to level selection
- **ESC** → Quit game
- **F11** → Toggle fullscreen

### **Intro Sequence:**
- **Any key or click** → Advance to next image
- **ESC** → Quit game
- **F11** → Toggle fullscreen

### **Map Video:**
- **1** → Select Level 1
- **2** → Select Level 2
- **3** → Select Level 3
- **Click** → Default to Level 1
- **ESC** → Quit game
- **F11** → Toggle fullscreen

### **Slideshow:**
- **Left/Right Arrow** → Navigate photos
- **Space** → Next photo
- **Backspace** → Previous photo
- **Click anywhere** → Back to splash
- **ESC** → Quit game
- **F11** → Toggle fullscreen

### **Mechanics:**
- **Left/Right Arrow** → Navigate pages (if multiple)
- **Click anywhere** → Back to splash
- **ESC** → Quit game
- **F11** → Toggle fullscreen

## 📁 File Structure

```
math_adventure/
├── main.py                          # Main game file
├── requirements.txt                 # Python dependencies
├── install_requirements.bat        # Windows installation script
├── README.md                       # This file
├── assets/
│   └── photos/
│       ├── FIRST PAGE.jpg          # Splash screen image
│       ├── intro/
│       │   ├── 5.png               # Intro image 1
│       │   ├── 6.png               # Intro image 2
│       │   ├── intro (1) .mp4      # Intro audio 1
│       │   └── intro (2) before showing the map.mp4  # Intro audio 2
│       ├── mechanics/
│       │   ├── mechanics_1.png     # Mechanics page 1
│       │   └── mechanics_2.png     # Mechanics page 2
│       └── level_1/
│           └── LEVEL 1.1/
│               ├── MAP 1 (VID).mp4 # Map video
│               └── MAP 1.png       # Map image (fallback)
└── photos/                         # Photo directories (created automatically)
    ├── level_1/                    # Photos for level 1
    ├── level_2/                    # Photos for level 2
    └── level_3/                    # Photos for level 3
```

## 🎵 Audio Support

- **MP4 Audio**: Automatic conversion to WAV for pygame compatibility
- **Synchronized Playback**: Audio plays with video frames
- **Fallback Support**: Works even without FFmpeg (audio-only mode)
- **Temporary Files**: Automatically cleaned up after use

## 🎬 Video Support

- **MoviePy Integration**: Full MP4 video playback
- **Aspect Ratio Preservation**: Videos scale to fit screen
- **Audio Synchronization**: Video and audio play together
- **Fallback Modes**: Image + audio or audio-only if video fails

## 📸 Supported Formats

### **Images:**
- JPG/JPEG
- PNG
- BMP
- GIF

### **Audio/Video:**
- MP4 (with audio)
- WAV (converted from MP4)

## ⚙️ Technical Requirements

- **Python 3.7+**
- **Pygame 2.0+**
- **MoviePy 2.0+** (for video playback)
- **FFmpeg** (for audio conversion)

## 🔧 Customization

You can easily modify the game by:
- **Adding more levels**: Edit the `load_levels()` method
- **Changing screen size**: Modify constants in `main.py`
- **Adding new content**: Place files in appropriate asset folders
- **Modifying controls**: Update input handlers
- **Changing colors/fonts**: Edit the drawing methods

## 🐛 Troubleshooting

### **Video not playing:**
- Install MoviePy: `pip install moviepy`
- Check if video file exists in correct path
- Verify video format is MP4

### **Audio not working:**
- Install FFmpeg and add to PATH
- Check if audio files exist in correct paths
- Verify MP4 files have audio tracks

### **Images not loading:**
- Check file paths in `assets/photos/` directory
- Verify image formats are supported
- Ensure files are not corrupted

## 🎉 Enjoy Your Adventure!

This game provides an immersive experience with smooth transitions, synchronized audio, and intuitive controls. Perfect for educational content, photo presentations, or interactive storytelling!