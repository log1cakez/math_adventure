import pygame
import os
import sys
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
        pygame.display.set_caption("Photo Slideshow Game")
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
        
        # Video clips for splash and second page
        self.splash_video_clip = None
        self.splash_video_playing = False
        self.splash_video_start_time = 0
        self.second_page_video_clip = None
        self.second_page_video_playing = False
        self.second_page_video_start_time = 0
        self.second_page_video_finished = False  # Track if video has finished
        self.second_page_last_frame = None  # Store last frame
        
        # Interactive areas (you can adjust these coordinates based on your image)
        self.gear_area = None  # Will be set based on image dimensions
        
        # Start playing background music when app launches
        self.play_background_music()
        
    def load_levels(self) -> List[Dict]:
        """Load level information from directories"""
        levels = []
        base_path = "photos"
        
        # Create photos directory if it doesn't exist
        if not os.path.exists(base_path):
            os.makedirs(base_path)
            
        # Create sample level directories and placeholder images
        for i in range(1, 6):  # Create 5 levels
            level_path = os.path.join(base_path, f"level_{i}")
            if not os.path.exists(level_path):
                os.makedirs(level_path)
                # Create a placeholder text file for each level
                with open(os.path.join(level_path, "info.txt"), "w") as f:
                    f.write(f"Level {i} - Add your photos here!\nSupported formats: .jpg, .jpeg, .png, .bmp")
            
            levels.append({
                "name": f"Level {i}",
                "path": level_path,
                "photos": self.get_photos_from_directory(level_path)
            })
            
        return levels
    
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
    
    def draw_splash(self):
        """Draw the splash screen with video"""
        self.screen.fill(BLACK)
        
        # Initialize video if not already playing
        if not self.splash_video_playing and self.splash_video:
            self.start_splash_video()
        
        # Display current video frame
        if self.splash_video_clip and self.splash_video_playing:
            current_time = (pygame.time.get_ticks() - self.splash_video_start_time) / 1000.0
            
            if current_time < self.splash_video_clip.duration:
                try:
                    frame = self.splash_video_clip.get_frame(current_time)
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
                    
                    # Set up clickable gear area (top right)
                    gear_x = frame_rect.x + frame_rect.width * 0.85
                    gear_y = frame_rect.y + frame_rect.height * 0.1
                    gear_size = 60
                    self.gear_area = pygame.Rect(gear_x, gear_y, gear_size, gear_size)
                except Exception as e:
                    print(f"Error displaying splash video frame: {e}")
                    # Fallback
                    title = self.font_large.render("Photo Slideshow Game", True, WHITE)
                    title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
                    self.screen.blit(title, title_rect)
            else:
                # Video finished - automatically transition to second page
                self.splash_video_playing = False
                self.current_state = "second_page"
                # Clean up splash video clip
                if self.splash_video_clip:
                    try:
                        self.splash_video_clip.close()
                    except:
                        pass
                    self.splash_video_clip = None
        else:
            # Fallback if video not available
            title = self.font_large.render("Photo Slideshow Game", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
            self.screen.blit(title, title_rect)
        
        # Instructions to proceed - moved to footer
        instruction_text = "Click anywhere to continue, or click gear for mechanics..."
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_second_page(self):
        """Draw the second page with video"""
        self.screen.fill(BLACK)
        
        # Initialize video if not already playing
        if not self.second_page_video_playing and self.second_page_video:
            self.start_second_page_video()
        
        # Display current video frame or last frame if finished
        if self.second_page_video_clip:
            if self.second_page_video_finished and self.second_page_last_frame:
                # Video has finished - display stored last frame
                scaled_frame = self.scale_photo_to_fit(self.second_page_last_frame)
                frame_rect = scaled_frame.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(scaled_frame, frame_rect)
                
                # Set up clickable top right area for mechanics
                self.top_right_area = pygame.Rect(frame_rect.x + frame_rect.width * 0.9, frame_rect.y, frame_rect.width * 0.1, frame_rect.height * 0.2)
            elif self.second_page_video_playing:
                # Video is still playing
                current_time = (pygame.time.get_ticks() - self.second_page_video_start_time) / 1000.0
                
                if current_time < self.second_page_video_clip.duration:
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
                        
                        # Set up clickable top right area for mechanics (10% width, 20% height)
                        self.top_right_area = pygame.Rect(frame_rect.x + frame_rect.width * 0.9, frame_rect.y, frame_rect.width * 0.1, frame_rect.height * 0.2)
                    except Exception as e:
                        print(f"Error displaying second page video frame: {e}")
                        # Fallback
                        title = self.font_large.render("MAIN MENU", True, WHITE)
                        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                        self.screen.blit(title, title_rect)
                        self.top_right_area = None
                else:
                    # Video just finished - capture last frame and pause
                    if not self.second_page_video_finished:
                        self.second_page_video_playing = False  # Pause video
                        self.second_page_video_finished = True
                        
                        # Background music already playing, keep it going
                        
                        # Capture and store last frame
                        try:
                            last_frame = self.second_page_video_clip.get_frame(self.second_page_video_clip.duration - 0.1)
                            # Convert numpy array to pygame surface
                            if NUMPY_AVAILABLE:
                                last_frame = np.swapaxes(last_frame, 0, 1)
                                frame_surface = pygame.surfarray.make_surface(last_frame)
                            else:
                                frame_surface = pygame.image.frombuffer(last_frame.tobytes(), (last_frame.shape[1], last_frame.shape[0]), "RGB")
                            
                            self.second_page_last_frame = frame_surface
                            print("Video finished, showing last frame")
                        except Exception as e:
                            print(f"Error capturing last frame: {e}")
                        
                        # Background music should already be playing since video start
                        # Ensure it continues if it stopped
                        if not pygame.mixer.music.get_busy():
                            self.play_background_music()
                    
                    # Display stored last frame
                    if self.second_page_last_frame:
                        scaled_frame = self.scale_photo_to_fit(self.second_page_last_frame)
                        frame_rect = scaled_frame.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                        self.screen.blit(scaled_frame, frame_rect)
                        self.top_right_area = pygame.Rect(frame_rect.x + frame_rect.width * 0.9, frame_rect.y, frame_rect.width * 0.1, frame_rect.height * 0.2)
        else:
            # Fallback if video not available
            title = self.font_large.render("MAIN MENU", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(title, title_rect)
            self.top_right_area = None
        
        # Instructions for the three options - moved to footer
        instruction_text = "Press 1 for Map, 2 for New Game, 3 for Exercises, click top right for mechanics"
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_select(self):
        """Draw the select screen"""
        self.screen.fill(BLACK)
        
        if self.select_image:
            # Display the select image centered
            select_rect = self.select_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(self.select_image, select_rect)
            
            # Set up clickable top right area for mechanics (10% width, 20% height)
            self.top_right_area = pygame.Rect(select_rect.x + select_rect.width * 0.9, select_rect.y, select_rect.width * 0.1, select_rect.height * 0.2)
        else:
            # Fallback if select image not found
            title = self.font_large.render("SELECT", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(title, title_rect)
            self.top_right_area = None
        
        # Instructions for level selection - moved to footer
        instruction_text = "Press 1-10 to select a level, ESC to go back, click top right for mechanics"
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_exercise_level(self):
        """Draw the exercise level screen"""
        self.screen.fill(BLACK)
        
        # Display the current exercise level image
        if (self.current_exercise_level > 0 and 
            self.current_exercise_level <= len(self.exercise_level_images) and 
            self.exercise_level_images[self.current_exercise_level - 1]):
            
            level_image = self.exercise_level_images[self.current_exercise_level - 1]
            level_rect = level_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(level_image, level_rect)
            
            # Set up clickable top right area for mechanics (10% width, 20% height)
            self.top_right_area = pygame.Rect(level_rect.x + level_rect.width * 0.9, level_rect.y, level_rect.width * 0.1, level_rect.height * 0.2)
        else:
            # Fallback if level image not found
            title = self.font_large.render(f"LEVEL {self.current_exercise_level}", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(title, title_rect)
            self.top_right_area = None
        
        # Draw exercise input boxes
        self.draw_exercise_inputs()
        
        # Instructions for navigation - moved to footer
        instruction_text = "Click inputs to type, TAB to switch, ENTER to submit, ESC to go back"
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_exercise_inputs(self):
        """Draw the 3 text input boxes for exercises"""
        # Input box dimensions
        input_width = 200
        input_height = 50
        input_spacing = 20
        total_width = (input_width * 3) + (input_spacing * 2)
        
        # Starting position (centered horizontally, positioned near bottom)
        start_x = (self.screen_width - total_width) // 2
        start_y = self.screen_height - 150
        
        # Draw semi-transparent background overlay for inputs area
        overlay_height = input_height + 40
        overlay = pygame.Surface((self.screen_width, overlay_height))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, start_y - 20))
        
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
        
        if map_to_display is not None:
            # Scale the map image to fit the screen while maintaining aspect ratio
            scaled_map = self.scale_photo_to_fit(map_to_display)
            map_rect = scaled_map.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(scaled_map, map_rect)
            
            # Set up top right area for mechanics access
            map_rect = scaled_map.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.top_right_area = pygame.Rect(map_rect.x + map_rect.width * 0.9, map_rect.y, map_rect.width * 0.1, map_rect.height * 0.2)
        else:
            # Fallback if map image not found
            title = self.font_large.render("Map Image Not Found", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(title, title_rect)
            self.top_right_area = None
        
        # Draw progress bar
        self.draw_progress_bar()
        
        # Dynamic instructions based on progress and state
        completed_count = len(self.completed_levels)
        total_sublevels = self.total_levels * self.sublevels_per_level
        if completed_count == 0:
            instruction_text = "Press 1-0 to select levels, ESC to go back, click top right for mechanics"
        elif completed_count < total_sublevels:
            instruction_text = f"Press 1-0 to select levels ({completed_count}/{total_sublevels} sublevels completed), ESC to go back, click top right for mechanics"
        else:
            instruction_text = "All sublevels completed! Press 1-0 to replay, ESC to go back, click top right for mechanics"
        
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        
        # Add subtle background behind instructions for better readability
        bg_padding = 8
        inst_bg_rect = pygame.Rect(instruction_rect.x - bg_padding, instruction_rect.y - bg_padding, 
                                  instruction_rect.width + 2 * bg_padding, instruction_rect.height + 2 * bg_padding)
        inst_bg_surface = pygame.Surface((inst_bg_rect.width, inst_bg_rect.height), pygame.SRCALPHA)
        inst_bg_surface.fill((0, 0, 0, 120))  # Semi-transparent black background
        self.screen.blit(inst_bg_surface, (inst_bg_rect.x, inst_bg_rect.y))
        
        self.screen.blit(instruction, instruction_rect)
    
    def draw_progress_bar(self):
        """Draw a progress bar showing completed levels"""
        # Responsive progress bar dimensions
        bar_width = min(self.screen_width * 0.7, 800)  # Max 70% width, capped at 800px
        bar_height = max(15, self.screen_height // 50)  # Minimum 15px, scales with screen
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = self.screen_height - 80  # Position at footer (above instructions)
        
        # Calculate progress (now based on sublevels)
        total_sublevels = self.total_levels * self.sublevels_per_level
        completed_count = len(self.completed_levels)
        progress = completed_count / total_sublevels if total_sublevels > 0 else 0
        
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
        
        # Draw progress text with dynamic content
        if completed_count == 0:
            progress_text = "Start your adventure! Complete sublevels to track progress"
        elif completed_count < total_sublevels:
            remaining = total_sublevels - completed_count
            progress_text = f"Progress: {completed_count}/{total_sublevels} sublevels completed ({remaining} remaining)"
        else:
            progress_text = f"🎉 Congratulations! All {total_sublevels} sublevels completed! 🎉"
        
        # Render text with subtle background for better readability
        text_surface = self.font_small.render(progress_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, bar_y + bar_height + 10))
        
        # Add subtle background behind text for better readability
        bg_padding = 5
        text_bg_rect = pygame.Rect(text_rect.x - bg_padding, text_rect.y - bg_padding, 
                                  text_rect.width + 2 * bg_padding, text_rect.height + 2 * bg_padding)
        text_bg_surface = pygame.Surface((text_bg_rect.width, text_bg_rect.height), pygame.SRCALPHA)
        text_bg_surface.fill((0, 0, 0, 100))  # Semi-transparent black background
        self.screen.blit(text_bg_surface, (text_bg_rect.x, text_bg_rect.y))
        
        self.screen.blit(text_surface, text_rect)
    
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
                page_rect = page_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
                self.screen.blit(page_surface, page_rect)
        
        # Instructions for navigation - moved to footer
        instruction_text = "Use LEFT/RIGHT arrows to navigate, ESC to go back"
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        self.screen.blit(instruction, instruction_rect)
    
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
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        self.screen.blit(instruction, instruction_rect)
    
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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if clicked on top right area for mechanics
                if self.top_right_area and self.top_right_area.collidepoint(mouse_pos):
                    self.current_state = "mechanics"
                else:
                    # Check if clicked on any input box to select it
                    input_width = 200
                    input_height = 50
                    input_spacing = 20
                    total_width = (input_width * 3) + (input_spacing * 2)
                    start_x = (self.screen_width - total_width) // 2
                    start_y = self.screen_height - 150
                    
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
            # Show wrong reward if not all filled
            self.previous_state_before_reward = "exercise_level"
            self.showing_reward = True
            self.reward_type = 'wrong'
            self.reward_start_time = pygame.time.get_ticks()
            self.current_state = "level_reward"
            self.play_reward_audio('wrong')
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
            # Level not in answer keys - treat as correct if all filled
            self.previous_state_before_reward = "exercise_level"
            self.showing_reward = True
            self.reward_type = 'correct'
            self.reward_start_time = pygame.time.get_ticks()
            self.current_state = "level_reward"
            self.play_reward_audio('correct')
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
        
        # Show appropriate reward
        self.previous_state_before_reward = "exercise_level"
        self.showing_reward = True
        if is_correct:
            self.reward_type = 'correct'
            self.play_reward_audio('correct')
            print(f"Exercise answers correct for level {self.current_exercise_level}: {self.exercise_inputs}")
        else:
            self.reward_type = 'wrong'
            self.play_reward_audio('wrong')
            print(f"Exercise answers wrong for level {self.current_exercise_level}. Expected: {expected_answers}, Got: {self.exercise_inputs}")
        
        self.reward_start_time = pygame.time.get_ticks()
        self.current_state = "level_reward"
    
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
                return False  # Quit game
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
        title = self.font_large.render("Photo Slideshow Game", True, WHITE)
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
                return False  # Quit game
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
        
        # Template structure for level questions
        level_path = resource_path(f"assets/photos/LEVEL {sublevel_string}")
        
        # Define answers for Level 1 sublevels based on file names
        level_1_answers = {
            '1.1': {
                '23.jpg': {'answer': None, 'is_scenario': True, 'needs_text_input': False},  # Just a photo, no answer needed
                '24.jpg': {'answer': 'B', 'is_scenario': False, 'needs_text_input': False},
                '27.jpg': {'answer': 'D', 'is_scenario': False, 'needs_text_input': False},
                '28.jpg': {'answer': 'A', 'is_scenario': False, 'needs_text_input': False},
                '29.jpg': {'answer': 'A', 'is_scenario': False, 'needs_text_input': False},
                '30.jpg': {'answer': '9', 'is_scenario': False, 'needs_text_input': True},  # Text input problem
                '32.jpg': {'answer': 'D', 'is_scenario': False, 'needs_text_input': False},
            },
            '1.2': {
                '36.jpg': {'answer': 'A', 'is_scenario': True, 'needs_text_input': False},
                '37.jpg': {'answer': 'A', 'is_scenario': False, 'needs_text_input': False},
                '40.jpg': {'answer': 'C', 'is_scenario': False, 'needs_text_input': False},
                '41.jpg': {'answer': 'A', 'is_scenario': False, 'needs_text_input': False},
                '42.jpg': {'answer': 'B', 'is_scenario': False, 'needs_text_input': False},
                '43.jpg': {'answer': '7', 'is_scenario': False, 'needs_text_input': True},  # Text input problem
                '45.jpg': {'answer': 'B', 'is_scenario': False, 'needs_text_input': False},
            },
            '1.3': {
                '46.jpg': {'answer': 'A', 'is_scenario': True, 'needs_text_input': False},
                '47.jpg': {'answer': 'D', 'is_scenario': False, 'needs_text_input': False},
                '50.jpg': {'answer': 'D', 'is_scenario': False, 'needs_text_input': False},
                '51.jpg': {'answer': 'B', 'is_scenario': False, 'needs_text_input': False},
                '52.jpg': {'answer': 'C', 'is_scenario': False, 'needs_text_input': False},
                '54.jpg': {'answer': '9', 'is_scenario': False, 'needs_text_input': True},  # Text input problem
                '56.jpg': {'answer': 'C', 'is_scenario': False, 'needs_text_input': False},
            },
        }
        
        if os.path.exists(level_path):
            # Load question images from the level directory
            question_files = []
            for file in os.listdir(level_path):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    question_files.append(file)
            
            question_files.sort()  # Sort to ensure consistent order
            
            for i, question_file in enumerate(question_files):
                question_data = {
                    'image_path': os.path.join(level_path, question_file),
                    'question_number': i + 1,
                    'correct_answer': 1,  # Default correct answer (A=1, B=2, C=3, D=4)
                    'audio_path': None,   # Will be set if audio file exists
                    'image': None,        # Will be loaded when needed
                    'is_scenario': False,
                    'needs_text_input': False
                }
                
                # Look for corresponding audio file
                # Priority: 1. VOICE OVER directory, 2. Level directory, 3. Background music
                # Parse main level number first (needed for special cases)
                main_level = int(sublevel_string.split('.')[0])
                audio_file_name = question_file.rsplit('.', 1)[0] + '.mp3'  # e.g., "22.mp3", "23.mp3"
                audio_path = None
                
                # First, check VOICE OVER directory
                voice_over_path = resource_path(f"assets/audio/VOICE OVER/{audio_file_name}")
                if os.path.exists(voice_over_path):
                    audio_path = voice_over_path
                    print(f"Found voice over for {question_file}: {audio_file_name}")
                else:
                    # Second, check level directory (for special cases like lvl 1.mp3)
                    if question_file == '22.jpg' and main_level == 1:
                        # Special case for 22.jpg - use lvl 1.mp3 in level directory
                        level_audio_file = 'lvl 1.mp3'
                        level_audio_path = os.path.join(level_path, level_audio_file)
                        if os.path.exists(level_audio_path):
                            audio_path = resource_path(level_audio_path)
                            print(f"Found level audio for {question_file}: {level_audio_file}")
                    else:
                        # Check for audio file matching image name in level directory
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
                
                # Set correct answers based on level
                # Apply Level 1 answers to specific sublevels (1.1, 1.2, 1.3)
                if main_level == 1 and sublevel_string in level_1_answers:
                    sublevel_answers = level_1_answers[sublevel_string]
                    if question_file in sublevel_answers:
                        answer_info = sublevel_answers[question_file]
                        
                        # Set scenario flag
                        question_data['is_scenario'] = answer_info['is_scenario']
                        question_data['needs_text_input'] = answer_info['needs_text_input']
                        
                        # Handle answer - could be letter (A-D) or text input value
                        answer_value = answer_info['answer']
                        if answer_value and not question_data['needs_text_input']:
                            # Convert letter answer to number (A=1, B=2, C=3, D=4)
                            if answer_value in ['A', 'B', 'C', 'D']:
                                question_data['correct_answer'] = ord(answer_value) - ord('A') + 1
                            else:
                                question_data['correct_answer'] = 1  # Default
                        elif question_data['needs_text_input']:
                            # Store expected text answer for text input questions
                            question_data['correct_answer'] = answer_value  # Store as string (e.g., '9', '7')
                        else:
                            question_data['correct_answer'] = None
                    else:
                        # Image not in answer key - check if it's a scenario or default
                        # Check if filename suggests scenario (common pattern)
                        if '22.jpg' in question_file.lower() or '21.jpg' in question_file.lower():
                            question_data['is_scenario'] = True
                            question_data['correct_answer'] = None
                        else:
                            question_data['correct_answer'] = (i % 4) + 1
                else:
                    # Default for other levels
                    question_data['correct_answer'] = (i % 4) + 1
                
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
        
        # Play reward audio
        self.play_reward_audio(reward_type)
    
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
            self.mission_complete_sequence_index = 0  # Start with stars.gif
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
                # Check if we came from exercise level
                if hasattr(self, 'previous_state_before_reward') and self.previous_state_before_reward == "exercise_level":
                    # Return to exercise level and reset inputs
                    self.current_state = "exercise_level"
                    if self.reward_type == 'correct':
                        # Clear inputs on correct answer
                        self.exercise_inputs = ["", "", ""]
                        self.exercise_active_input = 0
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
                # Check if we came from exercise level
                if hasattr(self, 'previous_state_before_reward') and self.previous_state_before_reward == "exercise_level":
                    # Return to exercise level and reset inputs
                    self.current_state = "exercise_level"
                    if self.reward_type == 'correct':
                        # Clear inputs on correct answer
                        self.exercise_inputs = ["", "", ""]
                        self.exercise_active_input = 0
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
            
            if question_data['image']:
                # Scale and display question image
                scaled_question = self.scale_photo_to_fit(question_data['image'])
                question_rect = scaled_question.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(scaled_question, question_rect)
        else:
            # No more questions
            title = self.font_large.render("Level Complete!", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(title, title_rect)
        
        # Draw text input box if active
        if self.text_input_active:
            self.draw_text_input_box()
        
        # Instructions for navigation - moved to footer
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
        
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        self.screen.blit(instruction, instruction_rect)
    
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
    
    def draw_level_reward(self):
        """Draw the level reward screen"""
        self.screen.fill(BLACK)
        
        # Load and display reward gif
        reward_path = None
        if self.reward_type == 'correct':
            reward_path = "videos/REWARD/CORRECT.gif"
        elif self.reward_type == 'wrong':
            reward_path = "videos/REWARD/WRONG.gif"
        elif self.reward_type == 'stars':
            reward_path = "videos/REWARD/stars.gif"
        
        if reward_path and os.path.exists(reward_path):
            try:
                # Try to load the GIF file
                reward_image = pygame.image.load(reward_path)
                
                # Scale the image to fit the screen while maintaining aspect ratio
                image_width, image_height = reward_image.get_size()
                screen_ratio = self.screen_width / self.screen_height
                image_ratio = image_width / image_height
                
                if image_ratio > screen_ratio:
                    # Image is wider than screen
                    new_width = self.screen_width
                    new_height = int(self.screen_width / image_ratio)
                else:
                    # Image is taller than screen
                    new_height = self.screen_height
                    new_width = int(self.screen_height * image_ratio)
                
                # Scale the image
                scaled_reward = pygame.transform.scale(reward_image, (new_width, new_height))
                
                # Center the image on screen
                reward_rect = scaled_reward.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(scaled_reward, reward_rect)
                
                print(f"Successfully loaded reward GIF: {reward_path}")
            except Exception as e:
                print(f"Error loading reward GIF: {e}")
                # Fallback to text
                reward_text = self.reward_type.upper()
                if self.reward_type == 'stars':
                    reward_text = "STARS! PERFECT SCORE!"
                
                reward_surface = self.font_large.render(reward_text, True, WHITE)
                reward_rect = reward_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(reward_surface, reward_rect)
        else:
            # Fallback text if GIF not found
            reward_text = self.reward_type.upper()
            if self.reward_type == 'stars':
                reward_text = "STARS! PERFECT SCORE!"
            
            reward_surface = self.font_large.render(reward_text, True, WHITE)
            reward_rect = reward_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(reward_surface, reward_rect)
            
            if reward_path:
                print(f"Reward GIF not found: {reward_path}")
        
        # Instructions for navigation - moved to footer
        instruction_text = "Press SPACE or click to continue"
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_mission_complete(self):
        """Draw the mission complete screen"""
        self.screen.fill(BLACK)
        
        image_path = None
        
        if self.mission_complete_type == 'sublevel':
            # Sublevel completion: show mission complete3.jpg
            image_path = resource_path("assets/photos/MISSION COMPLETE & REWARDS/mission complete3.jpg")
        elif self.mission_complete_type == 'level':
            # Level completion: sequence of 3 screens
            if self.mission_complete_sequence_index == 0:
                # First: stars.gif
                image_path = resource_path("videos/REWARD/stars.gif")
            elif self.mission_complete_sequence_index == 1:
                # Second: MISSION COMPLETE 1.jpg
                image_path = resource_path("assets/photos/MISSION COMPLETE & REWARDS/MISSION COMPLETE 1.jpg")
            elif self.mission_complete_sequence_index == 2:
                # Third: MISSION COMPLETE 2.jpg
                image_path = resource_path("assets/photos/MISSION COMPLETE & REWARDS/MISSION COMPLETE 2.jpg")
        
        if image_path and os.path.exists(image_path):
            try:
                # Try to load the image/GIF
                mission_image = pygame.image.load(image_path)
                
                # Scale the image to fit the screen while maintaining aspect ratio
                scaled_image = self.scale_photo_to_fit(mission_image)
                image_rect = scaled_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(scaled_image, image_rect)
                
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
        else:
            # Fallback text if image not found
            fallback_text = "Mission Complete!"
            if image_path:
                print(f"Mission complete image not found: {image_path}")
            
            text_surface = self.font_large.render(fallback_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(text_surface, text_rect)
        
        # Instructions for navigation
        instruction_text = "Press SPACE or click to continue"
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        self.screen.blit(instruction, instruction_rect)
    
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
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        self.screen.blit(instruction, instruction_rect)
    
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
        
        # Load intro image (5.png)
        intro_path = resource_path("assets/photos/intro/5.png")
        if os.path.exists(intro_path):
            try:
                intro_image = pygame.image.load(intro_path)
                self.intro_image = self.scale_photo_to_fit(intro_image)
                print(f"Loaded intro image: {intro_path}")
            except pygame.error as e:
                print(f"Error loading intro image: {e}")
                self.intro_image = None
        else:
            print(f"Intro image not found at {intro_path}")
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
        
        if self.intro_image:
            intro_rect = self.intro_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(self.intro_image, intro_rect)
        
        instruction_text = "Press any key or click to start Level 1"
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        self.screen.blit(instruction, instruction_rect)
    
    def handle_intro_new_game_input(self, event):
        """Handle input in intro new game state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self.toggle_fullscreen()
            else:
                # Start with sublevel 1.1
                self.start_level("1.1")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.start_level(1)
        return True

if __name__ == "__main__":
    game = PhotoSlideshowGame()
    game.run()