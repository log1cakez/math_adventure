import pygame
import os
import sys
from typing import List, Dict, Optional
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
        # Initialize in fullscreen mode
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.screen.get_size()
        pygame.display.set_caption("Photo Slideshow Game")
        self.clock = pygame.time.Clock()
        
        # Scale fonts based on screen size
        base_font_size = min(self.screen_width, self.screen_height) // 25
        self.font_large = pygame.font.Font(None, int(base_font_size * 1.5))
        self.font_medium = pygame.font.Font(None, int(base_font_size))
        self.font_small = pygame.font.Font(None, int(base_font_size * 0.75))
        
        # Game state
        self.current_state = "splash"  # splash, menu, intro, map, slideshow, level_select, mechanics
        self.current_level = 0
        self.current_photo_index = 0
        self.levels = self.load_levels()
        
        # Photo management
        self.current_photos = []
        self.photo_objects = []
        
        # Splash screen
        self.splash_image = self.load_splash_image()
        self.mechanics_images = self.load_mechanics_images()
        self.current_mechanics_index = 0
        
        # Intro sequence
        self.intro_images = self.load_intro_images()
        self.intro_audio_files = self.load_intro_audio_files()
        self.current_intro_index = 0
        
        # Map video
        self.map_video_path = "assets/photos/level_1/LEVEL 1.1/MAP 1 (VID).mp4"
        self.map_video_playing = False
        self.map_video_surface = None
        self.map_video_clip = None
        self.map_video_start_time = 0
        
        # Try to load a static map image as fallback
        self.map_image_path = "assets/photos/level_1/LEVEL 1.1/MAP 1.png"
        self.map_image = None
        if os.path.exists(self.map_image_path):
            try:
                self.map_image = pygame.image.load(self.map_image_path)
                print(f"Loaded map image: {self.map_image_path}")
            except:
                self.map_image = None
        
        # Check if map video exists
        if not os.path.exists(self.map_video_path):
            print(f"WARNING: Map video not found at: {self.map_video_path}")
            # Try alternative paths
            alternative_paths = [
                "assets/photos/LEVEL 1.1/MAP 1 (VID).mp4",
                "assets/photos/level_1/LEVEL 1.1/MAP 1 (VID).mp4",
                "assets/photos/level_1/LEVEL 1.1/MAP 1 (VID).mp4"
            ]
            for alt_path in alternative_paths:
                if os.path.exists(alt_path):
                    self.map_video_path = alt_path
                    print(f"Found map video at: {alt_path}")
                    break
        
        # Audio placeholder
        self.audio_enabled = True
        self.current_audio = None
        
        # Interactive areas (you can adjust these coordinates based on your image)
        self.gear_area = None  # Will be set based on image dimensions
        
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
        splash_path = "assets/photos/FIRST PAGE.jpg"
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
    
    def load_mechanics_images(self) -> List[pygame.Surface]:
        """Load the mechanics images"""
        mechanics_images = []
        mechanics_paths = [
            "assets/photos/mechanics/mechanics_1.png",
            "assets/photos/mechanics/mechanics_2.png"
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
    
    def load_intro_images(self) -> List[pygame.Surface]:
        """Load the intro images"""
        intro_images = []
        intro_paths = [
            "assets/photos/intro/5.png",
            "assets/photos/intro/6.png"
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
            "assets/photos/intro/intro (1) .mp4",
            "assets/photos/intro/intro (2) before showing the map.mp4"
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
        """Scale photo to fit screen while maintaining aspect ratio"""
        photo_width, photo_height = photo.get_size()
        screen_width, screen_height = self.screen_width - 100, self.screen_height - 150  # Leave margin
        
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
            
            # Draw a visible indicator to help debug (yellow rectangle)
            pygame.draw.rect(self.screen, (255, 255, 0), self.gear_area, 3)
            
            # Add multiple clickable areas for testing
            # Top right corner area
            top_right_area = pygame.Rect(splash_rect.x + splash_rect.width * 0.8, splash_rect.y, splash_rect.width * 0.2, splash_rect.height * 0.2)
            pygame.draw.rect(self.screen, (0, 255, 0), top_right_area, 2)  # Green rectangle
            
            # Add debug text
            debug_text = f"Gear area: {self.gear_area}"
            debug_surface = self.font_small.render(debug_text, True, (255, 255, 0))
            self.screen.blit(debug_surface, (10, 10))
            
            debug_text2 = f"Top right area: {top_right_area}"
            debug_surface2 = self.font_small.render(debug_text2, True, (0, 255, 0))
            self.screen.blit(debug_surface2, (10, 30))
        else:
            # Fallback if splash image not found
            title = self.font_large.render("Photo Slideshow Game", True, WHITE)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
            self.screen.blit(title, title_rect)
        
        # Instructions to proceed
        instruction_text = "Click anywhere to start intro, or click gear for mechanics..."
        instruction = self.font_medium.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
        self.screen.blit(instruction, instruction_rect)
        
        # Show Tab instruction
        tab_text = "Press TAB for level selection"
        tab_surface = self.font_small.render(tab_text, True, WHITE)
        tab_rect = tab_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        self.screen.blit(tab_surface, tab_rect)
    
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
        """Draw the map video screen"""
        self.screen.fill(BLACK)
        
        if self.map_video_clip is not None and self.map_video_playing and MOVIEPY_AVAILABLE:
            try:
                # Calculate current time in video
                current_time = (pygame.time.get_ticks() - self.map_video_start_time) / 1000.0
                
                # Check if video is still playing
                if current_time < self.map_video_clip.duration:
                    # Get current frame from video
                    frame = self.map_video_clip.get_frame(current_time)
                    
                    # Convert numpy array to pygame surface
                    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                    
                    # Scale the video to fit the screen while maintaining aspect ratio
                    video_width, video_height = frame_surface.get_size()
                    screen_ratio = self.screen_width / self.screen_height
                    video_ratio = video_width / video_height
                    
                    if video_ratio > screen_ratio:
                        # Video is wider than screen
                        new_width = self.screen_width
                        new_height = int(self.screen_width / video_ratio)
                    else:
                        # Video is taller than screen
                        new_height = self.screen_height
                        new_width = int(self.screen_height * video_ratio)
                    
                    # Scale the video
                    scaled_video = pygame.transform.scale(frame_surface, (new_width, new_height))
                    
                    # Center the video on screen
                    video_rect = scaled_video.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                    self.screen.blit(scaled_video, video_rect)
                else:
                    # Video finished, show last frame and pause
                    # Get the last frame of the video
                    last_frame = self.map_video_clip.get_frame(self.map_video_clip.duration - 0.1)
                    frame_surface = pygame.surfarray.make_surface(last_frame.swapaxes(0, 1))
                    
                    # Scale the video to fit the screen while maintaining aspect ratio
                    video_width, video_height = frame_surface.get_size()
                    screen_ratio = self.screen_width / self.screen_height
                    video_ratio = video_width / video_height
                    
                    if video_ratio > screen_ratio:
                        # Video is wider than screen
                        new_width = self.screen_width
                        new_height = int(self.screen_width / video_ratio)
                    else:
                        # Video is taller than screen
                        new_height = self.screen_height
                        new_width = int(self.screen_height * video_ratio)
                    
                    # Scale the video
                    scaled_video = pygame.transform.scale(frame_surface, (new_width, new_height))
                    
                    # Center the video on screen
                    video_rect = scaled_video.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                    self.screen.blit(scaled_video, video_rect)
                    
                    # Show level selection instructions
                    instruction_text = "Press 1 for Level 1, Press 2 for Level 2, Press 3 for Level 3"
                    instruction = self.font_medium.render(instruction_text, True, WHITE)
                    instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
                    self.screen.blit(instruction, instruction_rect)
                    
            except Exception as e:
                print(f"Error displaying video frame: {e}")
                # Fall back to audio-only mode
                self.draw_map_audio_only()
        else:
            # Fall back to audio-only mode if MoviePy not available
            self.draw_map_audio_only()
    
    def draw_map_audio_only(self):
        """Draw map screen with audio-only playback"""
        self.screen.fill(BLACK)
        
        if os.path.exists(self.map_video_path):
            # Try to show map image if available
            if self.map_image is not None:
                # Scale the map image to fit the screen while maintaining aspect ratio
                image_width, image_height = self.map_image.get_size()
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
                scaled_image = pygame.transform.scale(self.map_image, (new_width, new_height))
                
                # Center the image on screen
                image_rect = scaled_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(scaled_image, image_rect)
            else:
                # Show that audio is playing or paused
                if self.map_video_playing and pygame.mixer.music.get_busy():
                    status_text = "Playing Map Video Audio..."
                elif self.map_video_playing:
                    status_text = "Map Video Audio Paused"
                else:
                    status_text = "Loading Map Video..."
                
                status_surface = self.font_large.render(status_text, True, WHITE)
                status_rect = status_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
                self.screen.blit(status_surface, status_rect)
                
                # Show level selection instructions
                instruction_text = "Press 1 for Level 1, Press 2 for Level 2, Press 3 for Level 3"
                instruction = self.font_medium.render(instruction_text, True, WHITE)
                instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
                self.screen.blit(instruction, instruction_rect)
            
            # Show level selection instructions at bottom
            instruction_text = "Press 1 for Level 1, Press 2 for Level 2, Press 3 for Level 3"
            instruction = self.font_medium.render(instruction_text, True, WHITE)
            instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
            self.screen.blit(instruction, instruction_rect)
        else:
            # Show error message if video file not found
            error_title = self.font_large.render("Map Video Not Found", True, WHITE)
            error_rect = error_title.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
            self.screen.blit(error_title, error_rect)
            
            error_text = f"File not found: {self.map_video_path}"
            error_surface = self.font_medium.render(error_text, True, WHITE)
            error_text_rect = error_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(error_surface, error_text_rect)
    
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
            elif event.key == pygame.K_TAB:
                # Tab pressed - go directly to map video for level selection
                self.start_map_video()
            else:
                # Any other key press starts intro
                self.start_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                print(f"Mouse clicked at: {mouse_pos}")
                print(f"Gear area: {self.gear_area}")
                
                # Check if click is on gear area or in top-right corner
                gear_clicked = self.gear_area and self.gear_area.collidepoint(mouse_pos)
                top_right_clicked = False
                
                # Also check if clicked in the top-right area of the image
                if self.splash_image:
                    splash_rect = self.splash_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                    top_right_area = pygame.Rect(splash_rect.x + splash_rect.width * 0.8, splash_rect.y, splash_rect.width * 0.2, splash_rect.height * 0.2)
                    top_right_clicked = top_right_area.collidepoint(mouse_pos)
                    print(f"Top right area: {top_right_area}")
                    print(f"Top right clicked: {top_right_clicked}")
                
                if gear_clicked or top_right_clicked:
                    print("Gear area clicked! Going to mechanics...")
                    self.current_state = "mechanics"
                else:
                    print("Clicked outside gear area, starting intro...")
                    # Click anywhere else starts intro
                    self.start_game()
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
    
    def cleanup_map_video(self):
        """Clean up video resources"""
        if self.map_video_clip is not None:
            try:
                self.map_video_clip.close()
                self.map_video_clip = None
            except:
                pass
        
        # Clean up temporary audio file
        temp_audio_path = "temp_map_audio.wav"
        if os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
                print("Cleaned up temporary audio file")
            except:
                pass
        
        self.map_video_playing = False
    
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
        """Start the game with default level"""
        self.current_level = 0  # Use first level as default
        self.load_photos_for_level(0)
        self.start_intro_sequence()
    
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
        """Toggle between fullscreen and windowed mode"""
        if self.screen.get_flags() & pygame.FULLSCREEN:
            # Currently fullscreen, switch to windowed
            self.screen = pygame.display.set_mode((1200, 800))
        else:
            # Currently windowed, switch to fullscreen
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        
        # Update screen dimensions
        self.screen_width, self.screen_height = self.screen.get_size()
        
        # Recalculate font sizes
        base_font_size = min(self.screen_width, self.screen_height) // 25
        self.font_large = pygame.font.Font(None, int(base_font_size * 1.5))
        self.font_medium = pygame.font.Font(None, int(base_font_size))
        self.font_small = pygame.font.Font(None, int(base_font_size * 0.75))
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self.current_state == "splash":
                    running = self.handle_splash_input(event)
                elif self.current_state == "intro":
                    running = self.handle_intro_input(event)
                elif self.current_state == "map":
                    running = self.handle_map_input(event)
                elif self.current_state == "mechanics":
                    running = self.handle_mechanics_input(event)
                elif self.current_state == "menu":
                    running = self.handle_menu_input(event)
                elif self.current_state == "slideshow":
                    running = self.handle_slideshow_input(event)
            
            # Draw current state
            if self.current_state == "splash":
                self.draw_splash()
            elif self.current_state == "intro":
                self.draw_intro()
            elif self.current_state == "map":
                self.draw_map()
            elif self.current_state == "mechanics":
                self.draw_mechanics()
            elif self.current_state == "menu":
                self.draw_menu()
            elif self.current_state == "slideshow":
                self.draw_slideshow()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PhotoSlideshowGame()
    game.run()