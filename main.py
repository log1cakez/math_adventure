import pygame
import os
import sys
from typing import List, Dict, Optional

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
    from moviepy.editor import VideoFileClip
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
        
        # Drawing functionality
        self.drawing_enabled = True
        self.drawing_surface = None
        self.drawing_color = (255, 0, 0)  # Red color
        self.drawing_thickness = 3
        self.last_mouse_pos = None
        self.is_drawing = False
        
        # Photo management
        self.current_photos = []
        self.photo_objects = []
        
        # Splash screen
        self.splash_image = self.load_splash_image()
        self.second_page_image = self.load_second_page_image()
        self.select_image = self.load_select_image()
        self.exercise_level_images = self.load_exercise_level_images()
        self.mechanics_images = self.load_mechanics_images()
        self.map_image = self.load_map_image()
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
        
        # Progress tracking
        self.completed_levels = set()  # Track which levels have been completed
        self.total_levels = 10  # Total number of levels (1-10)
        
        # Text input for problem solving questions
        self.text_input_active = False
        self.text_input_value = ""
        self.text_input_cursor_blink = 0
        self.text_input_rect = pygame.Rect(0, 0, 400, 60)
        
        # New game intro sequence
        self.intro_image = None
        
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
    
    def load_splash_image(self) -> Optional[pygame.Surface]:
        """Load the splash screen image"""
        splash_path = resource_path("assets/photos/FIRST PAGE.png")
        try:
            if os.path.exists(splash_path):
                splash = pygame.image.load(splash_path)
                # Scale splash image to fit screen while maintaining aspect ratio
                splash = self.scale_photo_to_fit(splash)
                return splash
            else:
                print(f"Splash image not found at {splash_path}")
                return None
        except pygame.error as e:
            print(f"Error loading splash image: {e}")
            return None
    
    def load_second_page_image(self) -> Optional[pygame.Surface]:
        """Load the second page image"""
        second_page_path = resource_path("assets/photos/FIRST PAGE (2).png")
        try:
            if os.path.exists(second_page_path):
                second_page = pygame.image.load(second_page_path)
                # Scale second page image to fit screen while maintaining aspect ratio
                second_page = self.scale_photo_to_fit(second_page)
                return second_page
            else:
                print(f"Second page image not found at {second_page_path}")
                return None
        except pygame.error as e:
            print(f"Error loading second page image: {e}")
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
            level_path = resource_path(f"assets/photos/EXERCISES/LEVEL {i}.png")
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
        """Load the map image"""
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
        """Draw the splash screen"""
        self.screen.fill(BLACK)
        
        if self.splash_image:
            # Display the splash image centered
            splash_rect = self.splash_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(self.splash_image, splash_rect)
            
            # Set up clickable gear area - positioned on the gear icon in top right
            # The gear is in the top right corner of the image
            gear_x = splash_rect.x + splash_rect.width * 0.85  # 85% from left (top right area)
            gear_y = splash_rect.y + splash_rect.height * 0.1  # 10% from top (very top)
            gear_size = 60  # Clickable area size for the gear
            self.gear_area = pygame.Rect(gear_x, gear_y, gear_size, gear_size)
        else:
            # Fallback if splash image not found
            title = self.font_large.render("Photo Slideshow Game", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
            self.screen.blit(title, title_rect)
        
        # Instructions to proceed - moved to footer
        instruction_text = "Click anywhere to continue, or click gear for mechanics..."
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_second_page(self):
        """Draw the second page"""
        self.screen.fill(BLACK)
        
        if self.second_page_image:
            # Display the second page image centered
            second_page_rect = self.second_page_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(self.second_page_image, second_page_rect)
            
            # Set up clickable top right area for mechanics (10% width, 20% height)
            self.top_right_area = pygame.Rect(second_page_rect.x + second_page_rect.width * 0.9, second_page_rect.y, second_page_rect.width * 0.1, second_page_rect.height * 0.2)
        else:
            # Fallback if second page image not found
            title = self.font_large.render("FIRST PAGE (2)", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(title, title_rect)
            self.top_right_area = None
        
        # Instructions for the three options - moved to footer
        instruction_text = "Press 1 for Exercises, 2 for Map, 3 for New Game, click top right for mechanics"
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
            
            # Initialize drawing surface if not exists or if level changed
            if self.drawing_surface is None or self.drawing_surface.get_size() != level_rect.size:
                self.drawing_surface = pygame.Surface(level_rect.size, pygame.SRCALPHA)
                self.drawing_surface.fill((0, 0, 0, 0))  # Transparent background
            
            # Draw the drawing surface on top of the level image
            self.screen.blit(self.drawing_surface, level_rect)
            
            # Set up clickable top right area for mechanics (10% width, 20% height)
            self.top_right_area = pygame.Rect(level_rect.x + level_rect.width * 0.9, level_rect.y, level_rect.width * 0.1, level_rect.height * 0.2)
        else:
            # Fallback if level image not found
            title = self.font_large.render(f"LEVEL {self.current_exercise_level}", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(title, title_rect)
            self.top_right_area = None
            self.drawing_surface = None
        
        # Instructions for drawing and navigation - moved to footer
        instruction_text = "Draw with mouse, C to clear, 1-5 for colors, ESC to go back, click top right for mechanics"
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        self.screen.blit(instruction, instruction_rect)
        
        # Show current drawing color - optimized for laptops
        color_text = f"Color: {self.drawing_color}"
        color_surface = self.font_small.render(color_text, True, self.drawing_color)
        color_rect = color_surface.get_rect()
        color_rect.topleft = (max(20, self.screen_width // 40), max(20, self.screen_height // 40))
        self.screen.blit(color_surface, color_rect)
    
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
        
        if self.map_image is not None:
            # Scale the map image to fit the screen while maintaining aspect ratio
            scaled_map = self.scale_photo_to_fit(self.map_image)
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
        if completed_count == 0:
            instruction_text = "Press 1-0 to start levels, ESC to go back, click top right for mechanics"
        elif completed_count < self.total_levels:
            instruction_text = f"Press 1-0 for levels ({completed_count}/{self.total_levels} completed), ESC to go back, click top right for mechanics"
        else:
            instruction_text = "All levels completed! Press 1-0 to replay, ESC to go back, click top right for mechanics"
        
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
        
        # Calculate progress
        completed_count = len(self.completed_levels)
        progress = completed_count / self.total_levels if self.total_levels > 0 else 0
        
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
            progress_text = "Start your adventure! Complete levels to track progress"
        elif completed_count < self.total_levels:
            remaining = self.total_levels - completed_count
            progress_text = f"Progress: {completed_count}/{self.total_levels} levels completed ({remaining} remaining)"
        else:
            progress_text = f"🎉 Congratulations! All {self.total_levels} levels completed! 🎉"
        
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
                # Go to exercises (SELECT.png)
                self.current_state = "select"
            elif event.key == pygame.K_2:
                # Go to map image
                self.current_state = "map_image"
            elif event.key == pygame.K_3:
                # Start new game with intro sequence
                self.start_new_game()
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
            elif event.key == pygame.K_c:
                # Clear drawing
                if self.drawing_surface:
                    self.drawing_surface.fill((0, 0, 0, 0))
            elif event.key == pygame.K_1:
                self.drawing_color = RED
            elif event.key == pygame.K_2:
                self.drawing_color = GREEN
            elif event.key == pygame.K_3:
                self.drawing_color = BLUE
            elif event.key == pygame.K_4:
                self.drawing_color = (255, 255, 0)  # Yellow
            elif event.key == pygame.K_5:
                self.drawing_color = WHITE
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if clicked on top right area for mechanics
                if self.top_right_area and self.top_right_area.collidepoint(mouse_pos):
                    self.current_state = "mechanics"
                else:
                    # Start drawing
                    self.is_drawing = True
                    self.last_mouse_pos = mouse_pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.is_drawing = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_drawing and self.drawing_surface:
                current_pos = pygame.mouse.get_pos()
                if self.last_mouse_pos:
                    # Draw line on drawing surface
                    pygame.draw.line(self.drawing_surface, self.drawing_color, 
                                  self.last_mouse_pos, current_pos, self.drawing_thickness)
                self.last_mouse_pos = current_pos
        return True
    
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
                # Start level 1
                self.start_level(1)
            elif event.key == pygame.K_2:
                # Start level 2
                self.start_level(2)
            elif event.key == pygame.K_3:
                # Start level 3
                self.start_level(3)
            elif event.key == pygame.K_4:
                # Start level 4
                self.start_level(4)
            elif event.key == pygame.K_5:
                # Start level 5
                self.start_level(5)
            elif event.key == pygame.K_6:
                # Start level 6
                self.start_level(6)
            elif event.key == pygame.K_7:
                # Start level 7
                self.start_level(7)
            elif event.key == pygame.K_8:
                # Start level 8
                self.start_level(8)
            elif event.key == pygame.K_9:
                # Start level 9
                self.start_level(9)
            elif event.key == pygame.K_0:
                # Start level 10
                self.start_level(10)
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
                
                # Also check if clicked in the top-right area of the image
                if self.splash_image:
                    splash_rect = self.splash_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                    top_right_area = pygame.Rect(splash_rect.x + splash_rect.width * 0.9, splash_rect.y, splash_rect.width * 0.1, splash_rect.height * 0.2)
                    top_right_clicked = top_right_area.collidepoint(mouse_pos)
                
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
                # Go to exercises (SELECT.png)
                self.current_state = "select"
            elif event.key == pygame.K_2:
                # Go to map image
                self.current_state = "map_image"
            elif event.key == pygame.K_3:
                # Start new game with intro sequence
                self.start_new_game()
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
    
    def handle_exercise_level_input(self, event):
        """Handle input in exercise level state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                # Go back to select screen
                self.current_state = "select"
            elif event.key == pygame.K_c:
                # Clear drawing
                if self.drawing_surface:
                    self.drawing_surface.fill((0, 0, 0, 0))
            elif event.key == pygame.K_1:
                # Red color
                self.drawing_color = (255, 0, 0)
            elif event.key == pygame.K_2:
                # Green color
                self.drawing_color = (0, 255, 0)
            elif event.key == pygame.K_3:
                # Blue color
                self.drawing_color = (0, 0, 255)
            elif event.key == pygame.K_4:
                # Yellow color
                self.drawing_color = (255, 255, 0)
            elif event.key == pygame.K_5:
                # Black color
                self.drawing_color = (0, 0, 0)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                
                top_right_clicked = self.top_right_area and self.top_right_area.collidepoint(mouse_pos)
                if top_right_clicked:
                    self.current_state = "mechanics"
                else:
                    # Start drawing
                    self.is_drawing = True
                    self.last_mouse_pos = mouse_pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.is_drawing = False
                self.last_mouse_pos = None
        elif event.type == pygame.MOUSEMOTION:
            if self.is_drawing and self.drawing_surface and self.last_mouse_pos:
                current_pos = pygame.mouse.get_pos()
                
                # Convert screen coordinates to drawing surface coordinates
                if (self.current_exercise_level > 0 and 
                    self.current_exercise_level <= len(self.exercise_level_images) and 
                    self.exercise_level_images[self.current_exercise_level - 1]):
                    
                    level_image = self.exercise_level_images[self.current_exercise_level - 1]
                    level_rect = level_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                    
                    # Check if mouse is within the level image area
                    if level_rect.collidepoint(current_pos):
                        # Convert to drawing surface coordinates
                        draw_pos = (current_pos[0] - level_rect.x, current_pos[1] - level_rect.y)
                        last_draw_pos = (self.last_mouse_pos[0] - level_rect.x, self.last_mouse_pos[1] - level_rect.y)
                        
                        # Draw line on the drawing surface
                        pygame.draw.line(self.drawing_surface, self.drawing_color, last_draw_pos, draw_pos, self.drawing_thickness)
                        
                        self.last_mouse_pos = current_pos
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
                    self.map_video_clip.audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
                    
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
        
        # Reset drawing surface to None so it gets recreated with new size
        self.drawing_surface = None
    
    def start_level(self, level_number):
        """Start a specific level"""
        self.current_level_number = level_number
        self.current_question_index = 0
        self.correct_answers = 0
        self.showing_reward = False
        
        # Load level questions
        self.load_level_questions(level_number)
        
        if self.level_questions:
            self.total_questions = len(self.level_questions)
            self.current_state = "level_question"
            # Play audio for first question if available
            self.play_question_audio()
        else:
            print(f"No questions found for level {level_number}")
    
    def load_level_questions(self, level_number):
        """Load questions for a specific level"""
        self.level_questions = []
        
        # Template structure for level questions
        level_path = resource_path(f"assets/photos/LEVEL {level_number}")
        
        # Define answers for Level 1 based on file names
        level_1_answers = {
            '21.jpg': {'answer': None, 'is_scenario': True, 'needs_text_input': False},
            '22.jpg': {'answer': None, 'is_scenario': True, 'needs_text_input': False},
            '23.jpg': {'answer': 'B', 'is_scenario': False, 'needs_text_input': False},  # Answer B
            '26.jpg': {'answer': 'D', 'is_scenario': False, 'needs_text_input': False},  # Answer D
            '29.jpg': {'answer': 'A', 'is_scenario': False, 'needs_text_input': False},  # Answer A
            '32.jpg': {'answer': 'A', 'is_scenario': False, 'needs_text_input': False},  # Answer A
            '35.jpg': {'answer': None, 'is_scenario': False, 'needs_text_input': True},  # Text input problem
            '39.jpg': {'answer': 'D', 'is_scenario': False, 'needs_text_input': False},  # Answer D
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
                # Special case for 22.jpg - use lvl 1.mp3
                if question_file == '22.jpg' and level_number == 1:
                    audio_file = 'lvl 1.mp3'
                    audio_path = os.path.join(level_path, audio_file)
                else:
                    audio_file = question_file.rsplit('.', 1)[0] + '.mp3'
                    audio_path = os.path.join(level_path, audio_file)
                
                # Check if specific audio file exists
                if os.path.exists(audio_path):
                    question_data['audio_path'] = resource_path(audio_path)
                else:
                    # Use background music as fallback if no specific audio assigned
                    background_music_path = resource_path("assets/audio/BACKGROUND MUSIC/BACKGROUND MUSIC.mp3")
                    if os.path.exists(background_music_path):
                        question_data['audio_path'] = background_music_path
                        print(f"No audio found for {question_file}, using background music")
                    else:
                        question_data['audio_path'] = None
                
                # Set correct answers based on level
                if level_number == 1 and question_file in level_1_answers:
                    answer_info = level_1_answers[question_file]
                    
                    # Set scenario flag
                    question_data['is_scenario'] = answer_info['is_scenario']
                    question_data['needs_text_input'] = answer_info['needs_text_input']
                    
                    # Convert letter answer to number (A=1, B=2, C=3, D=4)
                    answer_letter = answer_info['answer']
                    if answer_letter:
                        question_data['correct_answer'] = ord(answer_letter) - ord('A') + 1
                    else:
                        question_data['correct_answer'] = None
                else:
                    # Default for other levels
                    question_data['correct_answer'] = (i % 4) + 1
                
                self.level_questions.append(question_data)
        
        print(f"Loaded {len(self.level_questions)} questions for level {level_number}")
    
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
        # For problem 35, we'll accept any non-empty numeric answer for now
        # You can modify this to check specific answer
        if self.text_input_value.strip():
            # Text input was provided, treat as correct for now
            # You can add specific answer checking here
            self.text_input_active = False
            answer_to_check = self.text_input_value.strip()
            
            # For now, we'll just move to next question
            # You can add validation here if you have a specific expected answer
            self.text_input_value = ""
            
            # Mark as correct and show reward
            self.correct_answers += 1
            self.show_reward('correct')
            
            # Move to next question - this will happen when reward is dismissed
            self.current_question_index += 1
    
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
                # All questions completed
                self.completed_levels.add(self.current_level_number)
                if self.correct_answers == self.total_questions:
                    self.show_reward('stars')
                else:
                    # Level completed but not perfect
                    self.current_state = "map_image"
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
                if self.current_question_index >= len(self.level_questions):
                    # Level completed
                    self.completed_levels.add(self.current_level_number)
                    if self.correct_answers == self.total_questions:
                        # Perfect score - show stars
                        self.show_reward('stars')
                    else:
                        # Level completed but not perfect
                        self.current_state = "map_image"
                else:
                    # Continue to next question
                    self.current_state = "level_question"
                    self.play_question_audio()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Continue after reward
                self.showing_reward = False
                if self.current_question_index >= len(self.level_questions):
                    # Level completed
                    self.completed_levels.add(self.current_level_number)
                    if self.correct_answers == self.total_questions:
                        # Perfect score - show stars
                        self.show_reward('stars')
                    else:
                        # Level completed but not perfect
                        self.current_state = "map_image"
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
        
        # Reset drawing surface to None so it gets recreated with new size
        self.drawing_surface = None
        
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
                self.start_level(1)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.start_level(1)
        return True

if __name__ == "__main__":
    game = PhotoSlideshowGame()
    game.run()