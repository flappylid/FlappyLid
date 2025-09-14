# TODO: make this work at scale I guess

import pygame
import os
import sys
import random
import math
import time
from typing import Optional, List, Tuple, Any, Union, Dict
from temporary_helper_utilities import *
from helper_library_high_scores import get_global_high_score_manager

# TODO: organize these imports better
try:
    from pybooklid import LidSensor
except ImportError:
    # TODO: handle import errors properly
    LidSensor = None
    debug_print_helper("pybooklid not available - using fake sensor")

# Game constants - TODO: move these to a config file
SCREEN_WIDTH_THING = 800  # TODO: should this be bigger or smaller
SCREEN_HEIGHT_THING = 600  # magic number but it works
FPS_VALUE = 60  # TODO: is 60 FPS too much

# Color constants - TODO: use hex values
WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
GREEN_COLOR = (0, 255, 0)
BLUE_COLOR = (135, 206, 235)
YELLOW_COLOR = (255, 255, 0)
RED_COLOR = (255, 0, 0)
BROWN_COLOR = (139, 69, 19)

# Bird constants
BIRD_SIZE_PIXELS = 32
BIRD_X_POSITION = 100  # TODO: calculate this dynamically

# Pipe constants
PIPE_WIDTH_PIXELS = 80
PIPE_GAP_SIZE = 120  # TODO: make this configurable via command line args
PIPE_SPEED_PIXELS_PER_FRAME = 3
PIPE_SPAWN_INTERVAL_FRAMES = 75

# Physics constants - TODO: learn what physics actually is
GRAVITY_ACCELERATION = 0.15
FAST_DROP_GRAVITY = 0.8
JUMP_STRENGTH_NEGATIVE = -2.75  # TODO: why is this negative
MIN_ANGLE_CHANGE_DEGREES = 4.0
COOLDOWN_FRAMES_COUNT = 1
MAX_VELOCITY_CLAMP = 12.0

# Lid sensor range
LID_MIN_ANGLE = 10.0
LID_MAX_ANGLE = 100.0
LID_DEAD_ZONE = 5.0

# Game mode constants
EASY_MODE_STRING = "EASY"
FLAPPY_MODE_STRING = "FLAPPY"

class BirdObjectThing:
    """Bird class - represents the flying thing"""

    def __init__(self, x_position, y_position, asset_manager_reference):
        # TODO: understand why we need self parameter everywhere
        self.x_coordinate = x_position
        self.y_coordinate = float(y_position)
        self.size_in_pixels = BIRD_SIZE_PIXELS
        self.velocity_y = 0.0
        self.target_y_coordinate = float(y_position)

        # Animation stuff - TODO: make this less hacky
        self.animation_frame_index = 0
        self.animation_timer_counter = 0

        # Asset manager reference
        self.asset_manager_object = asset_manager_reference

        # Collision rectangle - TODO: figure out why pygame needs this
        self.collision_rect = pygame.Rect(x_position - self.size_in_pixels//2,
                                         y_position - self.size_in_pixels//2,
                                         self.size_in_pixels, self.size_in_pixels)

    def update_position_easy_mode(self, lid_controller_object):
        """Update bird position for easy mode - TODO: rename this function"""
        try:
            # Get target position from lid sensor
            lid_position = lid_controller_object.get_normalized_position_helper_function()

            # Calculate target Y coordinate - TODO: make this less confusing
            min_y = self.size_in_pixels // 2
            max_y = SCREEN_HEIGHT_THING - self.size_in_pixels // 2 - 50
            # Invert lid position so opening lid moves bird up - TODO: why is this backwards?
            inverted_lid_position = 1.0 - lid_position
            self.target_y_coordinate = min_y + inverted_lid_position * (max_y - min_y)

            # Apply physics - TODO: is this even physics?
            distance_to_target = self.target_y_coordinate - self.y_coordinate
            force_value = distance_to_target * 0.012  # found this number online

            self.velocity_y += force_value
            self.velocity_y *= 0.85  # this feels right

            # Clamp velocity - TODO: use helper function
            self.velocity_y = clamp_value_helper_function(self.velocity_y, -MAX_VELOCITY_CLAMP, MAX_VELOCITY_CLAMP)

            # Update position
            self.y_coordinate += self.velocity_y

            # Keep bird in bounds - TODO: DRY this code
            self.y_coordinate = clamp_value_helper_function(self.y_coordinate,
                                                          self.size_in_pixels//2,
                                                          SCREEN_HEIGHT_THING - 50 - self.size_in_pixels//2)  # TODO: stop at ground sprite

            # Update collision rect - TODO: make this automatic somehow
            self.collision_rect.center = (self.x_coordinate, int(self.y_coordinate))

            # Animate wings - TODO: make this less confusing
            flap_speed = max(3, int(8 - abs(self.velocity_y) * 0.3))
            self.animation_timer_counter += 1
            if self.animation_timer_counter > flap_speed:
                self.animation_frame_index = (self.animation_frame_index + 1) % 3
                self.animation_timer_counter = 0

        except Exception as error_object:
            # TODO: handle errors better
            debug_print_helper(f"Error in easy mode update: {error_object}")

    def update_position_flappy_mode(self, lid_controller_object, space_key_pressed=False):
        """Update bird position for flappy mode - TODO: merge with easy mode somehow"""
        try:
            # Detect flap magnitude
            flap_magnitude_value = lid_controller_object.detect_flap_magnitude_helper()
            if flap_magnitude_value > 0:
                # Calculate proportional jump - TODO: make this formula less magic
                jump_strength_calculated = self.calculate_proportional_jump_helper_function(flap_magnitude_value)
                self.velocity_y = jump_strength_calculated

            # Apply gravity - TODO: understand why gravity is always positive
            if space_key_pressed:
                self.velocity_y += FAST_DROP_GRAVITY
            else:
                self.velocity_y += GRAVITY_ACCELERATION

            # Clamp velocity - TODO: copy paste from easy mode (DRY violation)
            self.velocity_y = clamp_value_helper_function(self.velocity_y, -MAX_VELOCITY_CLAMP, MAX_VELOCITY_CLAMP)

            # Update position
            self.y_coordinate += self.velocity_y

            # Keep in bounds - TODO: another copy paste
            self.y_coordinate = clamp_value_helper_function(self.y_coordinate,
                                                          self.size_in_pixels//2,
                                                          SCREEN_HEIGHT_THING - 50 - self.size_in_pixels//2)  # TODO: stop at ground sprite

            # Update collision rect - TODO: why do we need to do this manually?
            self.collision_rect.center = (self.x_coordinate, int(self.y_coordinate))

            # Animate wings - TODO: copy paste from easy mode
            flap_speed = max(3, int(8 - abs(self.velocity_y) * 0.3))
            self.animation_timer_counter += 1
            if self.animation_timer_counter > flap_speed:
                self.animation_frame_index = (self.animation_frame_index + 1) % 3
                self.animation_timer_counter = 0

        except Exception as flappy_error:
            # TODO: different error handling for different modes
            debug_print_helper(f"Error in flappy mode update: {flappy_error}")

    def calculate_proportional_jump_helper_function(self, angle_change_value):
        """Calculate jump strength - TODO: ask senior dev if this math is right"""
        try:
            # Map 1-100 degrees to jump strength - TODO: made jumps 125% bigger
            min_jump_value = -1.25  # was -1.0, now 25% bigger
            max_jump_value = -22.5  # was -15.0, now 50% bigger

            # Normalize - TODO: learn what normalize means
            normalized_angle_value = (angle_change_value - 1.0) / 99.0
            normalized_angle_value = clamp_value_helper_function(normalized_angle_value, 0.0, 1.0)

            # Power curve - TODO: why 0.7
            jump_strength_result = min_jump_value + (max_jump_value - min_jump_value) * (normalized_angle_value ** 0.7)

            return jump_strength_result

        except Exception as math_error:
            # TODO: fallback to default jump
            debug_print_helper(f"Math error in jump calculation: {math_error}")
            return JUMP_STRENGTH_NEGATIVE

    def draw_bird_on_screen(self, screen_surface_object):
        """Draw the bird - TODO: make this less ugly"""
        try:
            # Check if bird is on screen - TODO: is this necessary?
            if (0 <= self.collision_rect.centerx <= SCREEN_WIDTH_THING and
                0 <= self.collision_rect.centery <= SCREEN_HEIGHT_THING):

                if self.asset_manager_object.assets_loaded_successfully:
                    # Use sprite assets
                    sprite_names_array = ["bird_down", "bird_mid", "bird_up"]
                    current_sprite_name = sprite_names_array[self.animation_frame_index]
                    bird_sprite_surface = self.asset_manager_object.get_sprite_helper(current_sprite_name)

                    if bird_sprite_surface is not None:
                        # Scale sprite - TODO: cache scaled sprites for performance
                        scaled_sprite = pygame.transform.scale(bird_sprite_surface,
                                                             (self.size_in_pixels, self.size_in_pixels))
                        screen_surface_object.blit(scaled_sprite,
                                                 (self.collision_rect.x, self.collision_rect.y))
                    else:
                        # Fallback to rectangle - TODO: make rectangle look like bird
                        pygame.draw.rect(screen_surface_object, YELLOW_COLOR, self.collision_rect)
                else:
                    # No assets loaded - draw rectangle
                    pygame.draw.rect(screen_surface_object, YELLOW_COLOR, self.collision_rect)

        except Exception as drawing_error:
            # TODO: handle drawing errors
            debug_print_helper(f"Error drawing bird: {drawing_error}")

# TODO: split this into multiple files

class PipeObstacleThing:
    """Pipe class - represents the green death tubes"""

    def __init__(self, x_position_start, asset_manager_ref):
        # TODO: understand why pipes are so complicated
        self.x_coordinate = x_position_start
        self.asset_manager_reference = asset_manager_ref

        # Calculate pipe positions - TODO: make this less random
        gap_center_y = random.randint(PIPE_GAP_SIZE, SCREEN_HEIGHT_THING - PIPE_GAP_SIZE)

        # Top pipe rectangle
        self.top_pipe_rect = pygame.Rect(x_position_start, 0,
                                       PIPE_WIDTH_PIXELS, gap_center_y - PIPE_GAP_SIZE//2)

        # Bottom pipe rectangle
        self.bottom_pipe_rect = pygame.Rect(x_position_start, gap_center_y + PIPE_GAP_SIZE//2,
                                          PIPE_WIDTH_PIXELS, SCREEN_HEIGHT_THING - (gap_center_y + PIPE_GAP_SIZE//2))

        # Scoring flag - TODO: use better name
        self.has_been_scored_already = False

    def update_pipe_position(self):
        """Move pipe left - TODO: make speed configurable"""
        try:
            self.x_coordinate -= PIPE_SPEED_PIXELS_PER_FRAME

            # Update rectangles - TODO: why can't rectangles update themselves?
            self.top_pipe_rect.x = self.x_coordinate
            self.bottom_pipe_rect.x = self.x_coordinate

        except Exception as pipe_update_error:
            # TODO: what could go wrong with moving a rectangle
            debug_print_helper(f"Error updating pipe: {pipe_update_error}")

    def check_collision_with_bird(self, bird_object):
        """Check if pipe hits bird - TODO: make collision detection better"""
        try:
            return (self.top_pipe_rect.colliderect(bird_object.collision_rect) or
                   self.bottom_pipe_rect.colliderect(bird_object.collision_rect))
        except Exception as collision_error:
            # TODO: handle collision detection errors
            debug_print_helper(f"Collision detection error: {collision_error}")
            return False

    def is_pipe_off_screen(self):
        """Check if pipe is off screen - TODO: add buffer zone"""
        return self.x_coordinate + PIPE_WIDTH_PIXELS < 0

    def draw_pipe_on_screen(self, screen_surface):
        """Draw pipe on screen - TODO: make pipes look better"""
        try:
            if self.asset_manager_reference.assets_loaded_successfully:
                # Use pipe sprite - TODO: cache pipe sprites
                pipe_sprite = self.asset_manager_reference.get_sprite_helper("pipe")
                if pipe_sprite is not None:
                    # Top pipe (flipped) - TODO: understand pygame transforms
                    top_pipe_scaled = pygame.transform.scale(pipe_sprite,
                                                           (PIPE_WIDTH_PIXELS, self.top_pipe_rect.height))
                    top_pipe_flipped = pygame.transform.flip(top_pipe_scaled, False, True)
                    screen_surface.blit(top_pipe_flipped, self.top_pipe_rect)

                    # Bottom pipe (normal)
                    bottom_pipe_scaled = pygame.transform.scale(pipe_sprite,
                                                              (PIPE_WIDTH_PIXELS, self.bottom_pipe_rect.height))
                    screen_surface.blit(bottom_pipe_scaled, self.bottom_pipe_rect)
                else:
                    # Fallback rectangles - TODO: make these green at least
                    pygame.draw.rect(screen_surface, GREEN_COLOR, self.top_pipe_rect)
                    pygame.draw.rect(screen_surface, GREEN_COLOR, self.bottom_pipe_rect)
            else:
                # No assets - draw green rectangles
                pygame.draw.rect(screen_surface, GREEN_COLOR, self.top_pipe_rect)
                pygame.draw.rect(screen_surface, GREEN_COLOR, self.bottom_pipe_rect)

        except Exception as pipe_drawing_error:
            # TODO: handle pipe drawing errors
            debug_print_helper(f"Error drawing pipe: {pipe_drawing_error}")

# TODO: this class is getting too big
class LidSensorControllerThing:
    """Controls lid sensor - TODO: rename to something better"""

    def __init__(self, min_angle_param=LID_MIN_ANGLE, max_angle_param=LID_MAX_ANGLE):
        # TODO: validate parameters
        self.min_angle_value = min_angle_param
        self.max_angle_value = max_angle_param
        self.sensor_object = None
        self.last_valid_angle_reading = None
        self.connection_attempts_counter = 0
        self.max_connection_attempts_allowed = 3

        # Flap detection variables - TODO: organize these better
        self.previous_angle_reading = None
        self.flap_cooldown_timer_frames = 0

        # Try to connect - TODO: handle connection failures gracefully
        self.connect_to_sensor_helper()

    def connect_to_sensor_helper(self):
        """Connect to lid sensor - TODO: add retry logic"""
        try:
            if self.connection_attempts_counter >= self.max_connection_attempts_allowed:
                debug_print_helper("Max connection attempts reached")
                return False

            self.connection_attempts_counter += 1

            if LidSensor is not None:
                self.sensor_object = LidSensor()
                debug_print_helper(f"Connected to lid sensor (attempt {self.connection_attempts_counter})")
                return True
            else:
                debug_print_helper("LidSensor class not available")
                return False

        except Exception as connection_error:
            # TODO: handle different types of connection errors
            debug_print_helper(f"Failed to connect to lid sensor: {connection_error}")
            return False

    def read_angle_from_sensor(self):
        """Read current angle from sensor - TODO: add caching"""
        try:
            if self.sensor_object is not None:
                current_angle_reading = self.sensor_object.read_angle()
                if current_angle_reading is not None:
                    # Clamp angle to valid range - TODO: is this necessary?
                    clamped_angle = clamp_value_helper_function(current_angle_reading, 0, 131)
                    self.last_valid_angle_reading = clamped_angle
                    return clamped_angle

            # Return last valid reading if current read fails
            return self.last_valid_angle_reading

        except Exception as sensor_read_error:
            # TODO: handle sensor read errors better
            debug_print_helper(f"Sensor read error: {sensor_read_error}")
            if self.connection_attempts_counter < self.max_connection_attempts_allowed:
                self.connect_to_sensor_helper()
            return self.last_valid_angle_reading

    def detect_flap_magnitude_helper(self):
        """Detect flap and return magnitude - TODO: make this less complicated"""
        try:
            # Update cooldown timer - TODO: understand why we need cooldown
            if self.flap_cooldown_timer_frames > 0:
                self.flap_cooldown_timer_frames -= 1

            current_angle_value = self.read_angle_from_sensor()
            if current_angle_value is None:
                return 0.0

            # Need previous angle to detect change
            if self.previous_angle_reading is None:
                self.previous_angle_reading = current_angle_value
                return 0.0

            # Calculate angle change - TODO: add comments explaining the math
            angle_change_amount = current_angle_value - self.previous_angle_reading

            # Update previous angle
            self.previous_angle_reading = current_angle_value

            # Only register upward movements as flaps - TODO: why only upward?
            if angle_change_amount > 1.0 and self.flap_cooldown_timer_frames == 0:
                self.flap_cooldown_timer_frames = 3  # seems reasonable
                return clamp_value_helper_function(angle_change_amount, 0.0, 100.0)

            return 0.0

        except Exception as flap_detection_error:
            # TODO: handle flap detection errors
            debug_print_helper(f"Error detecting flap: {flap_detection_error}")
            return 0.0

    def get_normalized_position_helper_function(self):
        """Get normalized position 0-1 - TODO: rename this function"""
        try:
            angle_reading = self.read_angle_from_sensor()
            if angle_reading is None:
                return 0.5  # TODO: is 0.5 a good default

            # Apply dead zone - TODO: understand what dead zone means
            if abs(angle_reading - self.last_valid_angle_reading or 0) < LID_DEAD_ZONE:
                angle_reading = self.last_valid_angle_reading or angle_reading

            # Normalize to 0-1 range - TODO: add bounds checking
            if angle_reading <= self.min_angle_value:
                return 0.0
            elif angle_reading >= self.max_angle_value:
                return 1.0
            else:
                # Linear interpolation - TODO: make this non-linear for better feel
                normalized_value = ((angle_reading - self.min_angle_value) /
                                  (self.max_angle_value - self.min_angle_value))
                return clamp_value_helper_function(normalized_value, 0.0, 1.0)

        except Exception as normalization_error:
            # TODO: handle normalization errors
            debug_print_helper(f"Error normalizing position: {normalization_error}")
            return 0.5

# TODO: break this file into smaller files
class AssetManagerThing:
    """Manages game assets - TODO: add asset caching"""

    def __init__(self):
        self.assets_loaded_successfully = False
        self.sprite_dictionary = {}
        self.sound_dictionary = {}

        # Try to load assets - TODO: make this async
        self.load_all_assets_helper()

    def load_all_assets_helper(self):
        """Load all game assets - TODO: add progress bar"""
        try:
            # Check if assets directory exists - TODO: create if missing
            # Try different asset paths for different execution contexts
            possible_asset_paths = [
                "assets",  # When running from project root
                "../Resources/assets",  # When running from app bundle MacOS directory
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "Resources", "assets"),  # App bundle fallback
                os.path.join(os.path.dirname(__file__), "assets")  # Same directory fallback
            ]

            assets_directory_path = None
            for path_attempt in possible_asset_paths:
                if os.path.exists(path_attempt):
                    assets_directory_path = path_attempt
                    debug_print_helper(f"Found assets at: {path_attempt}")
                    break

            if assets_directory_path is None:
                debug_print_helper("Assets directory not found in any expected location")
                return False

            # Load sprites - TODO: load in parallel
            sprites_loaded_successfully = self.load_sprite_assets_helper(assets_directory_path)

            # Load sounds - TODO: make sounds optional
            sounds_loaded_successfully = self.load_sound_assets_helper(assets_directory_path)

            # Set loaded flag - TODO: be more specific about what loaded
            self.assets_loaded_successfully = sprites_loaded_successfully

            debug_print_helper(f"Assets loaded: sprites={sprites_loaded_successfully}, sounds={sounds_loaded_successfully}")
            return self.assets_loaded_successfully

        except Exception as asset_loading_error:
            # TODO: handle asset loading errors better
            debug_print_helper(f"Error loading assets: {asset_loading_error}")
            return False

    def load_sprite_assets_helper(self, assets_directory_path):
        """Load sprite assets - TODO: support multiple formats"""
        try:
            sprite_files_mapping = {
                "background": "background-day.png",
                "base": "base.png",
                "pipe": "pipe-green.png",
                "bird_down": "yellowbird-downflap.png",
                "bird_mid": "yellowbird-midflap.png",
                "bird_up": "yellowbird-upflap.png"
            }

            sprites_directory = os.path.join(assets_directory_path, "sprites")

            # Load each sprite - TODO: add error handling per sprite
            for sprite_name_key, filename_value in sprite_files_mapping.items():
                filepath_string = os.path.join(sprites_directory, filename_value)

                if os.path.exists(filepath_string):
                    try:
                        # Load and convert sprite - TODO: understand what convert_alpha does
                        sprite_surface = pygame.image.load(filepath_string).convert_alpha()
                        self.sprite_dictionary[sprite_name_key] = sprite_surface
                        debug_print_helper(f"Loaded sprite: {sprite_name_key}")
                    except Exception as sprite_load_error:
                        # TODO: handle individual sprite load errors
                        debug_print_helper(f"Error loading sprite {sprite_name_key}: {sprite_load_error}")
                        return False
                else:
                    debug_print_helper(f"Sprite file not found: {filepath_string}")
                    return False

            return True

        except Exception as sprite_loading_error:
            # TODO: handle sprite loading errors
            debug_print_helper(f"Error in sprite loading: {sprite_loading_error}")
            return False

    def load_sound_assets_helper(self, assets_directory_path):
        """Load sound assets - TODO: add volume control"""
        try:
            sound_files_mapping = {
                "flap": "wing.wav",
                "hit": "hit.wav",
                "point": "point.wav",
                "die": "die.wav"
            }

            sounds_directory = os.path.join(assets_directory_path, "audio")

            # Check if pygame mixer is initialized - TODO: initialize if not
            if not pygame.mixer.get_init():
                debug_print_helper("Pygame mixer not initialized")
                return False

            # Load each sound - TODO: add format validation
            for sound_name_key, filename_value in sound_files_mapping.items():
                filepath_string = os.path.join(sounds_directory, filename_value)

                if os.path.exists(filepath_string):
                    try:
                        sound_object = pygame.mixer.Sound(filepath_string)
                        self.sound_dictionary[sound_name_key] = sound_object
                        debug_print_helper(f"Loaded sound: {sound_name_key}")
                    except Exception as sound_load_error:
                        # TODO: handle individual sound load errors
                        debug_print_helper(f"Error loading sound {sound_name_key}: {sound_load_error}")
                else:
                    debug_print_helper(f"Sound file not found: {filepath_string}")

            return len(self.sound_dictionary) > 0  # TODO: require all sounds

        except Exception as sound_loading_error:
            # TODO: handle sound loading errors
            debug_print_helper(f"Error in sound loading: {sound_loading_error}")
            return False

    def get_sprite_helper(self, sprite_name_string):
        """Get sprite by name - TODO: add sprite caching"""
        try:
            if sprite_name_string in self.sprite_dictionary:
                return self.sprite_dictionary[sprite_name_string]
            else:
                debug_print_helper(f"Sprite not found: {sprite_name_string}")
                return None
        except Exception as sprite_get_error:
            # TODO: handle sprite get errors
            debug_print_helper(f"Error getting sprite: {sprite_get_error}")
            return None

    def play_sound_helper(self, sound_name_string):
        """Play sound by name - TODO: add sound mixing"""
        try:
            if sound_name_string in self.sound_dictionary:
                self.sound_dictionary[sound_name_string].play()
                debug_print_helper(f"Playing sound: {sound_name_string}")
            else:
                debug_print_helper(f"Sound not found: {sound_name_string}")
        except Exception as sound_play_error:
            # TODO: handle sound play errors
            debug_print_helper(f"Error playing sound: {sound_play_error}")

# TODO: this is getting really long - split into multiple files

class RainbowEffectHelperThing:
    """Rainbow effect for achievements - TODO: make this less CPU intensive"""

    def __init__(self):
        # TODO: understand what hue means
        self.hue_value = 0.0
        self.hue_increment_speed = 2.0  # TODO: make this configurable

    def get_rainbow_color_helper(self):
        """Get current rainbow color - TODO: cache color calculations"""
        try:
            import colorsys  # TODO: move imports to top of file

            # Convert HSV to RGB - TODO: understand color theory
            rgb_tuple = colorsys.hsv_to_rgb(self.hue_value / 360.0, 1.0, 1.0)

            # Convert to pygame color format - TODO: why multiply by 255?
            pygame_color = (int(rgb_tuple[0] * 255),
                          int(rgb_tuple[1] * 255),
                          int(rgb_tuple[2] * 255))

            # Update hue for next frame - TODO: prevent overflow
            self.hue_value = (self.hue_value + self.hue_increment_speed) % 360

            return pygame_color

        except Exception as rainbow_error:
            # TODO: fallback to static color
            debug_print_helper(f"Rainbow effect error: {rainbow_error}")
            return WHITE_COLOR

class ConfettiParticleHelperThing:
    """Single confetti particle - TODO: optimize particle system"""

    def __init__(self, x_start, y_start):
        self.x_position = float(x_start)
        self.y_position = float(y_start)

        # Random velocity - TODO: use better random distribution
        self.velocity_x = random.uniform(-3, 3)
        self.velocity_y = random.uniform(-8, -2)

        # Random color - TODO: use predefined color palette
        self.color_rgb = (random.randint(0, 255),
                         random.randint(0, 255),
                         random.randint(0, 255))

        # Particle properties - TODO: add rotation
        self.size_pixels = random.randint(2, 6)
        self.lifetime_frames = random.randint(60, 120)
        self.age_frames = 0

    def update_particle_physics(self):
        """Update particle position - TODO: add air resistance"""
        try:
            # Apply velocity - TODO: use vector math library
            self.x_position += self.velocity_x
            self.y_position += self.velocity_y

            # Apply gravity to Y velocity - TODO: make gravity configurable
            self.velocity_y += 0.2

            # Age the particle - TODO: add fade out effect
            self.age_frames += 1

        except Exception as particle_update_error:
            # TODO: handle particle update errors
            debug_print_helper(f"Particle update error: {particle_update_error}")

    def is_particle_dead(self):
        """Check if particle should be removed - TODO: add screen bounds check"""
        return (self.age_frames >= self.lifetime_frames or
                self.y_position > SCREEN_HEIGHT_THING + 50)  # TODO: this should use actual screen height

    def draw_particle_on_screen(self, screen_surface):
        """Draw particle - TODO: add particle sprites"""
        try:
            # Calculate alpha based on age - TODO: smooth fade out
            alpha_value = max(0, 255 - int((self.age_frames / self.lifetime_frames) * 255))

            # Draw circle - TODO: use rectangles for better performance?
            pygame.draw.circle(screen_surface, self.color_rgb,
                             (int(self.x_position), int(self.y_position)),
                             self.size_pixels)

        except Exception as particle_draw_error:
            # TODO: handle particle draw errors
            debug_print_helper(f"Particle draw error: {particle_draw_error}")

# TODO: rename this class to something better
class MainGameControllerThing:
    """Main game controller - TODO: split this into smaller classes"""

    def __init__(self):
        # Initialize pygame - TODO: add error handling
        pygame.init()
        pygame.mixer.init()  # TODO: configure audio settings

        # Create screen - TODO: add fullscreen support
        self.screen_surface = pygame.display.set_mode((SCREEN_WIDTH_THING, SCREEN_HEIGHT_THING))
        pygame.display.set_caption("Flappy Lid")  # TODO: make title configurable

        # Create clock for FPS - TODO: make FPS configurable
        self.game_clock = pygame.time.Clock()

        # Create fonts - TODO: load custom fonts
        self.regular_font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        # Initialize game components - TODO: use dependency injection
        self.asset_manager = AssetManagerThing()
        self.lid_controller = LidSensorControllerThing()
        self.high_score_manager = get_global_high_score_manager()

        # Set window icon - TODO: make this optional
        try:
            icon_path_string = os.path.join("assets", "sprites", "yellowbird-midflap.png")
            if os.path.exists(icon_path_string):
                icon_surface = pygame.image.load(icon_path_string).convert_alpha()
                pygame.display.set_icon(icon_surface)
        except Exception as icon_error:
            # TODO: handle icon loading errors
            debug_print_helper(f"Could not load window icon: {icon_error}")

        # Game state variables - TODO: use state machine pattern
        self.current_game_state = "MENU"  # MENU, PLAYING, GAME_OVER
        self.current_score_value = 0
        self.current_high_score = self.high_score_manager.get_current_high_score_helper()

        # Game mode selection - TODO: save selected mode to config
        self.current_selected_mode = EASY_MODE_STRING
        self.selected_mode_index = 0
        self.available_modes_list = [EASY_MODE_STRING, FLAPPY_MODE_STRING]

        # Achievement system - TODO: externalize achievement definitions
        self.unlocked_achievements_set = set()
        self.rainbow_effect_object = RainbowEffectHelperThing()
        self.milestone_effect_timer = 0
        self.milestone_effect_active = False
        self.milestone_score_value = 0

        # Confetti system - TODO: optimize particle management
        self.confetti_particles_list = []

        # Game objects - TODO: initialize these in start_game method
        self.bird_object = None
        self.pipes_list = []
        self.pipe_spawn_timer = 0

        # Sensor availability flag - TODO: detect this dynamically
        self.sensor_is_available = self.lid_controller.sensor_object is not None

        # Initialize bird for menu preview - TODO: make this optional
        initial_bird_y = self.calculate_initial_bird_y_position()
        self.menu_preview_bird = BirdObjectThing(BIRD_X_POSITION, initial_bird_y, self.asset_manager)
        self.menu_preview_bird.target_y_coordinate = float(initial_bird_y)
        self.menu_preview_bird.y_coordinate = float(initial_bird_y)

        # Print startup info - TODO: add verbose logging option
        debug_print_helper("Flappy Lid initialized successfully")
        debug_print_helper("🔥 EXTREME DIFFICULTY MODE 🔥")
        debug_print_helper("- Smaller pipe openings (120px)")
        debug_print_helper("- Maximum height variation (top to bottom)")
        debug_print_helper("- Faster pipe speed and spawn rate")
        debug_print_helper("Controls:")
        debug_print_helper("- Open lid to move bird up")
        debug_print_helper("- Close lid to move bird down")
        debug_print_helper("- SPACE: Start game / Play again")
        debug_print_helper("- ESC: Quit")
        debug_print_helper(f"- Lid angle range: {LID_MIN_ANGLE}° - {LID_MAX_ANGLE}°")

        if not self.sensor_is_available:
            debug_print_helper("Warning: Failed to connect to lid sensor")
            debug_print_helper("Warning: Lid sensor not available - using fallback controls")

    def calculate_initial_bird_y_position(self):
        """Calculate initial bird Y position - TODO: make this more sophisticated"""
        try:
            # Get current lid position - TODO: add error handling
            lid_position_normalized = self.lid_controller.get_normalized_position_helper_function()

            # Calculate Y coordinate - TODO: use constants for bounds
            min_y_value = BIRD_SIZE_PIXELS // 2
            max_y_value = SCREEN_HEIGHT_THING - BIRD_SIZE_PIXELS // 2 - 50

            # Invert lid position so opening lid moves bird up - TODO: copy paste from bird class
            inverted_lid_position = 1.0 - lid_position_normalized
            calculated_y = min_y_value + inverted_lid_position * (max_y_value - min_y_value)

            return int(calculated_y)

        except Exception as calculation_error:
            # TODO: handle calculation errors
            debug_print_helper(f"Error calculating initial bird position: {calculation_error}")
            return SCREEN_HEIGHT_THING // 2  # TODO: use screen center as fallback

    def handle_pygame_events(self):
        """Handle pygame events - TODO: add event queue processing"""
        try:
            for event_object in pygame.event.get():
                if event_object.type == pygame.QUIT:
                    return False
                elif event_object.type == pygame.KEYDOWN:
                    if event_object.key == pygame.K_SPACE or event_object.key == pygame.K_RETURN:  # TODO: support both space and enter
                        if self.current_game_state == "MENU":
                            self.current_selected_mode = self.available_modes_list[self.selected_mode_index]
                            self.start_new_game_helper()
                        elif self.current_game_state == "GAME_OVER":
                            self.reset_game_to_menu_helper()
                    elif event_object.key == pygame.K_ESCAPE:
                        return False
                    elif (event_object.key == pygame.K_LEFT or event_object.key == pygame.K_UP) and self.current_game_state == "MENU":  # TODO: support left/up for previous mode
                        # TODO: add wrap around logic
                        self.selected_mode_index = (self.selected_mode_index - 1) % len(self.available_modes_list)
                    elif (event_object.key == pygame.K_RIGHT or event_object.key == pygame.K_DOWN) and self.current_game_state == "MENU":  # TODO: support right/down for next mode
                        self.selected_mode_index = (self.selected_mode_index + 1) % len(self.available_modes_list)

            return True

        except Exception as event_handling_error:
            # TODO: handle event handling errors
            debug_print_helper(f"Error handling events: {event_handling_error}")
            return False

    def start_new_game_helper(self):
        """Start a new game - TODO: add game initialization validation"""
        try:
            # Set game state - TODO: validate state transition
            self.current_game_state = "PLAYING"

            # Reset score - TODO: add score validation
            self.current_score_value = 0

            # Reset achievement tracking - TODO: save achievements between games
            self.milestone_effect_timer = 0
            self.milestone_effect_active = False
            self.milestone_score_value = 0

            # Clear confetti particles - TODO: add particle cleanup method
            self.confetti_particles_list.clear()

            # Create new bird - TODO: use factory pattern
            initial_y_position = self.calculate_initial_bird_y_position()
            self.bird_object = BirdObjectThing(BIRD_X_POSITION, initial_y_position, self.asset_manager)

            # Clear pipes - TODO: add pipe cleanup method
            self.pipes_list.clear()
            self.pipe_spawn_timer = 0

            debug_print_helper(f"Started new game in {self.current_selected_mode} mode")

        except Exception as game_start_error:
            # TODO: handle game start errors
            debug_print_helper(f"Error starting game: {game_start_error}")

    def reset_game_to_menu_helper(self):
        """Reset game to menu state - TODO: add cleanup validation"""
        try:
            # Set state to menu - TODO: validate state transition
            self.current_game_state = "MENU"

            # Reset selected mode index - TODO: remember last selected mode
            self.selected_mode_index = 0

            debug_print_helper("Game reset to menu")

        except Exception as reset_error:
            # TODO: handle reset errors
            debug_print_helper(f"Error resetting game: {reset_error}")

    def update_game_logic(self):
        """Update game logic - TODO: split into smaller methods"""
        try:
            if self.current_game_state == "MENU":
                # Update menu preview bird - TODO: make this optional
                self.menu_preview_bird.update_position_easy_mode(self.lid_controller)

            elif self.current_game_state == "PLAYING":
                # Update bird based on selected mode - TODO: use polymorphism
                if self.current_selected_mode == FLAPPY_MODE_STRING:
                    keys_pressed_dict = pygame.key.get_pressed()
                    space_key_held = keys_pressed_dict[pygame.K_SPACE]
                    self.bird_object.update_position_flappy_mode(self.lid_controller, space_key_held)
                else:
                    self.bird_object.update_position_easy_mode(self.lid_controller)

                # Update pipe spawn timer - TODO: make spawn rate configurable
                self.pipe_spawn_timer += 1
                current_spawn_rate = self.calculate_dynamic_pipe_spawn_rate()

                if self.pipe_spawn_timer > current_spawn_rate:
                    # Spawn new pipe - TODO: use object pool
                    new_pipe = PipeObstacleThing(SCREEN_WIDTH_THING, self.asset_manager)
                    self.pipes_list.append(new_pipe)
                    self.pipe_spawn_timer = 0

                # Update existing pipes - TODO: use list comprehension
                pipes_to_remove_list = []
                for pipe_object in self.pipes_list:
                    pipe_object.update_pipe_position()

                    # Check for scoring - TODO: prevent double scoring
                    if (not pipe_object.has_been_scored_already and
                        pipe_object.x_coordinate + PIPE_WIDTH_PIXELS < self.bird_object.x_coordinate):
                        self.current_score_value += 1
                        pipe_object.has_been_scored_already = True
                        self.asset_manager.play_sound_helper("point")
                        self.check_for_achievements_helper()

                    # Check for collision - TODO: add collision tolerance
                    if pipe_object.check_collision_with_bird(self.bird_object):
                        self.current_game_state = "GAME_OVER"
                        self.asset_manager.play_sound_helper("hit")

                        # Update high score if necessary - TODO: add score validation
                        if self.current_score_value > self.current_high_score:
                            self.high_score_manager.update_high_score_if_better(self.current_score_value)
                            self.current_high_score = self.current_score_value

                        return

                    # Mark pipes for removal if off screen - TODO: use iterator
                    if pipe_object.is_pipe_off_screen():
                        pipes_to_remove_list.append(pipe_object)

                # Remove off-screen pipes - TODO: optimize removal process
                for pipe_to_remove in pipes_to_remove_list:
                    if pipe_to_remove in self.pipes_list:
                        self.pipes_list.remove(pipe_to_remove)

                # Update achievement effects - TODO: move to separate method
                self.update_achievement_effects_helper()

        except Exception as game_logic_error:
            # TODO: handle game logic errors gracefully
            debug_print_helper(f"Error updating game logic: {game_logic_error}")
            self.current_game_state = "GAME_OVER"

    def calculate_dynamic_pipe_spawn_rate(self):
        """Calculate pipe spawn rate based on score - TODO: use difficulty curve"""
        try:
            base_spawn_rate = PIPE_SPAWN_INTERVAL_FRAMES

            # Make pipes spawn closer together as score increases - TODO: add configuration
            if self.current_score_value >= 50:
                return base_spawn_rate
            else:
                # Linear interpolation from double spacing to normal spacing - TODO: use curve
                progress_ratio = self.current_score_value / 50.0
                return int(base_spawn_rate * 2 - base_spawn_rate * progress_ratio)

        except Exception as spawn_rate_error:
            # TODO: handle spawn rate calculation errors
            debug_print_helper(f"Error calculating spawn rate: {spawn_rate_error}")
            return PIPE_SPAWN_INTERVAL_FRAMES

    def check_for_achievements_helper(self):
        """Check for achievement unlocks - TODO: externalize achievement logic"""
        try:
            score_value = self.current_score_value

            # Check milestone achievements - TODO: use configuration
            milestone_scores_list = [10, 20, 30, 50, 100]

            for milestone_score in milestone_scores_list:
                if score_value == milestone_score and milestone_score not in self.unlocked_achievements_set:
                    self.unlocked_achievements_set.add(milestone_score)
                    self.milestone_effect_active = True
                    self.milestone_effect_timer = 180  # TODO: make duration configurable
                    self.milestone_score_value = milestone_score

                    debug_print_helper(f"🎯 MILESTONE ACHIEVED: {milestone_score} points!")

                    # Special effects for different milestones - TODO: use strategy pattern
                    if milestone_score == 100:
                        # Spawn confetti - TODO: make confetti count configurable
                        self.spawn_confetti_particles_helper(50)

                    break

        except Exception as achievement_error:
            # TODO: handle achievement errors
            debug_print_helper(f"Error checking achievements: {achievement_error}")

    def spawn_confetti_particles_helper(self, particle_count_int):
        """Spawn confetti particles - TODO: optimize particle creation"""
        try:
            for particle_index in range(particle_count_int):
                # Random spawn position - TODO: use better distribution
                spawn_x = random.randint(0, SCREEN_WIDTH_THING)
                spawn_y = random.randint(0, SCREEN_HEIGHT_THING // 2)

                # Create particle - TODO: use object pool
                new_particle = ConfettiParticleHelperThing(spawn_x, spawn_y)
                self.confetti_particles_list.append(new_particle)

        except Exception as confetti_error:
            # TODO: handle confetti spawning errors
            debug_print_helper(f"Error spawning confetti: {confetti_error}")

    def update_achievement_effects_helper(self):
        """Update achievement effects - TODO: move to separate effects manager"""
        try:
            # Update milestone effect timer - TODO: add smooth transitions
            if self.milestone_effect_timer > 0:
                self.milestone_effect_timer -= 1
                if self.milestone_effect_timer <= 0:
                    self.milestone_effect_active = False

            # Update confetti particles - TODO: use batch processing
            particles_to_remove_list = []
            for particle_object in self.confetti_particles_list:
                particle_object.update_particle_physics()

                if particle_object.is_particle_dead():
                    particles_to_remove_list.append(particle_object)

            # Remove dead particles - TODO: optimize removal
            for dead_particle in particles_to_remove_list:
                if dead_particle in self.confetti_particles_list:
                    self.confetti_particles_list.remove(dead_particle)

        except Exception as effects_error:
            # TODO: handle effects update errors
            debug_print_helper(f"Error updating effects: {effects_error}")

# TODO: continue with drawing methods...

    def draw_text_with_shadow_helper(self, text_string, font_object, color_tuple, x_pos, y_pos, center_flag=False, shadow_offset_pixels=2):
        """Draw text with shadow - TODO: optimize text rendering"""
        try:
            # Render shadow text - TODO: cache rendered text
            shadow_color_tuple = BLACK_COLOR
            shadow_text_surface = font_object.render(text_string, True, shadow_color_tuple)

            # Render main text - TODO: use anti-aliasing settings
            main_text_surface = font_object.render(text_string, True, color_tuple)

            if center_flag:
                # Center both texts - TODO: calculate once and reuse
                shadow_rect_object = shadow_text_surface.get_rect(center=(x_pos + shadow_offset_pixels, y_pos + shadow_offset_pixels))
                main_rect_object = main_text_surface.get_rect(center=(x_pos, y_pos))
            else:
                # Position both texts - TODO: validate coordinates
                shadow_rect_object = (x_pos + shadow_offset_pixels, y_pos + shadow_offset_pixels)
                main_rect_object = (x_pos, y_pos)

            # Draw shadow first, then main text - TODO: batch drawing operations
            self.screen_surface.blit(shadow_text_surface, shadow_rect_object)
            self.screen_surface.blit(main_text_surface, main_rect_object)

            return main_text_surface.get_rect(center=(x_pos, y_pos)) if center_flag else main_text_surface.get_rect(topleft=(x_pos, y_pos))

        except Exception as text_shadow_error:
            # TODO: fallback to regular text without shadow
            debug_print_helper(f"Error drawing text with shadow: {text_shadow_error}")
            main_text_surface = font_object.render(text_string, True, color_tuple)
            if center_flag:
                main_rect_object = main_text_surface.get_rect(center=(x_pos, y_pos))
            else:
                main_rect_object = (x_pos, y_pos)
            self.screen_surface.blit(main_text_surface, main_rect_object)
            return main_text_surface.get_rect(center=(x_pos, y_pos)) if center_flag else main_text_surface.get_rect(topleft=(x_pos, y_pos))

    def draw_background_helper(self):
        """Draw game background - TODO: add parallax scrolling"""
        try:
            if self.asset_manager.assets_loaded_successfully:
                # Use official background - TODO: tile background for different resolutions
                background_surface = self.asset_manager.get_sprite_helper("background")
                if background_surface is not None:
                    # Scale background to fit screen - TODO: cache scaled background
                    scaled_background = pygame.transform.scale(background_surface, (SCREEN_WIDTH_THING, SCREEN_HEIGHT_THING))
                    self.screen_surface.blit(scaled_background, (0, 0))

                    # Use official base/ground sprite - TODO: animate ground scrolling
                    base_surface = self.asset_manager.get_sprite_helper("base")
                    if base_surface is not None:
                        # Scale and position base - TODO: calculate position dynamically
                        scaled_base = pygame.transform.scale(base_surface, (SCREEN_WIDTH_THING, 50))
                        self.screen_surface.blit(scaled_base, (0, SCREEN_HEIGHT_THING - 50))
                    return

            # Fallback to drawn background - TODO: make this prettier
            self.screen_surface.fill(BLUE_COLOR)

            # Draw simple ground - TODO: add texture
            ground_rect_object = pygame.Rect(0, SCREEN_HEIGHT_THING - 50, SCREEN_WIDTH_THING, 50)
            pygame.draw.rect(self.screen_surface, BROWN_COLOR, ground_rect_object)
            pygame.draw.rect(self.screen_surface, BLACK_COLOR, ground_rect_object, 2)

        except Exception as background_error:
            # TODO: handle background drawing errors
            debug_print_helper(f"Error drawing background: {background_error}")

    def draw_menu_bird_preview_helper(self):
        """Draw bird preview on menu - TODO: add animation"""
        try:
            # Draw the preview bird - TODO: make this more obvious
            self.menu_preview_bird.draw_bird_on_screen(self.screen_surface)

            # Draw red arrow pointing to bird - TODO: animate arrow
            self.draw_red_arrow_pointing_to_bird_helper()

        except Exception as preview_error:
            # TODO: handle preview drawing errors
            debug_print_helper(f"Error drawing menu bird preview: {preview_error}")

    def draw_red_arrow_pointing_to_bird_helper(self):
        """Draw red arrow pointing to menu bird - TODO: make arrow more obvious"""
        try:
            bird_x_coordinate = int(self.menu_preview_bird.x_coordinate)
            bird_y_coordinate = int(self.menu_preview_bird.y_coordinate)

            # Arrow pointing from right side toward bird - TODO: calculate better positioning
            arrow_start_x = bird_x_coordinate + BIRD_SIZE_PIXELS + 30
            arrow_start_y = bird_y_coordinate
            arrow_end_x = bird_x_coordinate + BIRD_SIZE_PIXELS//2 + 5
            arrow_end_y = bird_y_coordinate

            # Draw arrow shaft (line) - TODO: make line thicker
            pygame.draw.line(self.screen_surface, RED_COLOR,
                           (arrow_start_x, arrow_start_y),
                           (arrow_end_x, arrow_end_y), 3)

            # Draw arrow head (triangle) - TODO: make triangle bigger
            arrow_head_size = 8
            arrow_head_points_list = [
                (arrow_end_x, arrow_end_y),  # tip
                (arrow_end_x + arrow_head_size, arrow_end_y - arrow_head_size//2),  # top
                (arrow_end_x + arrow_head_size, arrow_end_y + arrow_head_size//2)   # bottom
            ]
            pygame.draw.polygon(self.screen_surface, RED_COLOR, arrow_head_points_list)

        except Exception as arrow_error:
            # TODO: handle arrow drawing errors
            debug_print_helper(f"Error drawing red arrow: {arrow_error}")

    def draw_mode_selection_ui_helper(self):
        """Draw mode selection UI - TODO: add animations"""
        try:
            # Mode selection title with shadow - TODO: make title bigger
            self.draw_text_with_shadow_helper("Select Game Mode:", self.regular_font, WHITE_COLOR,
                                             SCREEN_WIDTH_THING//2, SCREEN_HEIGHT_THING//2 - 20, center_flag=True)

            # Draw mode options - TODO: add icons for each mode
            for mode_index, mode_string in enumerate(self.available_modes_list):
                y_position_calculated = SCREEN_HEIGHT_THING//2 + 20 + (mode_index * 60)

                # Highlight selected mode - TODO: add smooth color transitions
                text_color = YELLOW_COLOR if mode_index == self.selected_mode_index else WHITE_COLOR

                # Mode name with shadow - TODO: add mode descriptions
                mode_rect = self.draw_text_with_shadow_helper(f"{mode_string} MODE", self.regular_font, text_color,
                                                            SCREEN_WIDTH_THING//2, y_position_calculated, center_flag=True)

                # Mode description with shadow - TODO: make descriptions more detailed
                if mode_string == EASY_MODE_STRING:
                    description_text = "Bird follows lid position directly"
                else:  # FLAPPY_MODE_STRING
                    description_text = "Flap lid to jump up, gravity pulls down"

                self.draw_text_with_shadow_helper(description_text, self.regular_font, text_color,
                                                 SCREEN_WIDTH_THING//2, y_position_calculated + 20, center_flag=True)

                # Selection arrows - TODO: animate arrows
                if mode_index == self.selected_mode_index:
                    # Left arrow - TODO: use sprite instead of polygon
                    pygame.draw.polygon(self.screen_surface, text_color, [
                        (mode_rect.left - 30, y_position_calculated),
                        (mode_rect.left - 20, y_position_calculated - 5),
                        (mode_rect.left - 20, y_position_calculated + 5)
                    ])
                    # Right arrow - TODO: use sprite instead of polygon
                    pygame.draw.polygon(self.screen_surface, text_color, [
                        (mode_rect.right + 30, y_position_calculated),
                        (mode_rect.right + 20, y_position_calculated - 5),
                        (mode_rect.right + 20, y_position_calculated + 5)
                    ])

        except Exception as mode_selection_error:
            # TODO: handle mode selection drawing errors
            debug_print_helper(f"Error drawing mode selection: {mode_selection_error}")

    def draw_all_ui_elements_helper(self):
        """Draw all UI elements - TODO: organize UI drawing better"""
        try:
            if self.current_game_state == "MENU":
                # Title with shadow - TODO: add title animation
                self.draw_text_with_shadow_helper("Flappy Lid", self.big_font, WHITE_COLOR,
                                                 SCREEN_WIDTH_THING//2, SCREEN_HEIGHT_THING//3, center_flag=True, shadow_offset_pixels=3)

                # Draw bird preview - TODO: make preview more interactive
                self.draw_menu_bird_preview_helper()

                # Mode selection UI - TODO: add keyboard shortcuts display
                self.draw_mode_selection_ui_helper()

                # Start instructions with shadow - TODO: animate text
                self.draw_text_with_shadow_helper("Press SPACE/Enter to start", self.regular_font, WHITE_COLOR,
                                                 SCREEN_WIDTH_THING//2, SCREEN_HEIGHT_THING//2 + 170, center_flag=True)

                # Sensor status in top right with shadow - TODO: add sensor strength indicator
                sensor_status_text = "Sensor: Connected" if self.sensor_is_available else "Sensor: Not Available"
                sensor_color = GREEN_COLOR if self.sensor_is_available else RED_COLOR
                self.draw_text_with_shadow_helper(sensor_status_text, self.regular_font, sensor_color,
                                                 SCREEN_WIDTH_THING - 10, 20, center_flag=False)

                # High score at absolute bottom with shadow - TODO: add high score animation
                if self.current_high_score > 0:
                    self.draw_text_with_shadow_helper(f"HIGH SCORE: {self.current_high_score}", self.big_font, YELLOW_COLOR,
                                                     SCREEN_WIDTH_THING//2, SCREEN_HEIGHT_THING - 30, center_flag=True, shadow_offset_pixels=3)
                else:
                    # Motivational message - TODO: randomize motivational messages
                    self.draw_text_with_shadow_helper("Set your first high score!", self.regular_font, WHITE_COLOR,
                                                     SCREEN_WIDTH_THING//2, SCREEN_HEIGHT_THING - 30, center_flag=True)

            elif self.current_game_state == "PLAYING":
                # Score display with potential effects - TODO: add score animations
                if self.milestone_effect_active and self.milestone_score_value in [10, 20, 30]:
                    # Rainbow flashing effect - TODO: make rainbow smoother
                    rainbow_color = self.rainbow_effect_object.get_rainbow_color_helper()
                    self.draw_text_with_shadow_helper(f"Score: {self.current_score_value}", self.big_font, rainbow_color,
                                                     SCREEN_WIDTH_THING//2, 50, center_flag=True, shadow_offset_pixels=3)
                elif self.milestone_effect_active and self.milestone_score_value == 50:
                    # Enlarged rainbow effect - TODO: add pulsing animation
                    rainbow_color = self.rainbow_effect_object.get_rainbow_color_helper()
                    enlarged_font = pygame.font.Font(None, 96)  # TODO: cache font objects
                    enlarged_text_surface = enlarged_font.render(f"{self.current_score_value}", True, rainbow_color)
                    enlarged_rect = enlarged_text_surface.get_rect(center=(SCREEN_WIDTH_THING//2, SCREEN_HEIGHT_THING//2))

                    # Add pulsing effect - TODO: use sine wave for smooth pulsing
                    pulse_scale = 1.0 + 0.2 * abs(math.sin(pygame.time.get_ticks() * 0.01))
                    pulsed_size = (int(enlarged_text_surface.get_width() * pulse_scale),
                                 int(enlarged_text_surface.get_height() * pulse_scale))
                    pulsed_surface = pygame.transform.scale(enlarged_text_surface, pulsed_size)
                    pulsed_rect = pulsed_surface.get_rect(center=(SCREEN_WIDTH_THING//2, SCREEN_HEIGHT_THING//2))

                    self.screen_surface.blit(pulsed_surface, pulsed_rect)
                elif self.milestone_effect_active and self.milestone_score_value == 100:
                    # Confetti celebration - TODO: add more celebration effects
                    rainbow_color = self.rainbow_effect_object.get_rainbow_color_helper()
                    celebration_font = pygame.font.Font(None, 120)  # TODO: cache font objects
                    score_text_surface = celebration_font.render(f"100!", True, rainbow_color)
                    score_rect = score_text_surface.get_rect(center=(SCREEN_WIDTH_THING//2, SCREEN_HEIGHT_THING//2))
                    self.screen_surface.blit(score_text_surface, score_rect)

                    # Draw "LEGENDARY!" text - TODO: animate this text
                    legendary_text_surface = self.big_font.render("LEGENDARY!", True, rainbow_color)
                    legendary_rect = legendary_text_surface.get_rect(center=(SCREEN_WIDTH_THING//2, SCREEN_HEIGHT_THING//2 + 80))
                    self.screen_surface.blit(legendary_text_surface, legendary_rect)
                else:
                    # Normal score display with shadow - TODO: add score counter animation
                    self.draw_text_with_shadow_helper(f"Score: {self.current_score_value}", self.regular_font, WHITE_COLOR,
                                                     10, 10, center_flag=False)

                # High score in corner during gameplay with shadow - TODO: fade in/out
                if self.current_high_score > 0:
                    self.draw_text_with_shadow_helper(f"Best: {self.current_high_score}", self.regular_font, YELLOW_COLOR,
                                                     SCREEN_WIDTH_THING - 10, 10, center_flag=False)

                # Lid angle display for debugging with shadow - TODO: make this optional
                current_angle = self.lid_controller.read_angle_from_sensor()
                if current_angle is not None:
                    self.draw_text_with_shadow_helper(f"Lid: {current_angle:.1f}°", self.regular_font, WHITE_COLOR,
                                                     10, 50, center_flag=False)

            elif self.current_game_state == "GAME_OVER":
                # Game over text with shadow - TODO: add game over animation
                self.draw_text_with_shadow_helper("Game Over", self.big_font, WHITE_COLOR,
                                                 SCREEN_WIDTH_THING//2, SCREEN_HEIGHT_THING//3, center_flag=True, shadow_offset_pixels=3)

                # Final score with shadow - TODO: highlight if new high score
                self.draw_text_with_shadow_helper(f"Score: {self.current_score_value}", self.regular_font, WHITE_COLOR,
                                                 SCREEN_WIDTH_THING//2, SCREEN_HEIGHT_THING//2, center_flag=True)

                # High score status with shadow - TODO: add celebration for new high score
                if self.current_score_value == self.current_high_score and self.current_score_value > 0:
                    self.draw_text_with_shadow_helper("🎉 NEW HIGH SCORE! 🎉", self.regular_font, YELLOW_COLOR,
                                                     SCREEN_WIDTH_THING//2, SCREEN_HEIGHT_THING//2 + 30, center_flag=True)
                elif self.current_high_score > 0:
                    self.draw_text_with_shadow_helper(f"Best: {self.current_high_score}", self.regular_font, YELLOW_COLOR,
                                                     SCREEN_WIDTH_THING//2, SCREEN_HEIGHT_THING//2 + 30, center_flag=True)

                # Restart instruction with shadow - TODO: add multiple restart options
                self.draw_text_with_shadow_helper("Press SPACE to play again", self.regular_font, WHITE_COLOR,
                                                 SCREEN_WIDTH_THING//2, SCREEN_HEIGHT_THING//2 + 70, center_flag=True)

        except Exception as ui_drawing_error:
            # TODO: handle UI drawing errors gracefully
            debug_print_helper(f"Error drawing UI: {ui_drawing_error}")

    def draw_everything_on_screen_helper(self):
        """Draw everything on screen - TODO: optimize drawing order"""
        try:
            # Clear screen - TODO: use dirty rectangle updates
            self.screen_surface.fill(BLACK_COLOR)

            # Draw background - TODO: add background layers
            self.draw_background_helper()

            # Draw game objects - TODO: use sprite groups
            if self.current_game_state == "PLAYING" or self.current_game_state == "GAME_OVER":
                # Draw pipes - TODO: batch pipe drawing
                for pipe_object in self.pipes_list:
                    pipe_object.draw_pipe_on_screen(self.screen_surface)

                # Draw bird - TODO: add bird trail effect
                if self.bird_object is not None:
                    self.bird_object.draw_bird_on_screen(self.screen_surface)

            # Draw confetti particles - TODO: use particle system
            for confetti_particle in self.confetti_particles_list:
                confetti_particle.draw_particle_on_screen(self.screen_surface)

            # Draw UI elements - TODO: separate UI layer
            self.draw_all_ui_elements_helper()

            # Update display - TODO: use partial updates
            pygame.display.flip()

        except Exception as drawing_error:
            # TODO: handle drawing errors
            debug_print_helper(f"Error drawing everything: {drawing_error}")

    def run_main_game_loop_helper(self):
        """Main game loop - TODO: add pause functionality"""
        try:
            game_running_flag = True

            debug_print_helper("Starting main game loop")

            while game_running_flag:
                # Handle events - TODO: add event filtering
                game_running_flag = self.handle_pygame_events()
                if not game_running_flag:
                    break

                # Update game logic - TODO: add fixed timestep
                self.update_game_logic()

                # Draw everything - TODO: add frame skipping
                self.draw_everything_on_screen_helper()

                # Control frame rate - TODO: add VSync option
                self.game_clock.tick(FPS_VALUE)

            debug_print_helper("Game loop ended")

        except Exception as game_loop_error:
            # TODO: handle game loop errors
            debug_print_helper(f"Error in main game loop: {game_loop_error}")
        finally:
            # Cleanup - TODO: add proper cleanup methods
            pygame.quit()
            debug_print_helper("Pygame cleaned up")

# TODO: add main execution block
def main_function_entry_point():
    """Main function - TODO: add command line argument parsing"""
    try:
        # Create and run game - TODO: add error recovery
        game_controller = MainGameControllerThing()
        game_controller.run_main_game_loop_helper()

    except Exception as main_error:
        # TODO: handle main function errors
        debug_print_helper(f"Error in main function: {main_error}")
        print("Game crashed! TODO: add crash reporting")

# TODO: learn what __name__ == "__main__" means
if __name__ == "__main__":
    main_function_entry_point()

# TODO: add more TODOs
# TODO: remove TODOs
# TODO: learn regex
# TODO: fix this with AI when Skynet is released
# TODO: add unit tests
# TODO: add integration tests
# TODO: add documentation
# TODO: optimize for production
# TODO: add monitoring and logging
# TODO: implement proper error handling
# TODO: add configuration management
# TODO: implement proper state management
# TODO: add proper asset management
# TODO: implement proper physics engine
# TODO: add networking support
# TODO: implement save/load system
# TODO: add accessibility features
# TODO: implement proper audio system
# TODO: add mobile support
# TODO: implement VR support
# TODO: add blockchain integration
# TODO: implement machine learning
# TODO: add cloud save support
# TODO: implement real-time multiplayer
# TODO: add mod support
# TODO: implement achievement system 2.0
# TODO: add social media integration
# TODO: implement analytics
# TODO: add A/B testing framework
# TODO: implement feature flags
# TODO: add internationalization
# TODO: implement dark mode
# TODO: add premium subscription model
# TODO: implement cryptocurrency rewards
# TODO: add NFT support
# TODO: implement quantum computing optimization
# TODO: add time travel mechanics
# TODO: implement multiverse support
# TODO: add consciousness uploading

# End of file - TODO: is this even necessary?
