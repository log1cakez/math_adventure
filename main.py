import pygame
import os
import sys
import re
from typing import List, Dict, Optional

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("NumPy not available. Install with: pip install numpy")

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
try:
    import moviepy
    from moviepy import VideoFileClip
    MOVIEPY_AVAILABLE = True
    print("MoviePy loaded successfully")
except ImportError as e:
    MOVIEPY_AVAILABLE = False
    print(f"MoviePy import error: {e}")
    print("MoviePy not available. Install with: pip install moviepy")
except Exception as e:
    MOVIEPY_AVAILABLE = False
    print(f"MoviePy error: {e}")
    print("MoviePy not available. Install with: pip install moviepy")

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
BLUE = (0, 100, 200)
GREEN = (0, 200, 100)
RED = (200, 0, 0)

class PhotoSlideshowGame:
    def __init__(self):
        # Initialize in windowed mode with resizable window - optimized for laptops
        self.screen_width = 1600
        self.screen_height = 1000
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Math Adventure")
        self.clock = pygame.time.Clock()
        self.fullscreen = False
        
        # Set minimum window size for laptops
        self.min_width = 1024
        self.min_height = 768
        
        # Scale fonts based on screen size - optimized for laptops
        base_font_size = max(24, min(self.screen_width, self.screen_height) // 30)
        self.font_large = pygame.font.Font(None, int(base_font_size * 1.8))
        self.font_medium = pygame.font.Font(None, int(base_font_size * 1.2))
        self.font_small = pygame.font.Font(None, int(base_font_size))
        
        # Game state
        self.current_state = "splash"  # splash, second_page, select, exercise_level, map, slideshow, menu, mechanics
        self.current_level = 0
        self.current_photo_index = 0
        self.levels = self.load_levels()
        self.current_exercise_level = 0
        
        # Photo management
        self.current_photos = []
        self.photo_objects = []
        
        # Splash screen
        self.splash_video = self.load_splash_video()
        self.second_page_video = self.load_second_page_video()
        self.select_image = self.load_select_image()
        self.exercise_level_images = self.load_exercise_level_images()
        self.mechanics_images = self.load_mechanics_images()
        self.map_image = self.load_map_image()
        self.current_level_map_image = None  # Cache for level-specific map
        self.last_completed_main_level = 0  # Track which level map is currently displayed
        self.current_mechanics_index = 0
        
        # Audio placeholder
        self.audio_enabled = True
        self.current_audio = None
        
        # Level system
        self.current_level_number = 0
        self.current_question_index = 0
        self.level_questions = []
        self.correct_answers = 0
        self.total_questions = 0
        self.showing_reward = False
        self.reward_type = None  # 'correct', 'wrong', 'stars'
        self.reward_start_time = 0
        
        # Mission complete sequence tracking
        self.mission_complete_active = False
        self.mission_complete_type = None  # 'sublevel' or 'level'
        self.mission_complete_sequence_index = 0  # Current index in sequence
        self.mission_complete_level_number = None  # Main level number for level completion
        self.mission_complete_sublevel = None  # Current sublevel being completed (e.g., "1.1")
        
        # Progress tracking
        self.completed_levels = set()  # Track which sublevels have been completed (e.g., "1.1", "1.2")
        self.total_levels = 10  # Total number of main levels (1-10)
        self.sublevels_per_level = 3  # Each level has 3 sublevels
        
        # Sublevel selection
        self.selected_main_level = None  # Selected main level (1-10)
        
        # Track previous state before showing reward (for exercises)
        self.previous_state_before_reward = None
        
        # Text input for problem solving questions
        self.text_input_active = False
        self.text_input_value = ""
        self.text_input_cursor_blink = 0
        self.text_input_rect = pygame.Rect(0, 0, 400, 60)
        
        # Exercise text inputs (3 inputs)
        self.exercise_inputs = ["", "", ""]  # Three input fields
        self.exercise_active_input = 0  # 0, 1, or 2 for first, second, third input
        self.exercise_cursor_blink = 0
        
        # New game intro sequence
        self.intro_image = None
        self.intro_video_clip = None
        self.intro_video_playing = False
        self.intro_video_start_time = 0
        
        # Video clips for splash and second page
        self.splash_video_clip = None
        self.splash_video_playing = False
        self.splash_video_start_time = 0
        self.second_page_video_clip = None
        self.second_page_video_playing = False
        self.second_page_video_start_time = 0
        self.second_page_video_finished = False  # Track if video has finished
        self.second_page_last_frame = None  # Store last frame
        
        # Video/audio for level intros
        self.level_intro_video_clip = None
        self.level_intro_video_playing = False
        self.level_intro_video_start_time = 0
        self.level_intro_video_path = None
        self.level_intro_audio_paths = None  # List of audio paths (e.g. [pt1, pt2] for 5.1)
        self.level_intro_audio_index = 0
        self.level_intro_all_audio_finished = False
        self.level_intro_sublevel = None
        self.level_intro_music_end_event = pygame.USEREVENT + 3
        
        # Vocabulary screen shown before each sublevel starts
        self.sublevel_vocab_sublevel = None
        self.sublevel_vocab_image_path = None
        self.sublevel_vocab_image = None
        
        # Video clip for stars reward
        self.stars_video_clip = None
        self.stars_video_playing = False
        self.stars_video_start_time = 0
        
        # Video clip for correct/wrong reward (MP4, loops)
        self.reward_video_clip = None
        self.reward_video_start_time = 0
        
        # Interactive areas (you can adjust these coordinates based on your image)
        self.gear_area = None  # Will be set based on image dimensions
        
        # Start playing background music when app launches
        self.play_background_music()
        
    def load_levels(self) -> List[Dict]:
        """Load level information from directories - legacy function, no longer creates directories"""
        # This function is kept for backwards compatibility but no longer creates directories
        # The game now uses the structured level system in assets/photos/LEVEL X.Y/
        return []
    
    def load_splash_video(self) -> Optional[str]:
        """Load the splash screen video"""
        splash_path = resource_path("assets/photos/FIRST PAGE/OPENING.mp4")
        try:
            if os.path.exists(splash_path):
                return splash_path
            else:
                print(f"Splash video not found at {splash_path}")
                return None
        except Exception as e:
            print(f"Error loading splash video: {e}")
            return None
    
    def load_second_page_video(self) -> Optional[str]:
        """Load the second page video"""
        second_page_path = resource_path("assets/photos/FIRST PAGE/MAIN MENU.mp4")
        try:
            if os.path.exists(second_page_path):
                return second_page_path
            else:
                print(f"Second page video not found at {second_page_path}")
                return None
        except Exception as e:
            print(f"Error loading second page video: {e}")
            return None
    
    def load_select_image(self) -> Optional[pygame.Surface]:
        """Load the select image"""
        select_path = resource_path("assets/photos/EXERCISES/SELECT.png")
        try:
            if os.path.exists(select_path):
                select_image = pygame.image.load(select_path)
                # Scale select image to fit screen while maintaining aspect ratio
                select_image = self.scale_photo_to_fit(select_image)
                return select_image
            else:
                print(f"Select image not found at {select_path}")
                return None
        except pygame.error as e:
            print(f"Error loading select image: {e}")
            return None
    
    def load_exercise_level_images(self) -> List[pygame.Surface]:
        """Load the exercise level images"""
        exercise_level_images = []
        for i in range(1, 11):  # Levels 1-10
            level_path = resource_path(f"assets/photos/EXERCISES/EXERCISE ({i}).jpg")
            try:
                if os.path.exists(level_path):
                    level_image = pygame.image.load(level_path)
                    # Scale level image to fit screen while maintaining aspect ratio
                    level_image = self.scale_photo_to_fit(level_image)
                    exercise_level_images.append(level_image)
                    print(f"Loaded exercise level {i} image: {level_path}")
                else:
                    print(f"Exercise level {i} image not found at {level_path}")
                    exercise_level_images.append(None)
            except pygame.error as e:
                print(f"Error loading exercise level {i} image: {e}")
                exercise_level_images.append(None)
        
        return exercise_level_images
    
    def load_mechanics_images(self) -> List[pygame.Surface]:
        """Load the mechanics images"""
        mechanics_images = []
        mechanics_paths = [
            resource_path("assets/photos/mechanics/WELCOME.png"),
            resource_path("assets/photos/mechanics/MECHANICS PART 1.png"),
            resource_path("assets/photos/mechanics/MECHANICS PART 2.png"),
        ]
        
        for path in mechanics_paths:
            try:
                if os.path.exists(path):
                    mechanics = pygame.image.load(path)
                    # Scale mechanics image to fit screen while maintaining aspect ratio
                    mechanics = self.scale_photo_to_fit(mechanics)
                    mechanics_images.append(mechanics)
                    print(f"Loaded mechanics image: {path}")
                else:
                    print(f"Mechanics image not found at {path}")
            except pygame.error as e:
                print(f"Error loading mechanics image {path}: {e}")
        
        return mechanics_images
    
    def load_map_image(self) -> Optional[pygame.Surface]:
        """Load the map image - returns base map, level-specific maps loaded dynamically"""
        try:
            map_path = resource_path("assets/photos/MAP.png")
            
            if os.path.exists(map_path):
                image = pygame.image.load(map_path)
                return image
            else:
                print(f"ERROR: Map image not found at: {map_path}")
                return None
        except Exception as e:
            print(f"ERROR: Error loading map image: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_completed_main_level(self) -> int:
        """Get the highest completed main level (all 3 sublevels must be completed)"""
        max_completed = 0
        
        for level_num in range(1, self.total_levels + 1):
            # Check if all 3 sublevels are completed
            sublevels_completed = 0
            for sublevel_num in range(1, 4):
                sublevel_str = f"{level_num}.{sublevel_num}"
                if sublevel_str in self.completed_levels:
                    sublevels_completed += 1
            
            # If all 3 sublevels completed, this level is completed
            if sublevels_completed >= self.sublevels_per_level:
                max_completed = level_num
        
        return max_completed
    
    def is_level_completed(self, level_number: int) -> bool:
        """Check if all 3 sublevels of a main level are completed"""
        sublevels_completed = 0
        for sublevel_num in range(1, 4):
            sublevel_str = f"{level_number}.{sublevel_num}"
            if sublevel_str in self.completed_levels:
                sublevels_completed += 1
        return sublevels_completed >= self.sublevels_per_level
    
    def load_level_map_image(self, level_number: int) -> Optional[pygame.Surface]:
        """Load level-specific map image"""
        try:
            map_path = resource_path(f"assets/photos/MAP OVERALL/MAP LEVEL {level_number}.jpg")
            
            if os.path.exists(map_path):
                image = pygame.image.load(map_path)
                print(f"Loaded level map image: {map_path}")
                return image
            else:
                print(f"Level map image not found at: {map_path}")
                return None
        except Exception as e:
            print(f"Error loading level map image: {e}")
            return None
    
    def get_sublevel_folder(self, sublevel_string: str) -> Optional[str]:
        """Get the folder path for a sublevel (supports new LVL structure and legacy paths)"""
        try:
            parts = sublevel_string.split('.')
            main_level = parts[0]
        except Exception:
            return None
        
        candidates = [
            resource_path(f"assets/photos/LVL {main_level}/Level {sublevel_string}"),
            resource_path(f"assets/photos/LVL {main_level}/{sublevel_string}"),
            resource_path(f"assets/photos/LEVEL {sublevel_string}"),
        ]
        
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        
        return None
    
    def _get_first_item_from_folder(self, folder: str) -> Optional[str]:
        """Get the leading number from the first file in folder (sorted by numeric prefix), excluding intro mp4s."""
        if not folder or not os.path.exists(folder):
            return None
        files = [
            f for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f)) and not f.endswith("_intro.mp4")
        ]
        if not files:
            return None

        def sort_key(name):
            m = re.match(r"^(\d+)", name)
            return int(m.group(1)) if m else 0

        first = min(files, key=sort_key)
        m = re.match(r"^(\d+)", first)
        return m.group(1) if m else None

    def get_sublevel_intro_paths(self, sublevel_string: str):
        """Get intro video/audio paths for a sublevel. Returns (video_path, audio_paths) where audio_paths is a list."""
        sublevel_folder = self.get_sublevel_folder(sublevel_string)
        intro_video_path = None
        
        if sublevel_folder:
            candidate_video = os.path.join(sublevel_folder, f"{sublevel_string}_intro.mp4")
            if os.path.exists(candidate_video):
                intro_video_path = candidate_video
        
        # Level 5.1 has pt1 and pt2 - play in sequence
        if sublevel_string == "5.1":
            intro_audio_paths = []
            for suffix in ("_intro_pt1.mp3", "_intro_pt2.mp3"):
                p = resource_path(f"assets/audio/lvl_intro/{sublevel_string}{suffix}")
                if os.path.exists(p):
                    intro_audio_paths.append(p)
            if not intro_audio_paths:
                intro_audio_paths = None
        else:
            intro_audio_path = resource_path(f"assets/audio/lvl_intro/{sublevel_string}_intro.mp3")
            if not os.path.exists(intro_audio_path) and not intro_video_path and sublevel_folder:
                # No MP4 and no X.Y_intro.mp3: use first item in folder (e.g. 189.mp3)
                first_item = self._get_first_item_from_folder(sublevel_folder)
                if first_item:
                    fallback = resource_path(f"assets/audio/lvl_intro/{first_item}.mp3")
                    if os.path.exists(fallback):
                        intro_audio_path = fallback
            intro_audio_paths = [intro_audio_path] if os.path.exists(intro_audio_path) else None
        
        return intro_video_path, intro_audio_paths
    
    def get_sublevel_vocab_path(self, sublevel_string: str) -> Optional[str]:
        """Get vocabulary image path for a sublevel from assets/photos/Vocabulary words."""
        try:
            main_level = sublevel_string.split('.')[0]
        except Exception:
            return None
        
        vocab_folder = resource_path(f"assets/photos/Vocabulary words/level {main_level}")
        if not os.path.exists(vocab_folder):
            return None
        
        # Match filenames loosely (handles extra spaces like 'level 10. 2 .png')
        target = f"level{sublevel_string}".replace(" ", "")
        for name in os.listdir(vocab_folder):
            if not name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")):
                continue
            normalized = os.path.splitext(name.lower())[0].replace(" ", "")
            if normalized.startswith(target):
                return os.path.join(vocab_folder, name)
        
        return None
    
    def proceed_after_sublevel_complete(self):
        """Proceed to next sublevel after completing a sublevel"""
        if not self.mission_complete_sublevel:
            # Fallback to map if no sublevel info
            self.current_state = "map_image"
            self.play_background_music()
            return
        
        # Parse current sublevel (e.g., "1.1" -> main_level=1, sublevel=1)
        parts = self.mission_complete_sublevel.split('.')
        main_level = int(parts[0])
        sublevel = int(parts[1])
        
        # Check if there's a next sublevel (max 3 sublevels per level)
        if sublevel < 3:
            # Proceed to next sublevel
            next_sublevel = f"{main_level}.{sublevel + 1}"
            self.start_level(next_sublevel)
        else:
            # All sublevels done for this level - should have shown level complete sequence instead
            # Fallback to map
            self.current_state = "map_image"
            self.play_background_music()
    
    def show_level_map(self):
        """Show level-specific map after completing all sublevels of a level"""
        if not self.mission_complete_level_number:
            # Fallback to regular map
            self.current_state = "map_image"
            self.play_background_music()
            return
        
        # Load and display the level-specific map
        level_map_image = self.load_level_map_image(self.mission_complete_level_number)
        
        if level_map_image:
            # Store it as the current map to display
            self.current_level_map_image = level_map_image
            self.last_completed_main_level = self.mission_complete_level_number
        
        # Go to map state (will show level-specific map if loaded)
        self.current_state = "map_image"
        self.play_background_music()
    
    def load_intro_images(self) -> List[pygame.Surface]:
        """Load the intro images"""
        intro_images = []
        intro_paths = [
            resource_path("assets/photos/intro/5.png"),
            resource_path("assets/photos/intro/6.png")
        ]
        
        for path in intro_paths:
            try:
                if os.path.exists(path):
                    intro = pygame.image.load(path)
                    # Scale intro image to fit screen while maintaining aspect ratio
                    intro = self.scale_photo_to_fit(intro)
                    intro_images.append(intro)
                    print(f"Loaded intro image: {path}")
                else:
                    print(f"Intro image not found at {path}")
            except pygame.error as e:
                print(f"Error loading intro image {path}: {e}")
        
        return intro_images
    
    def load_intro_audio_files(self) -> List[str]:
        """Load the intro audio file paths"""
        intro_audio_files = []
        intro_audio_paths = [
            resource_path("assets/photos/intro/intro (1) .mp4"),
            resource_path("assets/photos/intro/intro (2) before showing the map.mp4")
        ]
        
        for path in intro_audio_paths:
            if os.path.exists(path):
                intro_audio_files.append(path)
                print(f"Found intro audio: {path}")
            else:
                print(f"Intro audio not found at {path}")
        
        return intro_audio_files
    
    def get_photos_from_directory(self, directory: str) -> List[str]:
        """Get all photo files from a directory"""
        photo_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        photos = []
        
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.lower().endswith(photo_extensions):
                    photos.append(os.path.join(directory, file))
                    
        return photos
    
    def load_photos_for_level(self, level_index: int):
        """Load photos for a specific level"""
        if 0 <= level_index < len(self.levels):
            self.current_photos = self.levels[level_index]["photos"]
            self.current_photo_index = 0
            self.photo_objects = []
            
            # Load and scale photos
            for photo_path in self.current_photos:
                try:
                    photo = pygame.image.load(photo_path)
                    # Scale photo to fit screen while maintaining aspect ratio
                    photo = self.scale_photo_to_fit(photo)
                    self.photo_objects.append(photo)
                except pygame.error as e:
                    print(f"Error loading photo {photo_path}: {e}")
                    # Create a placeholder if photo fails to load
                    placeholder = self.create_placeholder_photo()
                    self.photo_objects.append(placeholder)
            
            # Play level audio if available
            self.play_level_audio(level_index)
    
    def scale_photo_to_fit(self, photo: pygame.Surface) -> pygame.Surface:
        """Scale photo to fit screen while maintaining aspect ratio - optimized for laptops"""
        photo_width, photo_height = photo.get_size()
        # Larger margins for laptop screens to accommodate larger UI elements
        screen_width = self.screen_width - max(120, self.screen_width // 10)
        screen_height = self.screen_height - max(200, self.screen_height // 5)
        
        # Calculate scaling factor
        scale_x = screen_width / photo_width
        scale_y = screen_height / photo_height
        scale = min(scale_x, scale_y)
        
        new_width = int(photo_width * scale)
        new_height = int(photo_height * scale)
        
        return pygame.transform.scale(photo, (new_width, new_height))
    
    def create_placeholder_photo(self) -> pygame.Surface:
        """Create a placeholder photo when no photos are available"""
        placeholder_width = min(400, self.screen_width // 3)
        placeholder_height = min(300, self.screen_height // 3)
        placeholder = pygame.Surface((placeholder_width, placeholder_height))
        placeholder.fill(LIGHT_GRAY)
        
        # Add text to placeholder
        text = self.font_medium.render("No Photo Available", True, BLACK)
        text_rect = text.get_rect(center=(placeholder_width // 2, placeholder_height // 2))
        placeholder.blit(text, text_rect)
        
        return placeholder
    
    def draw_footer_instruction(self, instruction_text: str, content_rect: pygame.Rect = None):
        """Draw instruction text with a semi-transparent footer overlay over the slide/image/video"""
        # If content_rect is provided, position footer at bottom of content; otherwise use screen bottom
        if content_rect:
            # Position footer at bottom of the image/video content
            footer_height = 60
            footer_width = content_rect.width
            footer_x = content_rect.x
            footer_y = content_rect.y + content_rect.height - footer_height
            
            # Ensure footer doesn't go outside content bounds
            if footer_y < content_rect.y:
                footer_y = content_rect.y
                footer_height = content_rect.height
        else:
            # Fallback to screen bottom
            footer_height = 60
            footer_width = self.screen_width
            footer_x = 0
            footer_y = self.screen_height - footer_height
        
        # Create semi-transparent overlay
        footer_overlay = pygame.Surface((footer_width, footer_height), pygame.SRCALPHA)
        footer_overlay.fill((0, 0, 0, 180))  # Semi-transparent black background
        self.screen.blit(footer_overlay, (footer_x, footer_y))
        
        # Render and draw instruction text
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(footer_x + footer_width // 2, footer_y + footer_height // 2))
        self.screen.blit(instruction, instruction_rect)

    def draw_splash(self):
        """Draw the splash screen with video"""
        self.screen.fill(BLACK)
        
        # Initialize video if not already playing
        if not self.splash_video_playing and self.splash_video:
            self.start_splash_video()
        
        # Display current video frame
        if self.splash_video_clip and self.splash_video_playing:
            current_time = (pygame.time.get_ticks() - self.splash_video_start_time) / 1000.0
            try:
                # Loop video until user input
                if self.splash_video_clip.duration > 0:
                    current_time = current_time % self.splash_video_clip.duration
                frame = self.splash_video_clip.get_frame(current_time)
                # Convert numpy array to pygame surface
                if NUMPY_AVAILABLE:
                    # MoviePy gives (H,W,3), pygame needs (W,H,3)
                    frame = np.swapaxes(frame, 0, 1)
                    frame_surface = pygame.surfarray.make_surface(frame)
                else:
                    frame_surface = pygame.image.frombuffer(
                        frame.tobytes(),
                        (frame.shape[1], frame.shape[0]),
                        "RGB"
                    )
                
                # Scale to fit screen
                scaled_frame = self.scale_photo_to_fit(frame_surface)
                frame_rect = scaled_frame.get_rect(
                    center=(self.screen_width // 2, self.screen_height // 2)
                )
                self.screen.blit(scaled_frame, frame_rect)
                
                # Gear clickable area
                gear_x = frame_rect.x + frame_rect.width * 0.85
                gear_y = frame_rect.y + frame_rect.height * 0.1
                gear_size = 60
                self.gear_area = pygame.Rect(gear_x, gear_y, gear_size, gear_size)
                
                # Instructions
                instruction_text = "Click anywhere to continue, or click gear for mechanics..."
                self.draw_footer_instruction(instruction_text, frame_rect)
                return  # Avoid drawing twice
            except Exception as e:
                print(f"Error displaying splash video frame: {e}")
                # Fallback frame
                title = self.font_large.render("Math Adventure", True, WHITE)
                title_rect = title.get_rect(
                    center=(self.screen_width // 2, self.screen_height // 2 - 50)
                )
                self.screen.blit(title, title_rect)
        else:
            # Fallback if no video
            title = self.font_large.render("Math Adventure", True, WHITE)
            title_rect = title.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 - 50)
            )
            self.screen.blit(title, title_rect)
        
        # Instructions to proceed - moved to footer (fallback)
        instruction_text = "Click anywhere to continue, or click gear for mechanics..."
        self.draw_footer_instruction(instruction_text)
    
    def draw_second_page(self):
        """Draw the second page with video"""
        self.screen.fill(BLACK)
        
        # Initialize video if not already playing
        if not self.second_page_video_playing and self.second_page_video:
            self.start_second_page_video()
        
        # Track current content rect for instruction overlay
        current_content_rect = None
        
        # Display current video frame or last frame if finished
        if self.second_page_video_clip:
            if self.second_page_video_finished and self.second_page_last_frame:
                # Video has finished - display stored last frame
                scaled_frame = self.scale_photo_to_fit(self.second_page_last_frame)
                frame_rect = scaled_frame.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(scaled_frame, frame_rect)
                current_content_rect = frame_rect
                
                # Set up clickable top right area for mechanics
                self.top_right_area = pygame.Rect(frame_rect.x + frame_rect.width * 0.9, frame_rect.y, frame_rect.width * 0.1, frame_rect.height * 0.2)
            elif self.second_page_video_playing:
                # Video is still playing
                current_time = (pygame.time.get_ticks() - self.second_page_video_start_time) / 1000.0
                # Loop video until user input
                if self.second_page_video_clip.duration > 0:
                    current_time = current_time % self.second_page_video_clip.duration
                # Still playing - display current frame
                try:
                    frame = self.second_page_video_clip.get_frame(current_time)
                    # Convert numpy array to pygame surface
                    # MoviePy returns frames as (height, width, 3) RGB arrays
                    if NUMPY_AVAILABLE:
                        # Swap axes: (height, width, 3) -> (width, height, 3) for pygame
                        frame = np.swapaxes(frame, 0, 1)
                        frame_surface = pygame.surfarray.make_surface(frame)
                    else:
                        # Fallback: convert frame to pygame surface
                        frame_surface = pygame.image.frombuffer(frame.tobytes(), (frame.shape[1], frame.shape[0]), "RGB")
                    
                    # Scale to fit screen
                    scaled_frame = self.scale_photo_to_fit(frame_surface)
                    frame_rect = scaled_frame.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                    self.screen.blit(scaled_frame, frame_rect)
                    current_content_rect = frame_rect
                    
                    # Set up clickable top right area for mechanics (10% width, 20% height)
                    self.top_right_area = pygame.Rect(
                        frame_rect.x + frame_rect.width * 0.9,
                        frame_rect.y,
                        frame_rect.width * 0.1,
                        frame_rect.height * 0.2
                    )
                except Exception as e:
                    print(f"Error displaying second page video frame: {e}")
                    # Fallback
                    title = self.font_large.render("MAIN MENU", True, WHITE)
                    title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                    self.screen.blit(title, title_rect)
                    self.top_right_area = None
        else:
            # Fallback if video not available
            title = self.font_large.render("MAIN MENU", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(title, title_rect)
            self.top_right_area = None
        
        # Instructions for the three options - on the video/image
        instruction_text = "Press 1 for Map, 2 for New Game, 3 for Exercises, click top right for mechanics"
        self.draw_footer_instruction(instruction_text, current_content_rect)

    def draw_level_intro(self):
        """Draw the sublevel intro video (muted, looped). After audio ends, show play again prompt."""
        self.screen.fill(BLACK)
        
        if self.level_intro_video_clip and self.level_intro_video_playing:
            # Always loop video
            current_time = (pygame.time.get_ticks() - self.level_intro_video_start_time) / 1000.0
            try:
                if self.level_intro_video_clip.duration > 0:
                    current_time = current_time % self.level_intro_video_clip.duration
                frame = self.level_intro_video_clip.get_frame(current_time)
                if NUMPY_AVAILABLE:
                    frame = np.swapaxes(frame, 0, 1)
                    frame_surface = pygame.surfarray.make_surface(frame)
                else:
                    frame_surface = pygame.image.frombuffer(
                        frame.tobytes(),
                        (frame.shape[1], frame.shape[0]),
                        "RGB"
                    )
                
                scaled_frame = self.scale_photo_to_fit(frame_surface)
                frame_rect = scaled_frame.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(scaled_frame, frame_rect)
                
                # Show "Press SPACE to play again" when all audio parts have finished
                audio_finished = self.level_intro_audio_paths and self.level_intro_all_audio_finished
                if audio_finished:
                    play_text = self.font_medium.render("Press SPACE to play again", True, WHITE)
                    play_rect = play_text.get_rect(center=(self.screen_width // 2, self.screen_height - 80))
                    self.screen.blit(play_text, play_rect)
                
                instruction_text = "Press any key to skip intro"
                self.draw_footer_instruction(instruction_text, frame_rect)
                return
            except Exception as e:
                print(f"Error displaying level intro video frame: {e}")
        
        # Fallback if no video available
        title_text = f"Level {self.level_intro_sublevel} Intro"
        title = self.font_large.render(title_text, True, WHITE)
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 40))
        self.screen.blit(title, title_rect)
        instruction_text = "Press any key to continue"
        self.draw_footer_instruction(instruction_text)
    
    def draw_sublevel_vocab(self):
        """Draw vocabulary image before sublevel intro."""
        self.screen.fill(BLACK)
        content_rect = None
        
        if self.sublevel_vocab_image:
            scaled_image = self.scale_photo_to_fit(self.sublevel_vocab_image)
            image_rect = scaled_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(scaled_image, image_rect)
            content_rect = image_rect
        else:
            title = self.font_large.render(f"Level {self.sublevel_vocab_sublevel} Vocabulary", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(title, title_rect)
        
        instruction_text = "Press SPACE or click to continue"
        self.draw_footer_instruction(instruction_text, content_rect)
    
    def draw_select(self):
        """Draw the select screen"""
        self.screen.fill(BLACK)
        
        content_rect = None
        if self.select_image:
            # Display the select image centered
            select_rect = self.select_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(self.select_image, select_rect)
            content_rect = select_rect
            
            # Set up clickable top right area for mechanics (10% width, 20% height)
            self.top_right_area = pygame.Rect(select_rect.x + select_rect.width * 0.9, select_rect.y, select_rect.width * 0.1, select_rect.height * 0.2)
        else:
            # Fallback if select image not found
            title = self.font_large.render("SELECT", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(title, title_rect)
            self.top_right_area = None
        
        # Instructions for level selection - on the image
        instruction_text = "Press 1-10 to select a level, ESC to go back, click top right for mechanics"
        self.draw_footer_instruction(instruction_text, content_rect)
    
    def draw_exercise_level(self):
        """Draw the exercise level screen"""
        self.screen.fill(BLACK)
        
        # Display the current exercise level image
        content_rect = None
        if (self.current_exercise_level > 0 and 
            self.current_exercise_level <= len(self.exercise_level_images) and 
            self.exercise_level_images[self.current_exercise_level - 1]):
            
            level_image = self.exercise_level_images[self.current_exercise_level - 1]
            level_rect = level_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(level_image, level_rect)
            content_rect = level_rect
            
            # Set up clickable top right area for mechanics (10% width, 20% height)
            self.top_right_area = pygame.Rect(level_rect.x + level_rect.width * 0.9, level_rect.y, level_rect.width * 0.1, level_rect.height * 0.2)
        else:
            # Fallback if level image not found
            title = self.font_large.render(f"LEVEL {self.current_exercise_level}", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(title, title_rect)
            self.top_right_area = None
        
        # Draw exercise input boxes (pass content_rect to position relative to footer)
        self.draw_exercise_inputs(content_rect)
        
        # Instructions for navigation - on the image
        instruction_text = "Click inputs to type, TAB to switch, ENTER to submit, ESC to go back"
        self.draw_footer_instruction(instruction_text, content_rect)
    
    def get_exercise_input_position(self, content_rect: pygame.Rect = None):
        """Calculate the position for exercise input boxes based on footer location"""
        input_width = 300
        input_height = 50
        input_spacing = 20
        total_width = (input_width * 3) + (input_spacing * 2)
        footer_height = 60
        spacing_above_footer = 0  # No gap - inputs positioned directly above footer
        label_height = 30  # Space for labels above inputs
        
        # Determine where footer will be positioned
        if content_rect:
            # Footer is on the image - position inputs above the footer on the image
            footer_y = content_rect.y + content_rect.height - footer_height
            # Position inputs above the footer (accounting for labels and spacing)
            start_y = footer_y - spacing_above_footer - input_height - label_height
        else:
            # Footer is at screen bottom - position inputs above screen bottom
            start_y = self.screen_height - footer_height - spacing_above_footer - input_height - label_height
        
        # Starting position (centered horizontally)
        start_x = (self.screen_width - total_width) // 2
        return start_x, start_y, input_width, input_height, input_spacing
    
    def draw_exercise_inputs(self, content_rect: pygame.Rect = None):
        """Draw the 3 text input boxes for exercises"""
        # Get input position based on footer location
        start_x, start_y, input_width, input_height, input_spacing = self.get_exercise_input_position(content_rect)
        
        # Draw semi-transparent background overlay for inputs area
        overlay_padding = 45  # Padding above and below inputs for the overlay
        overlay_height = input_height + (overlay_padding * 2)  # Total overlay height
        overlay = pygame.Surface((self.screen_width, overlay_height))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, start_y - overlay_padding))
        
        # Draw labels
        label_y = start_y - 25
        for i in range(3):
            input_x = start_x + i * (input_width + input_spacing)
            label_text = f"Input {i + 1}:"
            if i == self.exercise_active_input:
                label_surface = self.font_small.render(label_text, True, GREEN)
            else:
                label_surface = self.font_small.render(label_text, True, WHITE)
            label_rect = label_surface.get_rect(center=(input_x + input_width // 2, label_y))
            self.screen.blit(label_surface, label_rect)
        
        # Update cursor blink
        self.exercise_cursor_blink += 1
        
        # Draw 3 input boxes
        for i in range(3):
            input_x = start_x + i * (input_width + input_spacing)
            input_rect = pygame.Rect(input_x, start_y, input_width, input_height)
            
            # Draw border (highlighted if active)
            if i == self.exercise_active_input:
                pygame.draw.rect(self.screen, GREEN, input_rect, 3)
            else:
                pygame.draw.rect(self.screen, WHITE, input_rect, 2)
            
            # Draw background
            pygame.draw.rect(self.screen, BLACK, input_rect)
            
            # Draw text value
            input_value = self.exercise_inputs[i]
            if input_value:
                text_surface = self.font_medium.render(input_value, True, WHITE)
                text_rect = text_surface.get_rect(center=(input_x + input_width // 2, start_y + input_height // 2))
                self.screen.blit(text_surface, text_rect)
            
            # Draw blinking cursor if this is the active input
            if i == self.exercise_active_input and (self.exercise_cursor_blink % 60 < 30):
                cursor_x = input_x + input_width // 2
                if input_value:
                    text_width = self.font_medium.size(input_value)[0]
                    cursor_x = input_x + input_width // 2 + text_width // 2 + 2
                cursor_y = start_y + 10
                cursor_height = input_height - 20
                pygame.draw.line(self.screen, WHITE, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)
    
    def draw_intro(self):
        """Draw the intro sequence"""
        self.screen.fill(BLACK)
        
        if self.intro_images and len(self.intro_images) > 0:
            # Display the current intro image centered
            current_intro = self.intro_images[self.current_intro_index]
            intro_rect = current_intro.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(current_intro, intro_rect)
            
            # Show progress indicator
            progress_text = f"Intro {self.current_intro_index + 1} of {len(self.intro_images)}"
            progress_surface = self.font_medium.render(progress_text, True, WHITE)
            progress_rect = progress_surface.get_rect(center=(self.screen_width // 2, 50))
            self.screen.blit(progress_surface, progress_rect)
            
            # Show navigation instructions
            if self.current_intro_index < len(self.intro_images) - 1:
                nav_text = "Press any key or click to continue..."
            else:
                nav_text = "Press any key or click to start slideshow..."
            
            nav_surface = self.font_medium.render(nav_text, True, WHITE)
            nav_rect = nav_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
            self.screen.blit(nav_surface, nav_rect)
        else:
            # Fallback if intro images not found
            title = self.font_large.render("Loading Level...", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(title, title_rect)
    
    def draw_map(self):
        """Draw the map screen - now redirects to map image"""
        self.draw_map_image()
    
    def draw_map_audio_only(self):
        """Draw map screen - now redirects to map image"""
        self.draw_map_image()
    
    def draw_map_image(self):
        """Draw the map image screen"""
        self.screen.fill(BLACK)
        
        # Determine which map to display based on completed levels
        completed_main_level = self.get_completed_main_level()
        
        # Load/cache level-specific map if completion status changed
        if completed_main_level > 0 and completed_main_level != self.last_completed_main_level:
            self.current_level_map_image = self.load_level_map_image(completed_main_level)
            self.last_completed_main_level = completed_main_level
        
        # Determine which map to display
        map_to_display = None
        if completed_main_level > 0 and self.current_level_map_image is not None:
            map_to_display = self.current_level_map_image
        else:
            # Fallback to base map
            map_to_display = self.map_image
            self.last_completed_main_level = 0  # Reset if using base map
        
        content_rect = None
        if map_to_display is not None:
            # Scale the map image to fit the screen while maintaining aspect ratio
            scaled_map = self.scale_photo_to_fit(map_to_display)
            map_rect = scaled_map.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(scaled_map, map_rect)
            content_rect = map_rect
            
            # Set up top right area for mechanics access
            self.top_right_area = pygame.Rect(map_rect.x + map_rect.width * 0.9, map_rect.y, map_rect.width * 0.1, map_rect.height * 0.2)
        else:
            # Fallback if map image not found
            title = self.font_large.render("Map Image Not Found", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(title, title_rect)
            self.top_right_area = None
        
        # Draw progress bar (on top of map)
        self.draw_progress_bar(content_rect)
        
        # Dynamic instructions based on progress and state - on the map image
        completed_count = len(self.completed_levels)
        total_sublevels = self.total_levels * self.sublevels_per_level
        if completed_count == 0:
            instruction_text = "Press 1-0 to select levels, ESC to go back, click top right for mechanics"
        elif completed_count < total_sublevels:
            instruction_text = f"Press 1-0 to select levels ({completed_count}/{total_sublevels} sublevels completed), ESC to go back, click top right for mechanics"
        else:
            instruction_text = "All sublevels completed! Press 1-0 to replay, ESC to go back, click top right for mechanics"
        
        self.draw_footer_instruction(instruction_text, content_rect)
    
    def draw_progress_bar(self, content_rect=None):
        """Draw a progress bar showing completed levels"""
        # Responsive progress bar dimensions
        bar_width = min(self.screen_width * 0.7, 800)  # Max 70% width, capped at 800px
        bar_height = max(15, self.screen_height // 50)  # Minimum 15px, scales with screen
        
        # Position relative to map if provided, otherwise use screen center
        if content_rect is not None:
            bar_x = content_rect.x + (content_rect.width - bar_width) // 2
            bar_y = content_rect.y + 60  # Position below top of map
        else:
            bar_x = (self.screen_width - bar_width) // 2
            bar_y = 40  # Fallback position at top area
        
        # Calculate progress (now based on sublevels)
        total_sublevels = self.total_levels * self.sublevels_per_level
        completed_count = len(self.completed_levels)
        progress = completed_count / total_sublevels if total_sublevels > 0 else 0
        
        # Draw progress text with dynamic content (above the bar)
        if completed_count == 0:
            progress_text = "Start your adventure! Complete sublevels to track progress"
        elif completed_count < total_sublevels:
            remaining = total_sublevels - completed_count
            progress_text = f"Progress: {completed_count}/{total_sublevels} sublevels completed ({remaining} remaining)"
        else:
            progress_text = f"🎉 Congratulations! All {total_sublevels} sublevels completed! 🎉"
        
        # Render text with subtle background for better readability (above the bar)
        text_surface = self.font_small.render(progress_text, True, WHITE)
        text_center_x = content_rect.centerx if content_rect is not None else self.screen_width // 2
        text_rect = text_surface.get_rect(center=(text_center_x, bar_y - 20))
        
        # Add subtle background behind text for better readability
        bg_padding = 5
        text_bg_rect = pygame.Rect(text_rect.x - bg_padding, text_rect.y - bg_padding, 
                                  text_rect.width + 2 * bg_padding, text_rect.height + 2 * bg_padding)
        text_bg_surface = pygame.Surface((text_bg_rect.width, text_bg_rect.height), pygame.SRCALPHA)
        text_bg_surface.fill((0, 0, 0, 100))  # Semi-transparent black background
        self.screen.blit(text_bg_surface, (text_bg_rect.x, text_bg_rect.y))
        self.screen.blit(text_surface, text_rect)
        
        # Draw semi-transparent background bar (dark gray with alpha)
        background_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        # Create a semi-transparent surface for the background
        bg_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        bg_surface.fill((50, 50, 50, 150))  # Dark gray with transparency
        self.screen.blit(bg_surface, (bar_x, bar_y))
        pygame.draw.rect(self.screen, WHITE, background_rect, 2)  # Border
        
        # Draw progress bar (green with transparency)
        if progress > 0:
            progress_width = int(bar_width * progress)
            progress_rect = pygame.Rect(bar_x, bar_y, progress_width, bar_height)
            # Create a semi-transparent surface for the progress
            progress_surface = pygame.Surface((progress_width, bar_height), pygame.SRCALPHA)
            progress_surface.fill((0, 200, 100, 180))  # Green with transparency
            self.screen.blit(progress_surface, (bar_x, bar_y))
    
    def draw_mechanics(self):
        """Draw the mechanics screen"""
        self.screen.fill(BLACK)
        
        content_rect = None
        if self.mechanics_images and len(self.mechanics_images) > 0:
            # Display the current mechanics image centered
            current_mechanics = self.mechanics_images[self.current_mechanics_index]
            mechanics_rect = current_mechanics.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(current_mechanics, mechanics_rect)
            content_rect = mechanics_rect
            
            # Show page counter if there are multiple images
            if len(self.mechanics_images) > 1:
                page_text = f"Page {self.current_mechanics_index + 1} of {len(self.mechanics_images)}"
                page_surface = self.font_medium.render(page_text, True, WHITE)
                page_rect = page_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
                self.screen.blit(page_surface, page_rect)
        
        # Instructions for navigation - on the mechanics image
        instruction_text = "Use LEFT/RIGHT arrows to navigate, ESC to go back"
        self.draw_footer_instruction(instruction_text, content_rect)
    
    def draw_menu(self):
        """Draw the menu screen"""
        self.screen.fill(BLACK)
        
        # Simple menu display
        title = self.font_large.render("Menu", True, WHITE)
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(title, title_rect)
    
    def draw_slideshow(self):
        """Draw the slideshow screen"""
        self.screen.fill(BLACK)
        
        if self.current_photos and len(self.current_photos) > 0:
            # Display current photo
            current_photo = self.current_photos[self.current_photo_index]
            photo_rect = current_photo.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(current_photo, photo_rect)
            
            # Show photo counter
            counter_text = f"Photo {self.current_photo_index + 1} of {len(self.current_photos)}"
            counter_surface = self.font_medium.render(counter_text, True, WHITE)
            counter_rect = counter_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
            self.screen.blit(counter_surface, counter_rect)
        else:
            # No photos available
            no_photos_text = "No photos available for this level"
            no_photos_surface = self.font_large.render(no_photos_text, True, WHITE)
            no_photos_rect = no_photos_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(no_photos_surface, no_photos_rect)
        
        # Instructions for navigation - moved to footer
        instruction_text = "Use LEFT/RIGHT arrows to navigate, ESC to go back"
        self.draw_footer_instruction(instruction_text)
    
    def handle_splash_input(self, event):
        """Handle input in splash state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                return False  # Quit game
            else:
                # Any other key goes to second page
                self.current_state = "second_page"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if clicked on gear area
                if self.gear_area and self.gear_area.collidepoint(mouse_pos):
                    self.current_state = "mechanics"
                elif self.top_right_area and self.top_right_area.collidepoint(mouse_pos):
                    self.current_state = "mechanics"
                else:
                    # Click anywhere else goes to second page
                    self.current_state = "second_page"
        return True
    
    def handle_second_page_input(self, event):
        """Handle input in second page state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                return False  # Quit game
            elif event.key == pygame.K_1:
                # Go to map image
                self.current_state = "map_image"
            elif event.key == pygame.K_2:
                # Start new game with intro sequence
                self.start_new_game()
            elif event.key == pygame.K_3:
                # Go to exercises (SELECT.png)
                self.current_state = "select"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                
                top_right_clicked = self.top_right_area and self.top_right_area.collidepoint(mouse_pos)
                if top_right_clicked:
                    self.current_state = "mechanics"
                else:
                    # Click anywhere else goes to map image
                    self.current_state = "map_image"
        return True
    
    def handle_select_input(self, event):
        """Handle input in select state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                # Go back to second page
                self.current_state = "second_page"
            elif event.key == pygame.K_1:
                self.current_exercise_level = 1
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_2:
                self.current_exercise_level = 2
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_3:
                self.current_exercise_level = 3
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_4:
                self.current_exercise_level = 4
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_5:
                self.current_exercise_level = 5
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_6:
                self.current_exercise_level = 6
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_7:
                self.current_exercise_level = 7
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_8:
                self.current_exercise_level = 8
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_9:
                self.current_exercise_level = 9
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_0:
                self.current_exercise_level = 10
                self.current_state = "exercise_level"
                self.play_background_music()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if clicked on top right area for mechanics
                if self.top_right_area and self.top_right_area.collidepoint(mouse_pos):
                    self.current_state = "mechanics"
                else:
                    # Click anywhere else goes back to second page
                    self.current_state = "second_page"
        return True
    
    def handle_exercise_level_input(self, event):
        """Handle input in exercise level state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                # Go back to select
                self.current_state = "select"
                # Reset inputs when leaving
                self.exercise_inputs = ["", "", ""]
                self.exercise_active_input = 0
            elif event.key == pygame.K_TAB:
                # Cycle through inputs with Tab key
                self.exercise_active_input = (self.exercise_active_input + 1) % 3
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Submit answers - check if all 3 inputs are filled
                if all(self.exercise_inputs):
                    self.check_exercise_answers()
                else:
                    # Show message that all inputs must be filled
                    print("Please fill all 3 inputs before submitting")
            elif event.key == pygame.K_BACKSPACE:
                # Delete character from active input
                if self.exercise_inputs[self.exercise_active_input]:
                    self.exercise_inputs[self.exercise_active_input] = self.exercise_inputs[self.exercise_active_input][:-1]
            else:
                # Handle text input for active input field
                # If no input is focused and user starts typing, focus first empty input
                if event.unicode:
                    char = event.unicode
                    # Allow digits, letters, and common math symbols
                    if char.isalnum() or char in '+-*/=. ':
                        # If current input is focused but user wants to type in empty one, auto-focus first empty
                        if not self.exercise_inputs[self.exercise_active_input] and any(not inp for inp in self.exercise_inputs):
                            # Focus first empty input
                            for i in range(3):
                                if not self.exercise_inputs[i]:
                                    self.exercise_active_input = i
                                    break
                        self.exercise_inputs[self.exercise_active_input] += char
                        # Auto-check once all three answers are filled
                        if all(inp.strip() for inp in self.exercise_inputs):
                            self.check_exercise_answers()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if clicked on top right area for mechanics
                if self.top_right_area and self.top_right_area.collidepoint(mouse_pos):
                    self.current_state = "mechanics"
                else:
                    # Check if clicked on any input box to select it
                    # Calculate content_rect same way as in draw_exercise_level
                    content_rect = None
                    if (self.current_exercise_level > 0 and 
                        self.current_exercise_level <= len(self.exercise_level_images) and 
                        self.exercise_level_images[self.current_exercise_level - 1]):
                        level_image = self.exercise_level_images[self.current_exercise_level - 1]
                        content_rect = level_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                    
                    # Get input position using same calculation as draw_exercise_inputs
                    start_x, start_y, input_width, input_height, input_spacing = self.get_exercise_input_position(content_rect)
                    
                    for i in range(3):
                        input_x = start_x + i * (input_width + input_spacing)
                        input_rect = pygame.Rect(input_x, start_y, input_width, input_height)
                        if input_rect.collidepoint(mouse_pos):
                            self.exercise_active_input = i
                            break
        return True
    
    def check_exercise_answers(self):
        """Check if all 3 exercise inputs are correct"""
        # Check that all inputs are non-empty
        all_filled = all(self.exercise_inputs)
        
        if not all_filled:
            self.previous_state_before_reward = "exercise_level"
            # Show wrong reward if not all filled
            self.show_reward('wrong')
            print("Not all inputs are filled")
            return
        
        # Define answer keys for each exercise level
        # Format: [first_number, second_number, result]
        exercise_answer_keys = {
            1: ['5', '3', '8'],
            2: ['20', '10', '30'],
            3: ['12', '5', '17'],
            4: ['32', '7', '39'],
            5: ['45', '4', '49'],
            6: ['51', '8', '59'],
            7: ['63', '5', '68'],
            8: ['72', '6', '78'],
            9: ['84', '5', '89'],
            10: ['50', '50', '100']
        }
        
        # Get expected answers for current exercise level
        if self.current_exercise_level not in exercise_answer_keys:
            self.previous_state_before_reward = "exercise_level"
            # Level not in answer keys - treat as correct if all filled
            self.show_reward('correct')
            print(f"Exercise level {self.current_exercise_level} not in answer keys, accepting any input")
            return
        
        expected_answers = exercise_answer_keys[self.current_exercise_level]
        
        # Check if all 3 inputs match expected answers (case-insensitive, strip whitespace)
        is_correct = True
        for i in range(3):
            user_input = self.exercise_inputs[i].strip()
            expected = expected_answers[i].strip()
            
            # Compare as strings (normalize to handle extra spaces)
            if user_input.lower() != expected.lower():
                is_correct = False
                break
        
        self.previous_state_before_reward = "exercise_level"
        # Show appropriate reward
        if is_correct:
            self.show_reward('correct')
            print(f"Exercise answers correct for level {self.current_exercise_level}: {self.exercise_inputs}")
        else:
            self.show_reward('wrong')
            print(f"Exercise answers wrong for level {self.current_exercise_level}. Expected: {expected_answers}, Got: {self.exercise_inputs}")
    
    def handle_intro_input(self, event):
        """Handle input in intro state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                return False  # Quit game
            elif event.key == pygame.K_SPACE:
                # Advance intro sequence
                self.advance_intro()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Advance intro sequence
                self.advance_intro()
        return True

    def handle_level_intro_input(self, event):
        """Handle input in level intro state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self.toggle_fullscreen()
            elif event.key == pygame.K_SPACE and self.level_intro_audio_paths and self.level_intro_all_audio_finished:
                # Replay audio from the beginning (pt1, then pt2 for 5.1)
                self.level_intro_all_audio_finished = False
                if self.audio_enabled:
                    self._play_level_intro_audio_part(0)
            else:
                self.finish_level_intro()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.finish_level_intro()
        return True
    
    def handle_sublevel_vocab_input(self, event):
        """Handle input on sublevel vocabulary screen."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                self.current_state = "map_image"
            else:
                self.start_level_intro(self.sublevel_vocab_sublevel)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.start_level_intro(self.sublevel_vocab_sublevel)
        return True
    
    def handle_map_input(self, event):
        """Handle input in map state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                return False  # Quit game
            elif event.key == pygame.K_1:
                # Select level 1
                self.current_level = 1
                self.load_photos_for_level(1)
                self.current_state = "slideshow"
            elif event.key == pygame.K_2:
                # Select level 2
                self.current_level = 2
                self.load_photos_for_level(2)
                self.current_state = "slideshow"
            elif event.key == pygame.K_3:
                # Select level 3
                self.current_level = 3
                self.load_photos_for_level(3)
                self.current_state = "slideshow"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Default to level 0
                self.current_level = 0
                self.load_photos_for_level(0)
                self.current_state = "slideshow"
        return True
    
    def handle_map_image_input(self, event):
        """Handle input in map image state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                # Go back to second page
                self.current_state = "second_page"
            elif event.key == pygame.K_1:
                # Select level 1, show sublevel selection
                self.selected_main_level = 1
                self.current_state = "sublevel_selection"
            elif event.key == pygame.K_2:
                # Select level 2, show sublevel selection
                self.selected_main_level = 2
                self.current_state = "sublevel_selection"
            elif event.key == pygame.K_3:
                # Select level 3, show sublevel selection
                self.selected_main_level = 3
                self.current_state = "sublevel_selection"
            elif event.key == pygame.K_4:
                # Select level 4, show sublevel selection
                self.selected_main_level = 4
                self.current_state = "sublevel_selection"
            elif event.key == pygame.K_5:
                # Select level 5, show sublevel selection
                self.selected_main_level = 5
                self.current_state = "sublevel_selection"
            elif event.key == pygame.K_6:
                # Select level 6, show sublevel selection
                self.selected_main_level = 6
                self.current_state = "sublevel_selection"
            elif event.key == pygame.K_7:
                # Select level 7, show sublevel selection
                self.selected_main_level = 7
                self.current_state = "sublevel_selection"
            elif event.key == pygame.K_8:
                # Select level 8, show sublevel selection
                self.selected_main_level = 8
                self.current_state = "sublevel_selection"
            elif event.key == pygame.K_9:
                # Select level 9, show sublevel selection
                self.selected_main_level = 9
                self.current_state = "sublevel_selection"
            elif event.key == pygame.K_0:
                # Select level 10, show sublevel selection
                self.selected_main_level = 10
                self.current_state = "sublevel_selection"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if clicked on top right area for mechanics
                if self.top_right_area and self.top_right_area.collidepoint(mouse_pos):
                    self.current_state = "mechanics"
                else:
                    # Click anywhere else to go back to second page
                    self.current_state = "second_page"
        return True
    
    def handle_mechanics_input(self, event):
        """Handle input in mechanics state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.current_state = "second_page"
            elif event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_LEFT and len(self.mechanics_images) > 1:
                # Previous mechanics image
                self.current_mechanics_index = (self.current_mechanics_index - 1) % len(self.mechanics_images)
            elif event.key == pygame.K_RIGHT and len(self.mechanics_images) > 1:
                # Next mechanics image
                self.current_mechanics_index = (self.current_mechanics_index + 1) % len(self.mechanics_images)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Click anywhere to go back
                self.current_state = "second_page"
        return True
    
    def handle_menu_input(self, event):
        """Handle input in menu state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False  # Quit game
            elif event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Click anywhere to go back
                self.current_state = "second_page"
        return True
    
    def handle_slideshow_input(self, event):
        """Handle input in slideshow state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                # Go back to second page
                self.current_state = "second_page"
            elif event.key == pygame.K_LEFT and len(self.current_photos) > 1:
                # Previous photo
                self.current_photo_index = (self.current_photo_index - 1) % len(self.current_photos)
            elif event.key == pygame.K_RIGHT and len(self.current_photos) > 1:
                # Next photo
                self.current_photo_index = (self.current_photo_index + 1) % len(self.current_photos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Click anywhere to go back
                self.current_state = "second_page"
        return True
    
    def start_game(self):
        """Start the game"""
        self.current_state = "second_page"
    
    def draw_mechanics(self):
        """Draw the mechanics screen"""
        self.screen.fill(BLACK)
        
        if self.mechanics_images and len(self.mechanics_images) > 0:
            # Display the current mechanics image centered
            current_mechanics = self.mechanics_images[self.current_mechanics_index]
            mechanics_rect = current_mechanics.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(current_mechanics, mechanics_rect)
            
            # Show page counter if there are multiple images
            if len(self.mechanics_images) > 1:
                page_text = f"Page {self.current_mechanics_index + 1} of {len(self.mechanics_images)}"
                page_surface = self.font_medium.render(page_text, True, WHITE)
                page_rect = page_surface.get_rect(center=(self.screen_width // 2, 50))
                self.screen.blit(page_surface, page_rect)
        else:
            # Fallback if mechanics images not found
            title = self.font_large.render("Game Mechanics", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
            self.screen.blit(title, title_rect)
            
            # Basic mechanics text
            mechanics_text = [
                "• Use arrow keys to navigate photos",
                "• Press 1-5 to select levels",
                "• ESC to go back to menu",
                "• Click gear icon for mechanics"
            ]
            
            y_offset = self.screen_height // 2
            for text in mechanics_text:
                text_surface = self.font_medium.render(text, True, WHITE)
                text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_offset))
                self.screen.blit(text_surface, text_rect)
                y_offset += 40
        
        # Navigation instructions
        if len(self.mechanics_images) > 1:
            nav_text = "LEFT/RIGHT: Navigate pages | ESC: Back to splash | Click anywhere: Back"
        else:
            nav_text = "ESC: Back to splash | Click anywhere: Back"
        
        nav_surface = self.font_medium.render(nav_text, True, WHITE)
        nav_rect = nav_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
        self.screen.blit(nav_surface, nav_rect)
    
    def draw_menu(self):
        """Draw the main menu"""
        self.screen.fill(BLACK)
        
        # Title
        title = self.font_large.render("Math Adventure", True, WHITE)
        title_rect = title.get_rect(center=(self.screen_width // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "Press any key or click to start the game",
            "ESC to quit | F11 to toggle fullscreen"
        ]
        
        y_offset = 250
        for instruction in instructions:
            text = self.font_medium.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(self.screen_width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 50
    
    def draw_slideshow(self):
        """Draw the slideshow view"""
        self.screen.fill(BLACK)
        
        if not self.photo_objects:
            # No photos available
            text = self.font_large.render("No photos available for this level!", True, WHITE)
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(text, text_rect)
            
            # Instructions
            back_text = self.font_medium.render("Press ESC to go back to menu", True, WHITE)
            back_rect = back_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
            self.screen.blit(back_text, back_rect)
        else:
            # Display current photo
            current_photo = self.photo_objects[self.current_photo_index]
            photo_rect = current_photo.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(current_photo, photo_rect)
            
            # Photo counter
            counter_text = f"Photo {self.current_photo_index + 1} of {len(self.photo_objects)}"
            counter_surface = self.font_medium.render(counter_text, True, WHITE)
            counter_rect = counter_surface.get_rect(center=(self.screen_width // 2, 50))
            self.screen.blit(counter_surface, counter_rect)
            
            # Level name
            level_name = f"Level {self.current_level + 1} - Photo Slideshow"
            level_surface = self.font_medium.render(level_name, True, WHITE)
            level_rect = level_surface.get_rect(center=(self.screen_width // 2, 90))
            self.screen.blit(level_surface, level_rect)
        
        # Controls
        controls = [
            "LEFT/RIGHT: Navigate photos",
            "ESC: Quit game",
            "SPACE: Next photo",
            "BACKSPACE: Previous photo",
            "Click anywhere: Back to splash"
        ]
        
        y_offset = self.screen_height - 120
        for control in controls:
            text = self.font_small.render(control, True, WHITE)
            text_rect = text.get_rect(center=(self.screen_width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 25
    
    def handle_splash_input(self, event):
        """Handle input in splash state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                return False  # Quit game
            else:
                # Any other key press goes to second page
                self.current_state = "second_page"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if click is on gear area or in top-right corner
                gear_clicked = self.gear_area and self.gear_area.collidepoint(mouse_pos)
                top_right_clicked = False
                
                # Also check if clicked in the top-right area of the video
                # Use a default area if video is playing
                if self.splash_video_playing:
                    # Estimate clickable area based on screen size
                    top_right_area = pygame.Rect(self.screen_width * 0.85, 0, self.screen_width * 0.15, self.screen_height * 0.2)
                    top_right_clicked = top_right_area.collidepoint(mouse_pos)
                else:
                    top_right_clicked = False
                
                if gear_clicked or top_right_clicked:
                    self.current_state = "mechanics"
                else:
                    # Click anywhere else goes to second page
                    self.current_state = "second_page"
        return True
    
    def handle_second_page_input(self, event):
        """Handle input in second page state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                return False  # Quit game
            elif event.key == pygame.K_1:
                # Go to map image
                self.current_state = "map_image"
            elif event.key == pygame.K_2:
                # Start new game with intro sequence
                self.start_new_game()
            elif event.key == pygame.K_3:
                # Go to exercises (SELECT.png)
                self.current_state = "select"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                
                top_right_clicked = self.top_right_area and self.top_right_area.collidepoint(mouse_pos)
                if top_right_clicked:
                    self.current_state = "mechanics"
                else:
                    # Click anywhere else goes to map image
                    self.current_state = "map_image"
        return True
    
    def handle_select_input(self, event):
        """Handle input in select state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                # Go back to second page
                self.current_state = "second_page"
            elif event.key == pygame.K_1:
                self.current_exercise_level = 1
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_2:
                self.current_exercise_level = 2
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_3:
                self.current_exercise_level = 3
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_4:
                self.current_exercise_level = 4
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_5:
                self.current_exercise_level = 5
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_6:
                self.current_exercise_level = 6
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_7:
                self.current_exercise_level = 7
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_8:
                self.current_exercise_level = 8
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_9:
                self.current_exercise_level = 9
                self.current_state = "exercise_level"
                self.play_background_music()
            elif event.key == pygame.K_0:
                self.current_exercise_level = 10
                self.current_state = "exercise_level"
                self.play_background_music()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                
                top_right_clicked = self.top_right_area and self.top_right_area.collidepoint(mouse_pos)
                if top_right_clicked:
                    self.current_state = "mechanics"
                else:
                    # Click anywhere else goes back to second page
                    self.current_state = "second_page"
        return True
    
    def handle_intro_input(self, event):
        """Handle input in intro state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                return False  # Quit game
            else:
                # Any other key advances to next image or slideshow
                self.advance_intro()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button - click to advance
                self.advance_intro()
        return True
    
    def handle_map_input(self, event):
        """Handle input in map state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                return False  # Quit game
            elif event.key == pygame.K_1:
                # Level 1 selected
                self.cleanup_map_video()
                self.current_level = 0
                self.load_photos_for_level(0)
                self.current_state = "slideshow"
            elif event.key == pygame.K_2:
                # Level 2 selected
                self.cleanup_map_video()
                self.current_level = 1
                self.load_photos_for_level(1)
                self.current_state = "slideshow"
            elif event.key == pygame.K_3:
                # Level 3 selected
                self.cleanup_map_video()
                self.current_level = 2
                self.load_photos_for_level(2)
                self.current_state = "slideshow"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button - click to continue (default to level 1)
                self.cleanup_map_video()
                self.current_level = 0
                self.load_photos_for_level(0)
                self.current_state = "slideshow"
        return True
    
    def handle_mechanics_input(self, event):
        """Handle input in mechanics state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.current_state = "second_page"
            elif event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_LEFT and len(self.mechanics_images) > 1:
                # Navigate to previous mechanics image
                self.current_mechanics_index = (self.current_mechanics_index - 1) % len(self.mechanics_images)
            elif event.key == pygame.K_RIGHT and len(self.mechanics_images) > 1:
                # Navigate to next mechanics image
                self.current_mechanics_index = (self.current_mechanics_index + 1) % len(self.mechanics_images)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button - click anywhere to go back to splash
                self.current_state = "splash"
        return True
    
    def handle_menu_input(self, event):
        """Handle input in menu state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False  # Quit game
            elif event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            else:
                # Any other key starts the game
                self.start_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button - click to start
                self.start_game()
        return True
    
    def handle_slideshow_input(self, event):
        """Handle input in slideshow state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False  # Quit game
            elif event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_LEFT or event.key == pygame.K_BACKSPACE:
                if self.photo_objects:
                    self.current_photo_index = (self.current_photo_index - 1) % len(self.photo_objects)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE:
                if self.photo_objects:
                    self.current_photo_index = (self.current_photo_index + 1) % len(self.photo_objects)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button - click anywhere to go back to splash
                self.current_state = "splash"
        return True
    
    def start_game(self):
        """Start the game - go to second page"""
        self.current_state = "second_page"
    
    def start_intro_sequence(self):
        """Start the intro sequence"""
        self.current_intro_index = 0
        self.current_state = "intro"
        
        # Play first intro audio if available
        self.play_intro_audio_for_index(0)
    
    def advance_intro(self):
        """Advance to next intro image or go to map"""
        self.current_intro_index += 1
        
        # If we've shown all intro images, go to map
        if self.current_intro_index >= len(self.intro_images):
            self.start_map_video()
        else:
            # Play audio for the next image if available
            self.play_intro_audio_for_index(self.current_intro_index)
    
    def play_intro_audio(self):
        """Play intro audio (placeholder)"""
        if self.audio_enabled:
            print("Playing intro audio...")
            # Placeholder for audio functionality
            # In a real implementation, you would load and play audio here
            # pygame.mixer.music.load("assets/audio/intro.mp3")
            # pygame.mixer.music.play()
    
    def play_intro_audio_for_index(self, index: int):
        """Play intro audio for specific image index"""
        if self.audio_enabled and index < len(self.intro_audio_files):
            audio_path = self.intro_audio_files[index]
            print(f"Playing intro audio {index + 1}: {audio_path}")
            
            try:
                # Convert MP4 to WAV for pygame compatibility
                wav_path = self.convert_mp4_to_wav(audio_path)
                if wav_path and os.path.exists(wav_path):
                    pygame.mixer.music.load(wav_path)
                    pygame.mixer.music.play()
                    print(f"Playing converted audio: {wav_path}")
                else:
                    print(f"Could not convert or find audio file: {audio_path}")
                
            except pygame.error as e:
                print(f"Error playing audio {audio_path}: {e}")
    
    def convert_mp4_to_wav(self, mp4_path: str) -> str:
        """Convert MP4 to WAV for pygame compatibility"""
        try:
            # Create WAV filename
            wav_path = mp4_path.replace('.mp4', '.wav')
            
            # Check if WAV already exists
            if os.path.exists(wav_path):
                return wav_path
            
            # Try to convert using ffmpeg (if available)
            import subprocess
            cmd = [
                'ffmpeg', '-i', mp4_path, '-vn', '-acodec', 'pcm_s16le', 
                '-ar', '44100', '-ac', '2', wav_path, '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and os.path.exists(wav_path):
                print(f"Converted {mp4_path} to {wav_path}")
                return wav_path
            else:
                print(f"FFmpeg conversion failed: {result.stderr}")
                return None
                
        except FileNotFoundError:
            print("FFmpeg not found. Please install FFmpeg to convert MP4 audio.")
            return None
        except Exception as e:
            print(f"Error converting MP4 to WAV: {e}")
            return None
    
    def start_map_video(self):
        """Start the map video"""
        self.current_state = "map"
        self.map_video_playing = True
        self.map_video_start_time = pygame.time.get_ticks()
        
        # Load video with MoviePy if available
        if MOVIEPY_AVAILABLE and os.path.exists(self.map_video_path):
            try:
                self.map_video_clip = VideoFileClip(self.map_video_path)
                print(f"Loaded video: {self.map_video_path}")
                
                # Play the video with its audio using MoviePy
                if self.map_video_clip.audio is not None:
                    # Create a temporary audio file and play it
                    temp_audio_path = "temp_map_audio.wav"
                    # MoviePy 2.x no longer supports the 'verbose' argument on write_audiofile
                    # Use default logging behavior instead
                    self.map_video_clip.audio.write_audiofile(temp_audio_path, logger=None)
                    
                    # Play the audio with pygame
                    pygame.mixer.music.load(temp_audio_path)
                    pygame.mixer.music.play()
                    print("Playing video with audio")
                else:
                    print("No audio track in video")
            except Exception as e:
                print(f"Error loading video: {e}")
                self.map_video_clip = None
        else:
            self.map_video_clip = None
            if not MOVIEPY_AVAILABLE:
                print("MoviePy not available. Install with: pip install moviepy")
        
        # Fallback: try pygame audio if MoviePy failed
        if self.map_video_clip is None:
            self.play_map_video()
    
    def play_map_video(self):
        """Play the map video audio"""
        if self.audio_enabled and os.path.exists(self.map_video_path):
            try:
                # Play MP4 audio directly
                pygame.mixer.music.load(self.map_video_path)
                pygame.mixer.music.play()
            except pygame.error as e:
                print(f"Error playing map video audio: {e}")
    
    def start_splash_video(self):
        """Start the splash video"""
        if not self.splash_video:
            return
        
        self.splash_video_playing = True
        self.splash_video_start_time = pygame.time.get_ticks()
        
        # Load video with MoviePy if available
        if MOVIEPY_AVAILABLE and os.path.exists(self.splash_video):
            try:
                self.splash_video_clip = VideoFileClip(self.splash_video)
                print(f"Loaded splash video: {self.splash_video}")
                
                # Play audio if available
                if self.splash_video_clip.audio is not None:
                    temp_audio_path = "temp_splash_audio.wav"
                    # MoviePy 2.x no longer supports the 'verbose' argument on write_audiofile
                    self.splash_video_clip.audio.write_audiofile(temp_audio_path, logger=None)
                    pygame.mixer.music.load(temp_audio_path)
                    pygame.mixer.music.play()
                    print("Playing splash video with audio")
            except Exception as e:
                print(f"Error loading splash video: {e}")
                self.splash_video_clip = None
        else:
            self.splash_video_clip = None
    
    def start_second_page_video(self):
        """Start the second page video"""
        if not self.second_page_video:
            return
        
        self.second_page_video_playing = True
        self.second_page_video_finished = False  # Reset finished flag
        self.second_page_last_frame = None  # Clear last frame
        self.second_page_video_start_time = pygame.time.get_ticks()
        
        # Stop any current music and start background music instead
        pygame.mixer.music.stop()
        self.play_background_music()
        
        # Load video with MoviePy if available
        if MOVIEPY_AVAILABLE and os.path.exists(self.second_page_video):
            try:
                self.second_page_video_clip = VideoFileClip(self.second_page_video)
                print(f"Loaded second page video: {self.second_page_video}")
                # Video audio is muted - background music plays instead
                print("Second page video audio muted, playing background music instead")
            except Exception as e:
                print(f"Error loading second page video: {e}")
                self.second_page_video_clip = None
        else:
            self.second_page_video_clip = None
    
    def start_stars_video(self):
        """Start the stars reward video"""
        stars_video_path = resource_path("videos/REWARD/REWARD STARS.mp4")
        
        self.stars_video_playing = True
        self.stars_video_start_time = pygame.time.get_ticks()
        
        # Load video with MoviePy if available
        if MOVIEPY_AVAILABLE and os.path.exists(stars_video_path):
            try:
                self.stars_video_clip = VideoFileClip(stars_video_path)
                print(f"Loaded stars video: {stars_video_path}")
                
                # Play audio if available
                if self.stars_video_clip.audio is not None:
                    temp_audio_path = "temp_stars_audio.wav"
                    self.stars_video_clip.audio.write_audiofile(temp_audio_path, logger=None)
                    pygame.mixer.music.load(temp_audio_path)
                    pygame.mixer.music.play()
                    print("Playing stars video with audio")
            except Exception as e:
                print(f"Error loading stars video: {e}")
                self.stars_video_clip = None
        else:
            self.stars_video_clip = None
    
    def play_level_audio(self, level_index: int):
        """Play level audio (placeholder)"""
        if self.audio_enabled:
            print(f"Playing level {level_index + 1} audio...")
            # Placeholder for audio functionality
            # In a real implementation, you would load and play audio here
            # audio_path = f"assets/audio/level_{level_index + 1}.mp3"
            # pygame.mixer.music.load(audio_path)
            # pygame.mixer.music.play()
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode - optimized for laptops"""
        if self.fullscreen:
            # Currently fullscreen, switch to windowed with laptop-optimized size
            self.screen = pygame.display.set_mode((1600, 1000), pygame.RESIZABLE)
            self.fullscreen = False
        else:
            # Currently windowed, switch to fullscreen
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.fullscreen = True
        
        # Update screen dimensions
        self.screen_width, self.screen_height = self.screen.get_size()
        
        # Recalculate font sizes - optimized for laptops
        base_font_size = max(24, min(self.screen_width, self.screen_height) // 30)
        self.font_large = pygame.font.Font(None, int(base_font_size * 1.8))
        self.font_medium = pygame.font.Font(None, int(base_font_size * 1.2))
        self.font_small = pygame.font.Font(None, int(base_font_size))
        
    
    def start_level(self, sublevel_string):
        """Start a specific sublevel (format: "1.1", "1.2", "1.3", etc.)"""
        self.current_level_number = sublevel_string
        self.start_sublevel_vocab(sublevel_string)
    
    def start_sublevel_vocab(self, sublevel_string: str):
        """Show vocabulary image for sublevel before intro."""
        self.sublevel_vocab_sublevel = sublevel_string
        self.sublevel_vocab_image_path = self.get_sublevel_vocab_path(sublevel_string)
        self.sublevel_vocab_image = None
        
        if not self.sublevel_vocab_image_path:
            # No vocab image for this sublevel; continue existing flow
            self.start_level_intro(sublevel_string)
            return
        
        try:
            self.sublevel_vocab_image = pygame.image.load(self.sublevel_vocab_image_path)
            self.current_state = "sublevel_vocab"
            print(f"Loaded vocabulary image: {self.sublevel_vocab_image_path}")
        except Exception as e:
            print(f"Error loading vocabulary image: {e}")
            self.sublevel_vocab_image = None
            self.start_level_intro(sublevel_string)
    
    def _play_level_intro_audio_part(self, index: int):
        """Play a single part of level intro audio by index."""
        if not self.level_intro_audio_paths or index >= len(self.level_intro_audio_paths):
            return
        path = self.level_intro_audio_paths[index]
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_endevent(self.level_intro_music_end_event)
            pygame.mixer.music.play()
            self.level_intro_audio_index = index
            print(f"Playing level intro audio: {path}")
        except Exception as e:
            print(f"Error playing level intro audio: {e}")
    
    def start_level_intro(self, sublevel_string: str):
        """Start the intro video/audio for a sublevel (video muted, MP3 plays). Skip entirely if no intro MP4."""
        self.level_intro_sublevel = sublevel_string
        self.level_intro_video_path, self.level_intro_audio_paths = self.get_sublevel_intro_paths(sublevel_string)
        
        # If no intro MP4, skip intro and go straight to questions
        if not self.level_intro_video_path:
            self.start_level_questions(sublevel_string)
            return
        
        self.level_intro_audio_index = 0
        self.level_intro_all_audio_finished = False
        
        # Reset any previous intro state
        self.level_intro_video_clip = None
        self.level_intro_video_playing = False
        self.level_intro_video_start_time = 0
        
        # Load intro video (muted)
        if self.level_intro_video_path and MOVIEPY_AVAILABLE:
            try:
                self.level_intro_video_clip = VideoFileClip(self.level_intro_video_path)
                self.level_intro_video_playing = True
                self.level_intro_video_start_time = pygame.time.get_ticks()
                print(f"Loaded level intro video: {self.level_intro_video_path}")
            except Exception as e:
                print(f"Error loading level intro video: {e}")
                self.level_intro_video_clip = None
        elif self.level_intro_video_path and not MOVIEPY_AVAILABLE:
            print("MoviePy not available. Install with: pip install moviepy")
        
        # Play intro audio (first part, or single file)
        if self.audio_enabled and self.level_intro_audio_paths:
            self._play_level_intro_audio_part(0)
        elif self.level_intro_audio_paths:
            print(f"Level intro audio not found: {self.level_intro_audio_paths}")
        
        self.current_state = "level_intro"
    
    def finish_level_intro(self):
        """Finish the level intro and proceed to questions"""
        # Cleanup video clip
        if self.level_intro_video_clip:
            try:
                self.level_intro_video_clip.close()
            except Exception:
                pass
        self.level_intro_video_clip = None
        self.level_intro_video_playing = False
        self.level_intro_video_start_time = 0
        pygame.mixer.music.set_endevent()  # Clear level intro end event
        
        # Stop intro audio before starting questions
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        
        self.start_level_questions(self.level_intro_sublevel)
    
    def start_level_questions(self, sublevel_string: str):
        """Load questions and start the level question flow"""
        self.current_question_index = 0
        self.correct_answers = 0
        self.showing_reward = False
        
        # Load level questions
        self.load_level_questions(sublevel_string)
        
        if self.level_questions:
            self.total_questions = len(self.level_questions)
            self.current_state = "level_question"
            # Play audio for first question if available
            self.play_question_audio()
        else:
            print(f"No questions found for sublevel {sublevel_string}")
    
    def load_level_questions(self, sublevel_string):
        """Load questions for a specific sublevel (format: "1.1", "1.2", "1.3", etc.)"""
        self.level_questions = []
        
        # Resolve folder for level questions (supports new LVL structure)
        level_path = self.get_sublevel_folder(sublevel_string)
        
        # Define answers for all sublevels using numeric filename keys
        level_1_answers = {
            '1.1': {'26': 'B', '29': 'D', '30': 'A', '31': 'A', '32': '9', '34': 'D'},
            '1.2': {'37': 'D', '40': 'C', '41': 'A', '42': 'C', '43': '7', '44': 'B'},
            '1.3': {'47': 'D', '48': 'D', '51': 'B', '52': 'C', '53': '9', '55': 'C'},
        }
        level_2_answers = {
            '2.1': {'63': 'C', '66': 'C', '67': 'A', '68': 'D', '71': '18', '74': 'A'},
            '2.2': {'79': 'D', '82': 'C', '83': 'A', '84': 'D', '85': '19', '87': 'A'},  # 85_solve.png
            '2.3': {'91': 'A', '94': 'D', '95': 'A', '96': 'A', '97': '15', '99': 'B'},  # 97_solve.png
        }
        level_3_answers = {
            '3.1': {'110': 'A', '111': 'D', '112': 'A', '113': 'D', '114': '26', '115': 'B'},
            '3.2': {'119': 'D', '120': 'C', '121': 'A', '122': 'B', '123': '22', '126': 'B'},  # 123_solve.png
            '3.3': {'130': 'D', '131': 'A', '132': 'A', '133': 'A', '134': '27', '136': 'D'},  # 134_solve.png
        }
        level_4_answers = {
            '4.1': {'146': 'C', '147': 'B', '148': 'A', '149': 'C', '150': '32', '152': 'B'},
            '4.2': {'156': 'C', '157': 'D', '158': 'A', '159': 'B', '160': '38', '161': 'B'},
            '4.3': {'165': 'A', '166': 'A', '167': 'C', '168': 'A', '169': '32', '171': 'C'},
        }
        level_5_answers = {
            '5.1': {'180': 'C', '181': 'D', '182': 'A', '183': 'A', '184': '48', '187': 'D'},  # 184_solve.png
            '5.2': {'190': 'D', '191': 'B', '192': 'A', '193': 'B', '194': '48', '196': 'D'},  # 194_solve.png
            '5.3': {'200': 'A', '201': 'C', '202': 'D', '203': 'B', '204': '48', '206': 'B'},
        }
        level_6_answers = {
            '6.1': {'214': 'B', '215': 'C', '216': 'D', '217': 'C', '218': '60', '219': 'B'},
            '6.2': {'222': 'B', '223': 'B', '224': 'D', '225': 'A', '226': '60', '228': 'C'},
            '6.3': {'232': 'C', '233': 'D', '234': 'A', '235': 'A', '236': '57', '238': 'C'},
        }
        level_7_answers = {
            '7.1': {'245': 'A', '246': 'D', '247': 'B', '248': 'A', '249': '65', '250': 'A'},
            '7.2': {'254': 'B', '255': 'C', '256': 'A', '257': 'C', '258': '66', '260': 'D'},  # 258_solve.png  
            '7.3': {'263': 'A', '264': 'C', '265': 'C', '266': 'C', '267': '66', '269': 'D'},
        }
        level_8_answers = {
            '8.1': {'274': 'C', '275': 'B', '276': 'D', '277': 'B', '278': '75', '279': 'A'},
            '8.2': {'283': 'A', '284': 'B', '285': 'D', '286': 'C', '287': '80', '289': 'C'},  # 288_solve_.png
            '8.3': {'293': 'C', '294': 'C', '295': 'A', '296': 'C', '297': '76', '299': 'A'},
        }
        level_9_answers = {
            '9.1': {'307': 'A', '308': 'C', '309': 'D', '310': 'B', '311': '85', '312': 'C'},
            '9.2': {'316': 'A', '317': 'D', '318': 'D', '319': 'A', '320': '87', '322': 'B'},
            '9.3': {'325': 'D', '326': 'A', '327': 'B', '328': 'A', '329': '86', '331': 'C'},
        }
        level_10_answers = {
            '10.1': {'339': 'D', '340': 'A', '341': 'A', '342': 'A', '343': '98', '344': 'D'},
            '10.2': {'348': 'D', '349': 'C', '350': 'A', '351': 'A', '352': '95', '354': 'D'},
            '10.3': {'357': 'C', '358': 'D', '359': 'B', '360': 'B', '361': '92', '363': 'A'},
        }
        level_answers = {
            1: level_1_answers,
            2: level_2_answers,
            3: level_3_answers,
            4: level_4_answers,
            5: level_5_answers,
            6: level_6_answers,
            7: level_7_answers,
            8: level_8_answers,
            9: level_9_answers,
            10: level_10_answers,
        }
        
        if level_path and os.path.exists(level_path):
            # Load question images from the level directory
            question_files = []
            for file in os.listdir(level_path):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    question_files.append(file)
            
            # Custom sort: story/intro files first, then AGONSA files in specific order
            def sort_question_files(filename):
                """Sort files: numeric first, then story/intro, then AGONSA in order a, g, o, n, s, ans"""
                filename_lower = filename.lower()
                
                # Numeric prefix (e.g., "30_what..." or "120.png")
                match = re.match(r"^(\d+)", filename_lower)
                if match:
                    return (-1, int(match.group(1)), filename_lower)
                
                # Check if it's an AGONSA file and determine order
                # Order: a (asked), g (given), o (operation), n (number sentence), s (solve), ans (answer)
                # Check for 'ans' first to avoid matching 'asked' files
                if filename_lower == 'ans.jpg' or filename_lower.startswith('ans.'):
                    return (1, 5)  # Category 1, order 5 (ans - what is the answer)
                elif 'the answer' in filename_lower or (filename_lower.endswith('answer_.jpg') or filename_lower.endswith('answer.jpg')):
                    return (1, 5)  # Category 1, order 5 (ans - what is the answer)
                elif filename_lower == 'a.jpg' or (filename_lower.startswith('a.') and filename_lower.endswith('.jpg')):
                    return (1, 0)  # Category 1, order 0 (a - what is asked)
                elif 'asked' in filename_lower:
                    return (1, 0)  # Category 1, order 0 (a - what is asked)
                elif filename_lower == 'g.jpg' or (filename_lower.startswith('g.') and filename_lower.endswith('.jpg')):
                    return (1, 1)  # Category 1, order 1 (g - what is given)
                elif 'given' in filename_lower:
                    return (1, 1)  # Category 1, order 1 (g - what is given)
                elif filename_lower == 'o.jpg' or (filename_lower.startswith('o.') and filename_lower.endswith('.jpg')):
                    return (1, 2)  # Category 1, order 2 (o - what operation to be used)
                elif 'operation' in filename_lower:
                    return (1, 2)  # Category 1, order 2 (o - what operation to be used)
                elif filename_lower == 'n.jpg' or (filename_lower.startswith('n.') and filename_lower.endswith('.jpg')):
                    return (1, 3)  # Category 1, order 3 (n - what is number sentence)
                elif 'number sentence' in filename_lower:
                    return (1, 3)  # Category 1, order 3 (n - what is number sentence)
                elif filename_lower == 's.jpg' or (filename_lower.startswith('s.') and filename_lower.endswith('.jpg')):
                    return (1, 4)  # Category 1, order 4 (s - solve)
                elif filename_lower == 'solve.jpg' or filename_lower.startswith('solve.'):
                    return (1, 4)  # Category 1, order 4 (s - solve)
                else:
                    # Story/intro files - sort alphabetically within category 0
                    return (0, filename_lower)
            
            question_files.sort(key=sort_question_files)
            
            for i, question_file in enumerate(question_files):
                question_data = {
                    'image_path': os.path.join(level_path, question_file),
                    'question_number': i + 1,
                    'correct_answer': 1,  # Default correct answer (A=1, B=2, C=3, D=4)
                    'audio_path': None,   # Will be set if audio file exists
                    'image': None,        # Will be loaded when needed
                    'is_scenario': False,
                    'needs_text_input': False,
                    'text_input_opened': False
                }
                
                # Look for corresponding audio file
                # Priority: 1. VOICE OVER (exact match - play voice over with its associated PNG)
                #           2. keyword AGONSA, 3. level dir, 4. background music
                # Audio file name matches photo name (e.g., "189.png" → "189.mp3")
                audio_file_name = question_file.rsplit('.', 1)[0] + '.mp3'  # e.g., "189.mp3", "341.mp3"
                audio_path = None
                filename_lower = question_file.lower()
                
                # First, check VOICE OVER - exact match so voice over plays with its associated PNG
                voice_over_path = resource_path(f"assets/audio/VOICE OVER/{audio_file_name}")
                if os.path.exists(voice_over_path):
                    audio_path = voice_over_path
                    print(f"Found voice over for {question_file}: {audio_file_name}")
                
                # Second, check keyword-based AGONSA audio (when no voice over for this PNG)
                if not audio_path:
                    keyword_audio_map = {
                        "asked": "asked.mp3",
                        "given": "given.mp3",
                        "operation": "operation.mp3",
                        "number sentence": "number sentence.mp3",
                        "number_sentence": "number sentence.mp3",
                        "solve": "solve.mp3",
                        "answer": "answer.mp3",
                    }
                    for keyword, audio_name in keyword_audio_map.items():
                        if keyword in filename_lower:
                            keyword_audio_path = resource_path(f"assets/audio/agonsa/{audio_name}")
                            if os.path.exists(keyword_audio_path):
                                audio_path = keyword_audio_path
                                print(f"Found keyword AGONSA audio for {question_file}: {audio_name}")
                            break
                
                # Third, check level directory as fallback
                if not audio_path:
                    level_audio_file = audio_file_name
                    level_audio_path = os.path.join(level_path, level_audio_file)
                    if os.path.exists(level_audio_path):
                        audio_path = resource_path(level_audio_path)
                        print(f"Found level audio for {question_file}: {level_audio_file}")
                
                # If audio found, use it; otherwise fallback to background music
                if audio_path:
                    question_data['audio_path'] = audio_path
                else:
                    # Use background music as fallback if no specific audio assigned
                    background_music_path = resource_path("assets/audio/BACKGROUND MUSIC/BACKGROUND MUSIC.mp3")
                    if os.path.exists(background_music_path):
                        question_data['audio_path'] = background_music_path
                        print(f"No audio found for {question_file}, using background music")
                    else:
                        question_data['audio_path'] = None
                
                # Parse main level number for answer lookup
                main_level = int(sublevel_string.split('.')[0])
                
                # Set correct answers based on level
                filename_lower = question_file.lower()
                numeric_match = re.match(r"^(\d+)", filename_lower)
                numeric_key = numeric_match.group(1) if numeric_match else None
                
                if main_level in level_answers and sublevel_string in level_answers[main_level]:
                    sublevel_answers = level_answers[main_level][sublevel_string]
                    answer_value = None
                    
                    if question_file in sublevel_answers:
                        answer_value = sublevel_answers[question_file]
                    elif numeric_key and numeric_key in sublevel_answers:
                        answer_value = sublevel_answers[numeric_key]
                    
                    if answer_value is not None:
                        question_data['is_scenario'] = False
                        question_data['needs_text_input'] = str(answer_value).isdigit()
                        
                        if question_data['needs_text_input']:
                            question_data['correct_answer'] = str(answer_value)
                        elif answer_value in ['A', 'B', 'C', 'D']:
                            question_data['correct_answer'] = ord(answer_value) - ord('A') + 1
                        else:
                            question_data['correct_answer'] = 1
                    else:
                        # Image not in answer key - treat as scenario (no answer required)
                        question_data['is_scenario'] = True
                        question_data['needs_text_input'] = False
                        question_data['correct_answer'] = None
                else:
                    # Level not in mapping - treat as scenario by default
                    question_data['is_scenario'] = True
                    question_data['needs_text_input'] = False
                    question_data['correct_answer'] = None
                
                self.level_questions.append(question_data)
        
        print(f"Loaded {len(self.level_questions)} questions for sublevel {sublevel_string}")
    
    def play_question_audio(self):
        """Play audio for current question - use background music if no specific audio"""
        if (self.current_question_index < len(self.level_questions) and 
            self.level_questions[self.current_question_index]['audio_path']):
            
            audio_path = self.level_questions[self.current_question_index]['audio_path']
            try:
                pygame.mixer.music.load(audio_path)
                # If it's background music, loop it; otherwise play once
                if "BACKGROUND MUSIC" in audio_path:
                    pygame.mixer.music.play(-1)  # Loop indefinitely
                    print(f"Playing background music for question {self.current_question_index + 1}: {audio_path}")
                else:
                    pygame.mixer.music.play()  # Play once
                    print(f"Playing question {self.current_question_index + 1} audio: {audio_path}")
                    # Resume background music immediately when the clip ends
                    if not hasattr(self, "bg_music_resume_event"):
                        self.bg_music_resume_event = pygame.USEREVENT + 2
                    pygame.mixer.music.set_endevent(self.bg_music_resume_event)
            except Exception as e:
                print(f"Error playing question audio: {e}")
        else:
            # No audio for this question - stop any playing music
            pygame.mixer.music.stop()
            print(f"No audio for question {self.current_question_index + 1}")
    
    def handle_level_question_input(self, event):
        """Handle input in level question state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                # Go back to map or close text input
                if self.text_input_active:
                    self.text_input_active = False
                    self.text_input_value = ""
                else:
                    self.current_state = "map_image"
            elif event.key == pygame.K_SPACE:
                # Check if current question needs text input
                if (self.current_question_index < len(self.level_questions) and 
                    self.level_questions[self.current_question_index].get('needs_text_input', False)):
                    # Activate text input for problem 35
                    self.text_input_active = True
                    self.text_input_value = ""
                # Space bar to proceed (for scenario images)
                elif (self.current_question_index < len(self.level_questions) and 
                    self.level_questions[self.current_question_index].get('is_scenario', False)):
                    self.check_answer(None)  # Proceed without answer
            elif self.text_input_active:
                # Handle text input
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    # Submit text input answer
                    self.submit_text_answer()
                elif event.key == pygame.K_BACKSPACE:
                    # Remove last character
                    self.text_input_value = self.text_input_value[:-1]
                else:
                    # Add character (numbers and basic math symbols)
                    char = event.unicode
                    if char.isdigit() or char in '+-*/=.':
                        self.text_input_value += char
            elif event.key == pygame.K_1:
                self.check_answer(1)
            elif event.key == pygame.K_2:
                self.check_answer(2)
            elif event.key == pygame.K_3:
                self.check_answer(3)
            elif event.key == pygame.K_4:
                self.check_answer(4)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Check if text input needs to be activated by click on problem image
                if (self.current_question_index < len(self.level_questions) and 
                    self.level_questions[self.current_question_index].get('needs_text_input', False) and not self.text_input_active):
                    # Click anywhere on problem 35 to open text input
                    self.text_input_active = True
                    self.text_input_value = ""
                # Check if this is a scenario image
                elif (self.current_question_index < len(self.level_questions) and 
                    self.level_questions[self.current_question_index].get('is_scenario', False)):
                    # Click to proceed for scenario images
                    self.check_answer(None)
                else:
                    # Click anywhere else to go back to map
                    self.current_state = "map_image"
        return True
    
    def submit_text_answer(self):
        """Submit text input answer for problem solving questions"""
        if self.current_question_index >= len(self.level_questions):
            return
        
        question_data = self.level_questions[self.current_question_index]
        
        if self.text_input_value.strip():
            self.text_input_active = False
            answer_to_check = self.text_input_value.strip()
            
            # Get expected answer from question data
            expected_answer = question_data.get('correct_answer', '').strip() if isinstance(question_data.get('correct_answer'), str) else ''
            
            # Compare answers (case-insensitive, strip whitespace)
            if answer_to_check.lower() == expected_answer.lower():
                # Correct answer
                self.correct_answers += 1
                self.show_reward('correct')
                self.text_input_value = ""
                # Move to next question - this will happen when reward is dismissed
                self.current_question_index += 1
            else:
                # Wrong answer
                self.show_reward('wrong')
                self.text_input_value = ""  # Clear input for retry
    
    def check_answer(self, answer):
        """Check if the answer is correct"""
        if self.current_question_index >= len(self.level_questions):
            return
        
        question_data = self.level_questions[self.current_question_index]
        
        # Check if this is a scenario image (no answer needed)
        if question_data.get('is_scenario', False):
            # Just move to next question
            self.current_question_index += 1
            if self.current_question_index >= len(self.level_questions):
                # All questions completed - mark sublevel as completed and show mission complete
                self.completed_levels.add(self.current_level_number)
                self.show_mission_complete(self.current_level_number)
            else:
                # Continue to next question
                self.current_state = "level_question"
                self.play_question_audio()
            return
        
        # Regular question with answer
        correct_answer = question_data['correct_answer']
        
        if answer == correct_answer:
            self.correct_answers += 1
            self.show_reward('correct')
            
            # Move to next question after showing reward (only if correct)
            self.current_question_index += 1
        else:
            # Wrong answer - show reward but DON'T advance to next question
            self.show_reward('wrong')
    
    def show_reward(self, reward_type):
        """Show reward animation"""
        self.showing_reward = True
        self.reward_type = reward_type
        self.reward_start_time = pygame.time.get_ticks()
        self.current_state = "level_reward"
        
        # Load reward video (CORRECT.mp4 or WRONG.mp4) for correct/wrong
        if reward_type in ('correct', 'wrong') and MOVIEPY_AVAILABLE:
            self._close_reward_video()
            try:
                path = resource_path(f"videos/REWARD/{reward_type.upper()}.mp4")
                if os.path.exists(path):
                    self.reward_video_clip = VideoFileClip(path)
                    self.reward_video_start_time = pygame.time.get_ticks()
            except Exception as e:
                print(f"Error loading reward video: {e}")
                self.reward_video_clip = None
        
        # Play reward audio
        self.play_reward_audio(reward_type)
    
    def _close_reward_video(self):
        """Close the correct/wrong reward video clip"""
        if self.reward_video_clip:
            try:
                self.reward_video_clip.close()
            except Exception:
                pass
            self.reward_video_clip = None
    
    def show_mission_complete(self, sublevel_string: str):
        """Show mission complete screen after sublevel or level completion"""
        # Parse level number from sublevel string (e.g., "1.1" -> main level 1)
        main_level = int(sublevel_string.split('.')[0])
        
        # Check if all sublevels of this main level are now completed (including the one we just added)
        all_sublevels_done = self.is_level_completed(main_level)
        
        # Check if this level was already completed before (check if it was completed before adding current sublevel)
        # Temporarily remove current sublevel to check if level was already complete
        temp_check_set = self.completed_levels.copy()
        temp_check_set.discard(sublevel_string)
        was_completed_before = True
        for sublevel_num in range(1, 4):
            sublevel_str = f"{main_level}.{sublevel_num}"
            if sublevel_str not in temp_check_set:
                was_completed_before = False
                break
        
        # Store the current sublevel being completed
        self.mission_complete_sublevel = sublevel_string
        
        # If all sublevels are done and this level wasn't completed before, show level completion sequence
        if all_sublevels_done and not was_completed_before:
            self.mission_complete_active = True
            self.mission_complete_type = 'level'
            self.mission_complete_sequence_index = 0  # Start with REWARD STARS.mp4
            self.mission_complete_level_number = main_level
            self.current_state = "mission_complete"
        else:
            # Just sublevel completion, show mission complete 3.jpg
            self.mission_complete_active = True
            self.mission_complete_type = 'sublevel'
            self.mission_complete_sequence_index = 0
            self.mission_complete_level_number = None
            self.current_state = "mission_complete"
    
    def play_reward_audio(self, reward_type):
        """Play audio for reward"""
        if not self.audio_enabled:
            return
            
        audio_path = None
        if reward_type == 'correct':
            audio_path = resource_path("assets/audio/BACKGROUND MUSIC/CORRECT.mp3")
        elif reward_type == 'wrong':
            audio_path = resource_path("assets/audio/BACKGROUND MUSIC/WRONG.mp3")
        elif reward_type == 'stars':
            audio_path = resource_path("assets/audio/BACKGROUND MUSIC/CORRECT.mp3")
        
        if audio_path and os.path.exists(audio_path):
            try:
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
                print(f"Playing reward audio: {audio_path}")
            except Exception as e:
                print(f"Error playing reward audio: {e}")
        else:
            print(f"Reward audio not found: {audio_path}")
    
    def play_background_music(self):
        """Play background music"""
        if not self.audio_enabled:
            return
            
        background_music_path = resource_path("assets/audio/BACKGROUND MUSIC/BACKGROUND MUSIC.mp3")
        
        if os.path.exists(background_music_path):
            try:
                pygame.mixer.music.load(background_music_path)
                pygame.mixer.music.play(-1)  # Loop indefinitely
                print(f"Playing background music: {background_music_path}")
            except Exception as e:
                print(f"Error playing background music: {e}")
        else:
            print(f"Background music not found: {background_music_path}")
    
    def handle_level_reward_input(self, event):
        """Handle input in level reward state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                # Continue after reward
                self.showing_reward = False
                self._close_reward_video()
                # Check if we came from exercise level
                if hasattr(self, 'previous_state_before_reward') and self.previous_state_before_reward == "exercise_level":
                    # Return to exercises flow
                    if self.reward_type == 'correct':
                        # On correct, proceed to next exercise level
                        if self.current_exercise_level < 10:
                            self.current_exercise_level += 1
                        # Reset inputs for the next level
                        self.exercise_inputs = ["", "", ""]
                        self.exercise_active_input = 0
                    self.current_state = "exercise_level"
                    # Reset the tracking
                    self.previous_state_before_reward = None
                elif self.current_question_index >= len(self.level_questions):
                    # Sublevel completed - mark it and show mission complete
                    self.completed_levels.add(self.current_level_number)
                    self.show_mission_complete(self.current_level_number)
                else:
                    # Continue to next question
                    self.current_state = "level_question"
                    self.play_question_audio()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Continue after reward
                self.showing_reward = False
                self._close_reward_video()
                # Check if we came from exercise level
                if hasattr(self, 'previous_state_before_reward') and self.previous_state_before_reward == "exercise_level":
                    # Return to exercises flow
                    if self.reward_type == 'correct':
                        # On correct, proceed to next exercise level
                        if self.current_exercise_level < 10:
                            self.current_exercise_level += 1
                        # Reset inputs for the next level
                        self.exercise_inputs = ["", "", ""]
                        self.exercise_active_input = 0
                    self.current_state = "exercise_level"
                    # Reset the tracking
                    self.previous_state_before_reward = None
                elif self.current_question_index >= len(self.level_questions):
                    # Sublevel completed - mark it and show mission complete
                    self.completed_levels.add(self.current_level_number)
                    self.show_mission_complete(self.current_level_number)
                else:
                    # Continue to next question
                    self.current_state = "level_question"
                    self.play_question_audio()
        return True
    
    def draw_level_question(self):
        """Draw the level question screen"""
        self.screen.fill(BLACK)
        
        if (self.current_question_index < len(self.level_questions)):
            question_data = self.level_questions[self.current_question_index]
            
            # Load question image if not already loaded
            if question_data['image'] is None:
                try:
                    question_data['image'] = pygame.image.load(question_data['image_path'])
                except Exception as e:
                    print(f"Error loading question image: {e}")
                    question_data['image'] = None
            
            content_rect = None
            if question_data['image']:
                # Scale and display question image
                scaled_question = self.scale_photo_to_fit(question_data['image'])
                question_rect = scaled_question.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(scaled_question, question_rect)
                content_rect = question_rect
            
            # Solve questions: user must press SPACE first to show input (no auto-open)
        else:
            # No more questions
            title = self.font_large.render("Level Complete!", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(title, title_rect)
        
        # Draw text input box if active
        if self.text_input_active:
            self.draw_text_input_box()
        
        # Instructions for navigation - on the image
        if self.text_input_active:
            # Show instructions for text input
            instruction_text = "Enter your answer and press ENTER, ESC to close"
        elif (self.current_question_index < len(self.level_questions) and 
            self.level_questions[self.current_question_index].get('needs_text_input', False)):
            # Problem solving question - click or press space to open input
            instruction_text = "Press SPACE or click to input answer, ESC to go back"
        elif (self.current_question_index < len(self.level_questions) and 
            self.level_questions[self.current_question_index].get('is_scenario', False)):
            # Scenario image - click to proceed
            instruction_text = "Click or press SPACE to continue, ESC to go back"
        else:
            # Regular question - answer with 1-4
            instruction_text = "Press 1-4 to answer, ESC to go back"
        
        self.draw_footer_instruction(instruction_text, content_rect)
    
    def draw_text_input_box(self):
        """Draw the text input box for problem solving questions"""
        # Position the text input box in the center
        input_x = (self.screen_width - self.text_input_rect.width) // 2
        input_y = self.screen_height // 2 + 100
        
        # Draw semi-transparent background overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw the input box
        input_rect = pygame.Rect(input_x, input_y, self.text_input_rect.width, self.text_input_rect.height)
        pygame.draw.rect(self.screen, WHITE, input_rect, 3)
        pygame.draw.rect(self.screen, BLACK, input_rect)
        
        # Draw the text value
        if self.text_input_value:
            text_surface = self.font_medium.render(self.text_input_value, True, WHITE)
            text_rect = text_surface.get_rect(center=(input_x + self.text_input_rect.width // 2, input_y + self.text_input_rect.height // 2))
            self.screen.blit(text_surface, text_rect)
        
        # Draw blinking cursor
        self.text_input_cursor_blink += 1
        if self.text_input_cursor_blink % 60 < 30:  # Blink every 30 frames
            cursor_x = input_x + 10 + self.font_medium.size(self.text_input_value)[0]
            cursor_y = input_y + 10
            cursor_height = self.text_input_rect.height - 20
            pygame.draw.line(self.screen, WHITE, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)
        
        # Draw title text
        title_text = "Enter your answer:"
        title_surface = self.font_medium.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(input_x + self.text_input_rect.width // 2, input_y - 30))
        self.screen.blit(title_surface, title_rect)

    def load_gif_frames(self, gif_path: str):
        """Load GIF frames using Pillow if available"""
        try:
            from PIL import Image
        except Exception:
            return []
        
        frames = []
        try:
            image = Image.open(gif_path)
            for frame_index in range(image.n_frames):
                image.seek(frame_index)
                frame = image.convert("RGBA")
                frame_surface = pygame.image.fromstring(frame.tobytes(), frame.size, "RGBA")
                frames.append(frame_surface)
        except Exception as e:
            print(f"Failed to load GIF frames: {e}")
            return []
        return frames
    
    def draw_level_reward(self):
        """Draw the level reward screen"""
        self.screen.fill(BLACK)
        
        # Load and display reward gif
        reward_path = None
        content_rect = None
        if self.reward_type == 'correct':
            reward_path = resource_path("videos/REWARD/CORRECT.mp4")
        elif self.reward_type == 'wrong':
            reward_path = resource_path("videos/REWARD/WRONG.mp4")
        elif self.reward_type == 'stars':
            # Handle stars as MP4 video
            reward_path = resource_path("videos/REWARD/REWARD STARS.mp4")
            
            # Initialize video if not already playing
            if not self.stars_video_playing:
                self.start_stars_video()
            
            # Display current video frame
            if self.stars_video_clip and self.stars_video_playing:
                current_time = (pygame.time.get_ticks() - self.stars_video_start_time) / 1000.0
                
                if current_time < self.stars_video_clip.duration:
                    try:
                        frame = self.stars_video_clip.get_frame(current_time)
                        # Convert numpy array to pygame surface
                        if NUMPY_AVAILABLE:
                            frame = np.swapaxes(frame, 0, 1)
                            frame_surface = pygame.surfarray.make_surface(frame)
                        else:
                            frame_surface = pygame.image.frombuffer(frame.tobytes(), (frame.shape[1], frame.shape[0]), "RGB")
                        
                        # Scale to fit screen
                        scaled_frame = self.scale_photo_to_fit(frame_surface)
                        frame_rect = scaled_frame.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                        self.screen.blit(scaled_frame, frame_rect)
                        content_rect = frame_rect
                    except Exception as e:
                        print(f"Error displaying stars video frame: {e}")
                        # Fallback to text
                        reward_text = "STARS! PERFECT SCORE!"
                        reward_surface = self.font_large.render(reward_text, True, WHITE)
                        reward_rect = reward_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                        self.screen.blit(reward_surface, reward_rect)
                        content_rect = None
                else:
                    # Video finished - show last frame
                    if self.stars_video_clip:
                        try:
                            last_frame = self.stars_video_clip.get_frame(self.stars_video_clip.duration - 0.1)
                            if NUMPY_AVAILABLE:
                                last_frame = np.swapaxes(last_frame, 0, 1)
                                frame_surface = pygame.surfarray.make_surface(last_frame)
                            else:
                                frame_surface = pygame.image.frombuffer(last_frame.tobytes(), (last_frame.shape[1], last_frame.shape[0]), "RGB")
                            
                            scaled_frame = self.scale_photo_to_fit(frame_surface)
                            frame_rect = scaled_frame.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                            self.screen.blit(scaled_frame, frame_rect)
                            content_rect = frame_rect
                        except Exception as e:
                            print(f"Error displaying last stars video frame: {e}")
                            content_rect = None
            else:
                # Fallback if video not available
                reward_text = "STARS! PERFECT SCORE!"
                reward_surface = self.font_large.render(reward_text, True, WHITE)
                reward_rect = reward_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(reward_surface, reward_rect)
                content_rect = None
        
        if self.reward_type != 'stars' and self.reward_video_clip and MOVIEPY_AVAILABLE:
            try:
                # Play MP4 reward video (looping)
                current_time = (pygame.time.get_ticks() - self.reward_video_start_time) / 1000.0
                if self.reward_video_clip.duration > 0:
                    current_time = current_time % self.reward_video_clip.duration
                frame = self.reward_video_clip.get_frame(current_time)
                if NUMPY_AVAILABLE:
                    frame = np.swapaxes(frame, 0, 1)
                    frame_surface = pygame.surfarray.make_surface(frame)
                else:
                    frame_surface = pygame.image.frombuffer(frame.tobytes(), (frame.shape[1], frame.shape[0]), "RGB")
                scaled_reward = self.scale_photo_to_fit(frame_surface)
                reward_rect = scaled_reward.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(scaled_reward, reward_rect)
                content_rect = reward_rect
            except Exception as e:
                print(f"Error displaying reward video: {e}")
                reward_text = self.reward_type.upper()
                reward_surface = self.font_large.render(reward_text, True, WHITE)
                reward_rect = reward_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(reward_surface, reward_rect)
                content_rect = None
        elif self.reward_type != 'stars':
            # Fallback text if MP4 not loaded (for correct/wrong rewards)
            reward_text = self.reward_type.upper()
            reward_surface = self.font_large.render(reward_text, True, WHITE)
            reward_rect = reward_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(reward_surface, reward_rect)
            content_rect = None
        
        # Instructions for navigation - on the reward image
        instruction_text = "Press SPACE or click to continue"
        self.draw_footer_instruction(instruction_text, content_rect)
    
    def draw_mission_complete(self):
        """Draw the mission complete screen"""
        self.screen.fill(BLACK)
        
        image_path = None
        
        if self.mission_complete_type == 'sublevel':
            # Sublevel completion: show mission complete3.jpg
            image_path = resource_path("assets/photos/MISSION COMPLETE & REWARDS/mission complete3.png")
        elif self.mission_complete_type == 'level':
            # Level completion: sequence of 3 screens
            if self.mission_complete_sequence_index == 0:
                # First: REWARD STARS.mp4
                stars_video_path = resource_path("videos/REWARD/REWARD STARS.mp4")
                
                # Initialize video if not already playing
                if not self.stars_video_playing:
                    self.start_stars_video()
                
                # Display current video frame
                if self.stars_video_clip and self.stars_video_playing:
                    current_time = (pygame.time.get_ticks() - self.stars_video_start_time) / 1000.0
                    
                    if current_time < self.stars_video_clip.duration:
                        try:
                            frame = self.stars_video_clip.get_frame(current_time)
                            # Convert numpy array to pygame surface
                            if NUMPY_AVAILABLE:
                                frame = np.swapaxes(frame, 0, 1)
                                frame_surface = pygame.surfarray.make_surface(frame)
                            else:
                                frame_surface = pygame.image.frombuffer(frame.tobytes(), (frame.shape[1], frame.shape[0]), "RGB")
                            
                            # Scale to fit screen
                            scaled_frame = self.scale_photo_to_fit(frame_surface)
                            image_rect = scaled_frame.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                            self.screen.blit(scaled_frame, image_rect)
                            content_rect = image_rect
                            
                            print(f"Successfully displaying stars video frame")
                        except Exception as e:
                            print(f"Error displaying stars video frame: {e}")
                            # Fallback to text
                            fallback_text = "Stars!"
                            text_surface = self.font_large.render(fallback_text, True, WHITE)
                            text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                            self.screen.blit(text_surface, text_rect)
                            content_rect = None
                    else:
                        # Video finished - show last frame
                        if self.stars_video_clip:
                            try:
                                last_frame = self.stars_video_clip.get_frame(self.stars_video_clip.duration - 0.1)
                                if NUMPY_AVAILABLE:
                                    last_frame = np.swapaxes(last_frame, 0, 1)
                                    frame_surface = pygame.surfarray.make_surface(last_frame)
                                else:
                                    frame_surface = pygame.image.frombuffer(last_frame.tobytes(), (last_frame.shape[1], last_frame.shape[0]), "RGB")
                                
                                scaled_frame = self.scale_photo_to_fit(frame_surface)
                                image_rect = scaled_frame.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                                self.screen.blit(scaled_frame, image_rect)
                                content_rect = image_rect
                            except Exception as e:
                                print(f"Error displaying last stars video frame: {e}")
                                content_rect = None
                else:
                    # Fallback if video not available
                    fallback_text = "Stars!"
                    text_surface = self.font_large.render(fallback_text, True, WHITE)
                    text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                    self.screen.blit(text_surface, text_rect)
                    content_rect = None
                
                # Skip the normal image loading for stars video
                image_path = None
            elif self.mission_complete_sequence_index == 1:
                # Second: MISSION COMPLETE 1.jpg
                image_path = resource_path("assets/photos/MISSION COMPLETE & REWARDS/MISSION COMPLETE 1.png")
        
        if image_path and os.path.exists(image_path):
            try:
                # Try to load the image/GIF
                mission_image = pygame.image.load(image_path)
                
                # Scale the image to fit the screen while maintaining aspect ratio
                scaled_image = self.scale_photo_to_fit(mission_image)
                image_rect = scaled_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(scaled_image, image_rect)
                content_rect = image_rect
                
                print(f"Successfully loaded mission complete image: {image_path}")
            except Exception as e:
                print(f"Error loading mission complete image: {e}")
                # Fallback to text
                fallback_text = "Mission Complete!"
                if self.mission_complete_type == 'level':
                    if self.mission_complete_sequence_index == 0:
                        fallback_text = "Stars!"
                    elif self.mission_complete_sequence_index == 1:
                        fallback_text = "Mission Complete 1!"
                    elif self.mission_complete_sequence_index == 2:
                        fallback_text = "Mission Complete 2!"
                
                text_surface = self.font_large.render(fallback_text, True, WHITE)
                text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(text_surface, text_rect)
                content_rect = None
        else:
            # Fallback text if image not found
            fallback_text = "Mission Complete!"
            if image_path:
                print(f"Mission complete image not found: {image_path}")
            
            text_surface = self.font_large.render(fallback_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(text_surface, text_rect)
            content_rect = None
        
        # Instructions for navigation - on the mission complete image
        instruction_text = "Press SPACE or click to continue"
        self.draw_footer_instruction(instruction_text, content_rect)
    
    def handle_mission_complete_input(self, event):
        """Handle input in mission complete state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                # Advance mission complete sequence or proceed to next sublevel
                if self.mission_complete_type == 'sublevel':
                    # Sublevel completion: proceed to next sublevel or go to map
                    self.mission_complete_active = False
                    self.proceed_after_sublevel_complete()
                elif self.mission_complete_type == 'level':
                    # Level completion: advance through sequence
                    # Clean up stars video if we're moving past it
                    if self.mission_complete_sequence_index == 0 and self.stars_video_clip:
                        try:
                            self.stars_video_clip.close()
                        except:
                            pass
                        self.stars_video_clip = None
                        self.stars_video_playing = False
                    
                    self.mission_complete_sequence_index += 1
                    if self.mission_complete_sequence_index >= 3:
                        # Sequence complete: show level-specific map
                        self.mission_complete_active = False
                        self.mission_complete_sequence_index = 0
                        self.show_level_map()
                    # Otherwise, continue showing next image in sequence
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Advance mission complete sequence or proceed to next sublevel
                if self.mission_complete_type == 'sublevel':
                    # Sublevel completion: proceed to next sublevel or go to map
                    self.mission_complete_active = False
                    self.proceed_after_sublevel_complete()
                elif self.mission_complete_type == 'level':
                    # Level completion: advance through sequence
                    # Clean up stars video if we're moving past it
                    if self.mission_complete_sequence_index == 0 and self.stars_video_clip:
                        try:
                            self.stars_video_clip.close()
                        except:
                            pass
                        self.stars_video_clip = None
                        self.stars_video_playing = False
                    
                    self.mission_complete_sequence_index += 1
                    if self.mission_complete_sequence_index >= 3:
                        # Sequence complete: show level-specific map
                        self.mission_complete_active = False
                        self.mission_complete_sequence_index = 0
                        self.show_level_map()
                    # Otherwise, continue showing next image in sequence
        return True
    
    def draw_sublevel_selection(self):
        """Draw the sublevel selection screen"""
        self.screen.fill(BLACK)
        
        if self.map_image is not None:
            # Show map in background (dimmed)
            scaled_map = self.scale_photo_to_fit(self.map_image)
            map_rect = scaled_map.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            # Draw dimmed map
            dimmed_map = scaled_map.copy()
            dimmed_map.set_alpha(128)
            self.screen.blit(dimmed_map, map_rect)
        else:
            # Set up top right area
            self.top_right_area = None
        
        # Draw sublevel selection overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        title_text = f"Select Sublevel for Level {self.selected_main_level}"
        title_surface = self.font_large.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Draw sublevel options
        sublevel_y_start = self.screen_height // 2 - 100
        for i in range(1, 4):  # 3 sublevels
            sublevel_number = f"{self.selected_main_level}.{i}"
            sublevel_key = str(i)
            
            # Check if completed
            is_completed = sublevel_number in self.completed_levels
            
            # Sublevel text
            sublevel_text = f"Press {sublevel_key}: Level {sublevel_number}"
            if is_completed:
                sublevel_text += " ✓"
            
            color = GREEN if is_completed else WHITE
            sublevel_surface = self.font_medium.render(sublevel_text, True, color)
            sublevel_rect = sublevel_surface.get_rect(center=(self.screen_width // 2, sublevel_y_start + i * 80))
            self.screen.blit(sublevel_surface, sublevel_rect)
        
        # Instructions
        instruction_text = "Press 1-3 to select sublevel, ESC to go back"
        self.draw_footer_instruction(instruction_text)
    
    def handle_sublevel_selection_input(self, event):
        """Handle input in sublevel selection state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                # Go back to map
                self.selected_main_level = None
                self.current_state = "map_image"
            elif event.key == pygame.K_1:
                # Start sublevel X.1
                sublevel = f"{self.selected_main_level}.1"
                self.start_level(sublevel)
            elif event.key == pygame.K_2:
                # Start sublevel X.2
                sublevel = f"{self.selected_main_level}.2"
                self.start_level(sublevel)
            elif event.key == pygame.K_3:
                # Start sublevel X.3
                sublevel = f"{self.selected_main_level}.3"
                self.start_level(sublevel)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Click anywhere to go back
                self.selected_main_level = None
                self.current_state = "map_image"
        return True
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif hasattr(self, "bg_music_resume_event") and event.type == self.bg_music_resume_event:
                    # Resume background music after VO/clip ends
                    pygame.mixer.music.set_endevent()
                    self.play_background_music()
                elif event.type == self.level_intro_music_end_event and self.current_state == "level_intro":
                    # Level intro track finished - play next part or mark all done
                    next_index = self.level_intro_audio_index + 1
                    if self.level_intro_audio_paths and next_index < len(self.level_intro_audio_paths):
                        self._play_level_intro_audio_part(next_index)
                    else:
                        pygame.mixer.music.set_endevent()
                        self.level_intro_all_audio_finished = True
                elif event.type == pygame.VIDEORESIZE:
                    # Handle window resize
                    self.handle_window_resize(event.w, event.h)
                elif self.current_state == "splash":
                    running = self.handle_splash_input(event)
                elif self.current_state == "second_page":
                    running = self.handle_second_page_input(event)
                elif self.current_state == "select":
                    running = self.handle_select_input(event)
                elif self.current_state == "exercise_level":
                    running = self.handle_exercise_level_input(event)
                elif self.current_state == "intro":
                    running = self.handle_intro_input(event)
                elif self.current_state == "sublevel_vocab":
                    running = self.handle_sublevel_vocab_input(event)
                elif self.current_state == "level_intro":
                    running = self.handle_level_intro_input(event)
                elif self.current_state == "map":
                    running = self.handle_map_input(event)
                elif self.current_state == "map_image":
                    running = self.handle_map_image_input(event)
                elif self.current_state == "level_question":
                    running = self.handle_level_question_input(event)
                elif self.current_state == "level_reward":
                    running = self.handle_level_reward_input(event)
                elif self.current_state == "mechanics":
                    running = self.handle_mechanics_input(event)
                elif self.current_state == "menu":
                    running = self.handle_menu_input(event)
                elif self.current_state == "slideshow":
                    running = self.handle_slideshow_input(event)
                elif self.current_state == "intro_new_game":
                    running = self.handle_intro_new_game_input(event)
                elif self.current_state == "sublevel_selection":
                    running = self.handle_sublevel_selection_input(event)
                elif self.current_state == "mission_complete":
                    running = self.handle_mission_complete_input(event)
            
            # Draw current state
            if self.current_state == "splash":
                self.draw_splash()
            elif self.current_state == "second_page":
                self.draw_second_page()
            elif self.current_state == "select":
                self.draw_select()
            elif self.current_state == "exercise_level":
                self.draw_exercise_level()
            elif self.current_state == "intro":
                self.draw_intro()
            elif self.current_state == "sublevel_vocab":
                self.draw_sublevel_vocab()
            elif self.current_state == "level_intro":
                self.draw_level_intro()
            elif self.current_state == "map":
                self.draw_map()
            elif self.current_state == "map_image":
                self.draw_map_image()
            elif self.current_state == "level_question":
                self.draw_level_question()
            elif self.current_state == "level_reward":
                self.draw_level_reward()
            elif self.current_state == "mechanics":
                self.draw_mechanics()
            elif self.current_state == "menu":
                self.draw_menu()
            elif self.current_state == "slideshow":
                self.draw_slideshow()
            elif self.current_state == "intro_new_game":
                self.draw_intro_new_game()
            elif self.current_state == "sublevel_selection":
                self.draw_sublevel_selection()
            elif self.current_state == "mission_complete":
                self.draw_mission_complete()

            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def handle_window_resize(self, width, height):
        """Handle window resize events - optimized for laptops"""
        # Enforce minimum window size
        width = max(width, self.min_width)
        height = max(height, self.min_height)
        
        self.screen_width = width
        self.screen_height = height
        
        # Update screen size
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        
        # Recalculate font sizes based on new screen size - optimized for laptops
        base_font_size = max(24, min(self.screen_width, self.screen_height) // 30)
        self.font_large = pygame.font.Font(None, int(base_font_size * 1.8))
        self.font_medium = pygame.font.Font(None, int(base_font_size * 1.2))
        self.font_small = pygame.font.Font(None, int(base_font_size))
        
        
        print(f"Window resized to: {width}x{height} (laptop optimized)")
    
    def start_new_game(self):
        """Start new game with intro sequence showing 5.png and playing intro audio"""
        self.current_state = "intro_new_game"
        
        # Reset intro media state
        self.intro_image = None
        self.intro_video_clip = None
        self.intro_video_playing = False
        self.intro_video_start_time = 0
        
        # Load intro media (5.mp4 preferred)
        intro_path = resource_path("assets/photos/intro/5.mp4")
        if os.path.exists(intro_path):
            try:
                if MOVIEPY_AVAILABLE:
                    self.intro_video_clip = VideoFileClip(intro_path)
                    self.intro_video_playing = True
                    self.intro_video_start_time = pygame.time.get_ticks()
                    print(f"Loaded intro video: {intro_path}")
                else:
                    print("MoviePy not available for intro video.")
            except Exception as e:
                print(f"Error loading intro video: {e}")
                self.intro_video_clip = None
                self.intro_video_playing = False
        else:
            print(f"Intro video not found at {intro_path}")
        
        # Fallback image if video unavailable
        if not self.intro_video_clip:
            fallback_image_path = resource_path("assets/photos/intro/5.png")
            if os.path.exists(fallback_image_path):
                try:
                    intro_image = pygame.image.load(fallback_image_path)
                    self.intro_image = self.scale_photo_to_fit(intro_image)
                    print(f"Loaded intro fallback image: {fallback_image_path}")
                except pygame.error as e:
                    print(f"Error loading intro fallback image: {e}")
                    self.intro_image = None
        
        # Play intro audio (intro (1).mp3)
        audio_path = resource_path("assets/audio/VOICE OVER/intro (1) .mp3")
        if os.path.exists(audio_path):
            try:
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
                print(f"Playing intro audio: {audio_path}")
            except Exception as e:
                print(f"Error playing intro audio: {e}")
        else:
            print(f"Intro audio not found: {audio_path}")
    
    def draw_intro_new_game(self):
        """Draw the new game intro screen"""
        self.screen.fill(BLACK)
        
        content_rect = None
        if self.intro_video_clip and self.intro_video_playing:
            current_time = (pygame.time.get_ticks() - self.intro_video_start_time) / 1000.0
            try:
                if self.intro_video_clip.duration > 0:
                    current_time = current_time % self.intro_video_clip.duration
                frame = self.intro_video_clip.get_frame(current_time)
                if NUMPY_AVAILABLE:
                    frame = np.swapaxes(frame, 0, 1)
                    frame_surface = pygame.surfarray.make_surface(frame)
                else:
                    frame_surface = pygame.image.frombuffer(frame.tobytes(), (frame.shape[1], frame.shape[0]), "RGB")
                scaled_frame = self.scale_photo_to_fit(frame_surface)
                intro_rect = scaled_frame.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(scaled_frame, intro_rect)
                content_rect = intro_rect
            except Exception as e:
                print(f"Error displaying intro video frame: {e}")
        elif self.intro_image:
            intro_rect = self.intro_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(self.intro_image, intro_rect)
            content_rect = intro_rect
        
        instruction_text = "Press any key or click to start Level 1"
        self.draw_footer_instruction(instruction_text, content_rect)
    
    def handle_intro_new_game_input(self, event):
        """Handle input in intro new game state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self.toggle_fullscreen()
            else:
                if self.intro_video_clip:
                    try:
                        self.intro_video_clip.close()
                    except Exception:
                        pass
                self.intro_video_clip = None
                self.intro_video_playing = False
                # Start with sublevel 1.1
                self.start_level("1.1")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.intro_video_clip:
                    try:
                        self.intro_video_clip.close()
                    except Exception:
                        pass
                self.intro_video_clip = None
                self.intro_video_playing = False
                self.start_level("1.1")
        return True

if __name__ == "__main__":
    game = PhotoSlideshowGame()
    game.run()