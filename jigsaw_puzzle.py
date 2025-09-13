import pygame
import random
import math
import time
import json
import os
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from typing import List, Any, Optional, Tuple

def clamp_color(value):
    """Ensure color values are within valid range (0-255)."""
    return max(0, min(255, int(value)))

class HintType(Enum):
    """Types of hints available in the enhanced hint system."""
    EDGE_STRUCTURE = "edge_structure"
    FOCAL_POINT = "focal_point"
    COLOR_REGION = "color_region"
    PATTERN_MATCH = "pattern_match"
    COMPOSITION_OVERVIEW = "composition_overview"
    PROGRESS_GUIDANCE = "progress_guidance"

@dataclass
class PuzzleLevel:
    """Represents a puzzle level with image and metadata."""
    name: str
    image_url: str
    description: str
    difficulty: int  # 1-5
    grid_size: tuple
    points: int

@dataclass
class PuzzleRegion:
    """Represents a rectangular region within the puzzle."""
    x: int
    y: int
    width: int
    height: int
    piece_ids: List[int]

    def contains_point(self, px: int, py: int) -> bool:
        """Check if a point is within this region."""
        return (self.x <= px <= self.x + self.width and
                self.y <= py <= self.y + self.height)

class PuzzlePiece:
    def __init__(self, x, y, width, height, image_section, correct_x, correct_y, piece_id):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image_section = image_section
        self.correct_x = correct_x
        self.correct_y = correct_y
        self.piece_id = piece_id
        self.is_placed = False
        self.dragging = False
        self.hint_revealed = False
        self.rotation = 0  # For future rotation feature

    def draw(self, screen, alpha=255):
        if self.image_section:
            temp_surface = self.image_section.copy()
            temp_surface.set_alpha(alpha)
            screen.blit(temp_surface, (self.x, self.y))

            # Draw border with different colors for different states
            if self.is_placed:
                color = (0, 255, 0)  # Green for placed
            elif self.hint_revealed:
                color = (255, 255, 0)  # Yellow for hinted
            elif self.dragging:
                color = (255, 100, 100)  # Red for dragging
            else:
                color = (255, 255, 255)  # White for normal

            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), 2)

    def contains_point(self, px, py):
        return (self.x <= px <= self.x + self.width and
                self.y <= py <= self.y + self.height)

    def is_near_correct_position(self, tolerance=30):
        return (abs(self.x - self.correct_x) < tolerance and
                abs(self.y - self.correct_y) < tolerance)

class JigsawPuzzle:
    def __init__(self):
        pygame.init()
        self.screen_width = 1200
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Jigsaw Puzzle Adventure")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)

        # Game state
        self.current_level = 0
        self.total_score = 0
        self.level_start_time = None
        self.puzzle_complete = False

        # Puzzle dimensions
        self.puzzle_width = 600
        self.puzzle_height = 450

        # Positions
        self.puzzle_x = 50
        self.puzzle_y = 100
        self.pieces_area_x = 700
        self.pieces_area_y = 100

        # Initialize levels
        self.levels = self.create_levels()

        # Game variables
        self.pieces = []
        self.selected_piece = None
        self.mouse_offset_x = 0
        self.mouse_offset_y = 0

        # Hint system
        self.save_file = "puzzle_progress.json"
        self.load_progress()

        # UI elements
        self.next_button_rect = pygame.Rect(900, 600, 150, 50)
        self.hint_button_rect = pygame.Rect(900, 550, 150, 40)

        # Load first level
        self.load_level(self.current_level)

    def create_levels(self):
        """Create puzzle levels with different themes and difficulties."""
        return [
            PuzzleLevel("Cute Cat", self.create_cat_image(), "Adorable orange tabby cat", 1, (3, 2), 100),
            PuzzleLevel("Mona Lisa", self.create_monalisa_image(), "Leonardo da Vinci's masterpiece", 2, (4, 3), 200),
            PuzzleLevel("Starry Night", self.create_starry_night_image(), "Van Gogh's swirling sky", 3, (4, 3), 300),
            PuzzleLevel("Sunflowers", self.create_sunflower_image(), "Bright yellow sunflower field", 2, (3, 3), 250),
            PuzzleLevel("Mountain Lake", self.create_landscape_image(), "Serene mountain reflection", 3, (5, 3), 350),
            PuzzleLevel("Abstract Art", self.create_abstract_image(), "Colorful geometric patterns", 4, (4, 4), 400),
            PuzzleLevel("City Skyline", self.create_city_image(), "Modern urban landscape", 4, (5, 4), 450),
            PuzzleLevel("Ocean Waves", self.create_ocean_image(), "Crashing ocean waves", 5, (6, 4), 500),
        ]

    def create_cat_image(self):
        """Create a stylized cat image."""
        surface = pygame.Surface((600, 450))
        surface.fill((135, 206, 235))  # Sky blue background

        # Cat body (orange)
        pygame.draw.ellipse(surface, (255, 140, 0), (200, 200, 200, 150))

        # Cat head
        pygame.draw.circle(surface, (255, 140, 0), (300, 180), 80)

        # Cat ears
        pygame.draw.polygon(surface, (255, 140, 0), [(250, 120), (270, 160), (290, 140)])
        pygame.draw.polygon(surface, (255, 140, 0), [(310, 140), (330, 160), (350, 120)])

        # Inner ears
        pygame.draw.polygon(surface, (255, 182, 193), [(260, 135), (275, 150), (285, 140)])
        pygame.draw.polygon(surface, (255, 182, 193), [(315, 140), (325, 150), (340, 135)])

        # Eyes
        pygame.draw.circle(surface, (34, 139, 34), (280, 170), 15)
        pygame.draw.circle(surface, (34, 139, 34), (320, 170), 15)
        pygame.draw.circle(surface, (0, 0, 0), (280, 170), 8)
        pygame.draw.circle(surface, (0, 0, 0), (320, 170), 8)

        # Nose
        pygame.draw.polygon(surface, (255, 20, 147), [(295, 185), (305, 185), (300, 195)])

        # Mouth
        pygame.draw.arc(surface, (0, 0, 0), (285, 195, 30, 20), 0, math.pi, 2)

        # Whiskers
        for i in range(3):
            y_offset = i * 5
            pygame.draw.line(surface, (0, 0, 0), (240, 185 + y_offset), (270, 190 + y_offset), 2)
            pygame.draw.line(surface, (0, 0, 0), (330, 190 + y_offset), (360, 185 + y_offset), 2)

        # Stripes
        for i in range(5):
            y = 150 + i * 20
            pygame.draw.line(surface, (200, 100, 0), (250, y), (350, y), 3)

        # Grass
        for x in range(0, 600, 20):
            for blade in range(3):
                blade_x = x + random.randint(0, 15)
                pygame.draw.line(surface, (34, 139, 34), (blade_x, 400), (blade_x, 380 + random.randint(0, 20)), 2)

        return surface

    def create_monalisa_image(self):
        """Create a simplified Mona Lisa inspired image."""
        surface = pygame.Surface((600, 450))

        # Background - renaissance style
        for y in range(450):
            color_val = clamp_color(100 + 50 * (y / 450))
            surface.fill((color_val, clamp_color(color_val - 20), clamp_color(color_val - 30)), (0, y, 600, 1))

        # Face shape
        pygame.draw.ellipse(surface, (245, 220, 177), (200, 120, 200, 250))

        # Hair
        pygame.draw.ellipse(surface, (101, 67, 33), (180, 100, 240, 180))
        pygame.draw.ellipse(surface, (245, 220, 177), (210, 130, 180, 220))

        # Eyes
        pygame.draw.ellipse(surface, (255, 255, 255), (230, 180, 40, 20))
        pygame.draw.ellipse(surface, (255, 255, 255), (330, 180, 40, 20))
        pygame.draw.ellipse(surface, (101, 67, 33), (240, 185, 20, 10))
        pygame.draw.ellipse(surface, (101, 67, 33), (340, 185, 20, 10))

        # Nose
        pygame.draw.polygon(surface, (235, 210, 167), [(290, 200), (310, 200), (300, 220)])

        # Mouth - the famous smile
        pygame.draw.arc(surface, (200, 100, 100), (270, 230, 60, 30), 0, math.pi, 3)

        # Hands
        pygame.draw.ellipse(surface, (245, 220, 177), (150, 300, 100, 80))
        pygame.draw.ellipse(surface, (245, 220, 177), (350, 320, 100, 60))

        # Dress
        pygame.draw.rect(surface, (60, 60, 100), (180, 280, 240, 170))

        return surface

    def create_starry_night_image(self):
        """Create a Van Gogh Starry Night inspired image."""
        surface = pygame.Surface((600, 450))

        # Night sky with swirls
        for y in range(300):
            blue_val = clamp_color(25 + 30 * math.sin(y / 20))
            surface.fill((blue_val, clamp_color(blue_val + 10), clamp_color(blue_val + 40)), (0, y, 600, 1))

        # Ground/village
        surface.fill((40, 40, 80), (0, 300, 600, 150))

        # Swirls in the sky
        for i in range(8):
            center_x = 100 + i * 60
            center_y = 100 + random.randint(0, 50)
            for radius in range(10, 40, 5):
                color_intensity = clamp_color(100 - radius)
                pygame.draw.circle(surface, (color_intensity, color_intensity, clamp_color(color_intensity + 50)),
                                 (center_x, center_y), radius, 2)

        # Stars
        for i in range(30):
            x = random.randint(0, 600)
            y = random.randint(0, 250)
            pygame.draw.circle(surface, (255, 255, 200), (x, y), 3)

        # Moon
        pygame.draw.circle(surface, (255, 255, 200), (500, 80), 40)

        # Cypress tree (tall dark tree)
        points = [(50, 450), (60, 400), (45, 350), (70, 300), (40, 250), (80, 200),
                  (50, 150), (90, 100), (70, 50), (55, 0), (45, 50), (25, 100),
                  (50, 150), (20, 200), (60, 250), (30, 300), (55, 350), (40, 400)]
        pygame.draw.polygon(surface, (20, 40, 20), points)

        # Village houses
        for i in range(4):
            x = 150 + i * 100
            pygame.draw.rect(surface, (60, 40, 20), (x, 320, 80, 80))
            pygame.draw.polygon(surface, (80, 60, 40), [(x, 320), (x + 40, 300), (x + 80, 320)])
            # Windows
            pygame.draw.rect(surface, (255, 255, 100), (x + 10, 340, 15, 20))
            pygame.draw.rect(surface, (255, 255, 100), (x + 55, 340, 15, 20))

        return surface

    def create_sunflower_image(self):
        """Create a sunflower field image."""
        surface = pygame.Surface((600, 450))
        surface.fill((135, 206, 235))  # Sky

        # Ground
        surface.fill((34, 139, 34), (0, 350, 600, 100))

        # Multiple sunflowers
        sunflower_positions = [(150, 250), (350, 200), (500, 280), (80, 300), (420, 320)]

        for x, y in sunflower_positions:
            size = random.randint(40, 70)

            # Petals
            for angle in range(0, 360, 30):
                petal_x = x + math.cos(math.radians(angle)) * size
                petal_y = y + math.sin(math.radians(angle)) * size
                pygame.draw.ellipse(surface, (255, 215, 0),
                                  (petal_x - 15, petal_y - 8, 30, 16))

            # Center
            pygame.draw.circle(surface, (139, 69, 19), (x, y), size // 2)

            # Seeds pattern
            for i in range(20):
                seed_angle = i * 18
                seed_radius = random.randint(5, size // 3)
                seed_x = x + math.cos(math.radians(seed_angle)) * seed_radius
                seed_y = y + math.sin(math.radians(seed_angle)) * seed_radius
                pygame.draw.circle(surface, (101, 67, 33), (int(seed_x), int(seed_y)), 2)

            # Stem
            pygame.draw.line(surface, (34, 139, 34), (x, y + size // 2), (x, 450), 8)

        # Clouds
        for i in range(3):
            cloud_x = 100 + i * 200
            cloud_y = 50 + random.randint(0, 30)
            pygame.draw.circle(surface, (255, 255, 255), (cloud_x, cloud_y), 30)
            pygame.draw.circle(surface, (255, 255, 255), (cloud_x + 25, cloud_y), 35)
            pygame.draw.circle(surface, (255, 255, 255), (cloud_x + 50, cloud_y), 30)

        return surface

    def create_landscape_image(self):
        """Create a mountain lake landscape."""
        surface = pygame.Surface((600, 450))

        # Sky gradient
        for y in range(200):
            blue = clamp_color(135 + 100 * (1 - y / 200))
            surface.fill((blue, clamp_color(blue + 50), 255), (0, y, 600, 1))

        # Mountains
        mountain_points = [(0, 200), (150, 80), (300, 120), (450, 60), (600, 180), (600, 200)]
        pygame.draw.polygon(surface, (100, 100, 100), mountain_points)

        # Snow caps
        snow_points = [(120, 100), (150, 80), (180, 100)]
        pygame.draw.polygon(surface, (255, 255, 255), snow_points)
        snow_points2 = [(420, 80), (450, 60), (480, 80)]
        pygame.draw.polygon(surface, (255, 255, 255), snow_points2)

        # Lake
        pygame.draw.ellipse(surface, (30, 144, 255), (50, 200, 500, 150))

        # Lake reflection
        for y in range(200, 350):
            alpha = clamp_color(100 * (1 - (y - 200) / 150))
            reflection_surface = pygame.Surface((500, 1))
            reflection_surface.set_alpha(alpha)
            reflection_surface.fill((100, 100, 100))
            surface.blit(reflection_surface, (50, y))

        # Trees
        for i in range(8):
            x = 80 + i * 60
            height = random.randint(40, 80)
            pygame.draw.rect(surface, (139, 69, 19), (x, 200 - height, 10, height))
            pygame.draw.circle(surface, (34, 139, 34), (x + 5, 200 - height), 15)

        return surface

    def create_abstract_image(self):
        """Create a colorful abstract art image."""
        surface = pygame.Surface((600, 450))
        surface.fill((240, 240, 240))

        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                  (255, 0, 255), (0, 255, 255), (255, 165, 0), (128, 0, 128)]

        # Geometric shapes
        for i in range(15):
            color = random.choice(colors)
            shape_type = random.randint(1, 4)
            x = random.randint(0, 500)
            y = random.randint(0, 350)

            if shape_type == 1:  # Circle
                radius = random.randint(20, 80)
                pygame.draw.circle(surface, color, (x, y), radius)
            elif shape_type == 2:  # Rectangle
                w = random.randint(30, 100)
                h = random.randint(30, 100)
                pygame.draw.rect(surface, color, (x, y, w, h))
            elif shape_type == 3:  # Triangle
                points = [(x, y), (x + random.randint(20, 80), y + random.randint(20, 80)),
                         (x - random.randint(20, 80), y + random.randint(20, 80))]
                pygame.draw.polygon(surface, color, points)
            else:  # Lines
                end_x = x + random.randint(-100, 100)
                end_y = y + random.randint(-100, 100)
                pygame.draw.line(surface, color, (x, y), (end_x, end_y), 5)

        return surface

    def create_city_image(self):
        """Create a city skyline image."""
        surface = pygame.Surface((600, 450))

        # Sky gradient (sunset)
        for y in range(300):
            red = clamp_color(255 * (1 - y / 300))
            blue = clamp_color(100 + 155 * (y / 300))
            surface.fill((red, 100, blue), (0, y, 600, 1))

        # Ground
        surface.fill((50, 50, 50), (0, 300, 600, 150))

        # Buildings
        building_heights = [180, 220, 160, 200, 240, 190, 170, 210]
        building_width = 75

        for i, height in enumerate(building_heights):
            x = i * building_width
            y = 300 - height

            # Building
            pygame.draw.rect(surface, (80, 80, 80), (x, y, building_width, height))

            # Windows
            for row in range(height // 25):
                for col in range(building_width // 20):
                    window_x = x + 5 + col * 20
                    window_y = y + 10 + row * 25
                    if random.random() > 0.3:  # Some windows are lit
                        pygame.draw.rect(surface, (255, 255, 100), (window_x, window_y, 10, 15))
                    else:
                        pygame.draw.rect(surface, (30, 30, 30), (window_x, window_y, 10, 15))

        # Sun
        pygame.draw.circle(surface, (255, 200, 0), (500, 100), 40)

        return surface

    def create_ocean_image(self):
        """Create an ocean waves image."""
        surface = pygame.Surface((600, 450))

        # Sky
        surface.fill((135, 206, 235))

        # Ocean layers
        ocean_colors = [(0, 100, 150), (0, 120, 170), (0, 140, 190), (0, 160, 210)]

        for i, color in enumerate(ocean_colors):
            y = 150 + i * 75
            # Create wave effect
            points = [(0, y)]
            for x in range(0, 600, 20):
                wave_y = y + 20 * math.sin((x + i * 50) / 30)
                points.append((x, int(wave_y)))
            points.append((600, 450))
            points.append((0, 450))
            pygame.draw.polygon(surface, color, points)

        # Foam on waves
        for x in range(0, 600, 30):
            foam_y = 200 + 15 * math.sin(x / 20)
            pygame.draw.circle(surface, (255, 255, 255), (x, int(foam_y)), 5)

        # Seagulls
        for i in range(5):
            x = random.randint(100, 500)
            y = random.randint(50, 150)
            # Simple V shape for seagull
            pygame.draw.line(surface, (100, 100, 100), (x - 10, y), (x, y - 5), 2)
            pygame.draw.line(surface, (100, 100, 100), (x, y - 5), (x + 10, y), 2)

        # Clouds
        for i in range(4):
            x = 50 + i * 140
            y = 30 + random.randint(0, 40)
            for j in range(3):
                pygame.draw.circle(surface, (255, 255, 255),
                                 (x + j * 20, y + random.randint(-10, 10)),
                                 random.randint(15, 25))

        return surface

    def load_level(self, level_index):
        """Load a specific puzzle level."""
        if level_index >= len(self.levels):
            return False

        level = self.levels[level_index]
        self.current_image = level.image_url  # This is actually our generated surface
        self.grid_cols, self.grid_rows = level.grid_size
        self.piece_width = self.puzzle_width // self.grid_cols
        self.piece_height = self.puzzle_height // self.grid_rows

        # Scale the generated image
        self.original_image = pygame.transform.scale(self.current_image,
                                                   (self.puzzle_width, self.puzzle_height))

        self.pieces = []
        self.puzzle_complete = False
        self.level_start_time = time.time()

        self.create_pieces()
        self.scramble_pieces()
        return True

    def create_pieces(self):
        """Create puzzle pieces from the current image."""
        piece_id = 0
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                # Extract piece from original image
                piece_rect = pygame.Rect(col * self.piece_width, row * self.piece_height,
                                       self.piece_width, self.piece_height)
                piece_image = self.original_image.subsurface(piece_rect).copy()

                # Correct position in puzzle
                correct_x = self.puzzle_x + col * self.piece_width
                correct_y = self.puzzle_y + row * self.piece_height

                # Create piece
                piece = PuzzlePiece(0, 0, self.piece_width, self.piece_height,
                                  piece_image, correct_x, correct_y, piece_id)
                self.pieces.append(piece)
                piece_id += 1

    def scramble_pieces(self):
        """Scramble pieces more randomly across the pieces area."""
        available_positions = []

        # Create a grid of available positions in the pieces area
        cols = 4
        rows = (len(self.pieces) + cols - 1) // cols  # Ceiling division

        for row in range(rows + 2):  # Add extra rows for more scrambling
            for col in range(cols):
                x = self.pieces_area_x + col * (self.piece_width + 15) + random.randint(-20, 20)
                y = self.pieces_area_y + row * (self.piece_height + 15) + random.randint(-10, 10)
                available_positions.append((x, y))

        # Shuffle the positions
        random.shuffle(available_positions)

        # Assign positions to pieces
        for i, piece in enumerate(self.pieces):
            if not piece.is_placed and i < len(available_positions):
                piece.x, piece.y = available_positions[i]

                # Add some random rotation-like displacement
                piece.x += random.randint(-30, 30)
                piece.y += random.randint(-20, 20)

                # Keep pieces within screen bounds
                piece.x = max(self.pieces_area_x - 50,
                             min(self.screen_width - piece.width, piece.x))
                piece.y = max(50, min(self.screen_height - piece.height - 100, piece.y))

    def calculate_level_score(self):
        """Calculate score based on time and hints used."""
        if not self.level_start_time:
            return 0

        time_taken = time.time() - self.level_start_time
        base_score = self.levels[self.current_level].points

        # Time bonus (faster = more points)
        time_bonus = max(0, base_score // 2 - int(time_taken // 10))

        # Hint penalty
        hint_penalty = self.hints_used * 20

        final_score = max(50, base_score + time_bonus - hint_penalty)
        return final_score

    def complete_level(self):
        """Handle level completion."""
        level_score = self.calculate_level_score()
        self.total_score += level_score
        self.puzzle_complete = True
        self.save_progress()

        print(f"Level {self.current_level + 1} completed!")
        print(f"Score: {level_score} points")
        print(f"Total Score: {self.total_score}")

    def next_level(self):
        """Move to the next level."""
        if self.current_level < len(self.levels) - 1:
            self.current_level += 1
            self.hints_used = 0  # Reset hints for new level
            if self.load_level(self.current_level):
                return True
        return False

    def load_progress(self):
        """Load game progress from file."""
        self.last_hint_time = None
        self.hints_used = 0

        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    if 'last_hint_time' in data:
                        self.last_hint_time = datetime.fromisoformat(data['last_hint_time'])
                    self.hints_used = data.get('hints_used', 0)
                    self.current_level = data.get('current_level', 0)
                    self.total_score = data.get('total_score', 0)
            except:
                pass

    def save_progress(self):
        """Save game progress to file."""
        data = {
            'hints_used': self.hints_used,
            'current_level': self.current_level,
            'total_score': self.total_score
        }
        if self.last_hint_time:
            data['last_hint_time'] = self.last_hint_time.isoformat()

        try:
            with open(self.save_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Could not save progress: {e}")

    def can_use_hint(self):
        """Check if hint can be used (every 2 hours for better gameplay)."""
        if self.last_hint_time is None:
            return True

        time_since_last_hint = datetime.now() - self.last_hint_time
        return time_since_last_hint >= timedelta(hours=2)  # Reduced from 4

    def use_hint(self):
        """Use a hint to reveal a piece's correct position."""
        if not self.can_use_hint():
            return False

        # Find pieces that haven't been revealed as hints yet
        unrevealed_pieces = [p for p in self.pieces if not p.hint_revealed and not p.is_placed]

        if unrevealed_pieces:
            # Reveal a random piece
            piece = random.choice(unrevealed_pieces)
            piece.hint_revealed = True
            self.hints_used += 1
            self.last_hint_time = datetime.now()
            self.save_progress()
            return True

        return False

    def handle_mouse_down(self, pos):
        """Handle mouse button down events."""
        # Check if clicking on UI buttons first
        if self.puzzle_complete and self.next_button_rect.collidepoint(pos):
            if self.current_level < len(self.levels) - 1:
                self.next_level()
            else:
                # Game completed, restart from level 1
                self.current_level = 0
                self.load_level(self.current_level)
            return

        if self.hint_button_rect.collidepoint(pos):
            if self.use_hint():
                print("Hint revealed!")
            else:
                print("Hint not available yet!")
            return

        # Check if clicking on a piece
        for piece in reversed(self.pieces):  # Check from top to bottom
            if piece.contains_point(pos[0], pos[1]) and not piece.is_placed:
                self.selected_piece = piece
                piece.dragging = True
                self.mouse_offset_x = pos[0] - piece.x
                self.mouse_offset_y = pos[1] - piece.y
                # Move selected piece to end of list (draw on top)
                self.pieces.remove(piece)
                self.pieces.append(piece)
                break

    def handle_mouse_up(self, pos):
        """Handle mouse button up events."""
        if self.selected_piece:
            # Check if piece is near its correct position
            if self.selected_piece.is_near_correct_position():
                self.selected_piece.x = self.selected_piece.correct_x
                self.selected_piece.y = self.selected_piece.correct_y
                self.selected_piece.is_placed = True

                # Check if puzzle is complete
                if all(piece.is_placed for piece in self.pieces):
                    self.complete_level()

            self.selected_piece.dragging = False
            self.selected_piece = None

    def handle_mouse_motion(self, pos):
        """Handle mouse motion events."""
        if self.selected_piece and self.selected_piece.dragging:
            self.selected_piece.x = pos[0] - self.mouse_offset_x
            self.selected_piece.y = pos[1] - self.mouse_offset_y

    def draw_hint_overlay(self):
        """Draw hint overlay showing where hinted pieces belong."""
        overlay = pygame.Surface((self.puzzle_width, self.puzzle_height))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))

        for piece in self.pieces:
            if piece.hint_revealed and not piece.is_placed:
                # Draw the piece in its correct position with transparency
                piece_x = piece.correct_x - self.puzzle_x
                piece_y = piece.correct_y - self.puzzle_y
                overlay.blit(piece.image_section, (piece_x, piece_y))

                # Draw a pulsing yellow highlight
                pulse = int(50 + 30 * math.sin(time.time() * 5))
                highlight_color = (255, 255, pulse)
                highlight_rect = pygame.Rect(piece_x - 3, piece_y - 3,
                                           piece.width + 6, piece.height + 6)
                pygame.draw.rect(overlay, highlight_color, highlight_rect, 4)

        if any(piece.hint_revealed and not piece.is_placed for piece in self.pieces):
            self.screen.blit(overlay, (self.puzzle_x, self.puzzle_y))

    def draw_ui(self):
        """Draw the user interface."""
        # Title and level info
        level_info = f"Level {self.current_level + 1}: {self.levels[self.current_level].name}"
        title = self.font.render(level_info, True, (255, 255, 255))
        self.screen.blit(title, (50, 20))

        # Level description
        desc = self.levels[self.current_level].description
        desc_surface = self.small_font.render(desc, True, (200, 200, 200))
        self.screen.blit(desc_surface, (50, 50))

        # Progress
        placed_pieces = sum(1 for piece in self.pieces if piece.is_placed)
        total_pieces = len(self.pieces)
        progress_text = f"Progress: {placed_pieces}/{total_pieces} pieces"
        progress_surface = self.small_font.render(progress_text, True, (255, 255, 255))
        self.screen.blit(progress_surface, (50, 75))

        # Score
        score_text = f"Total Score: {self.total_score}"
        score_surface = self.small_font.render(score_text, True, (255, 215, 0))
        self.screen.blit(score_surface, (300, 20))

        if self.level_start_time:
            current_score = self.calculate_level_score()
            level_score_text = f"Level Score: {current_score}"
            level_score_surface = self.small_font.render(level_score_text, True, (255, 215, 0))
            self.screen.blit(level_score_surface, (300, 45))

        # Difficulty stars
        difficulty = self.levels[self.current_level].difficulty
        stars_text = "★" * difficulty + "☆" * (5 - difficulty)
        stars_surface = self.small_font.render(f"Difficulty: {stars_text}", True, (255, 255, 100))
        self.screen.blit(stars_surface, (300, 70))

        # Hint button
        hint_color = (0, 200, 0) if self.can_use_hint() else (100, 100, 100)
        pygame.draw.rect(self.screen, hint_color, self.hint_button_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.hint_button_rect, 2)

        hint_text = "HINT" if self.can_use_hint() else "WAIT"
        hint_surface = self.small_font.render(hint_text, True, (255, 255, 255))
        hint_rect = hint_surface.get_rect(center=self.hint_button_rect.center)
        self.screen.blit(hint_surface, hint_rect)

        # Hint timer
        if not self.can_use_hint() and self.last_hint_time:
            time_left = timedelta(hours=2) - (datetime.now() - self.last_hint_time)
            hours = int(time_left.total_seconds() // 3600)
            minutes = int((time_left.total_seconds() % 3600) // 60)
            timer_text = f"Next hint: {hours}h {minutes}m"
            timer_surface = self.small_font.render(timer_text, True, (255, 255, 100))
            self.screen.blit(timer_surface, (900, 500))

        # Hints used
        hints_text = f"Hints used: {self.hints_used}"
        hints_surface = self.small_font.render(hints_text, True, (255, 255, 255))
        self.screen.blit(hints_surface, (900, 475))

        # Next level button (only when puzzle is complete)
        if self.puzzle_complete:
            button_color = (0, 150, 0)
            pygame.draw.rect(self.screen, button_color, self.next_button_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), self.next_button_rect, 2)

            button_text = "NEXT LEVEL" if self.current_level < len(self.levels) - 1 else "RESTART"
            next_surface = self.small_font.render(button_text, True, (255, 255, 255))
            next_rect = next_surface.get_rect(center=self.next_button_rect.center)
            self.screen.blit(next_surface, next_rect)

        # Instructions
        instructions = [
            "Drag pieces to assemble the puzzle",
            "Click HINT button for help (every 2 hours)",
            "Green border = correctly placed",
            "Yellow border = hinted piece",
            "Red border = currently dragging"
        ]

        for i, instruction in enumerate(instructions):
            text_surface = self.small_font.render(instruction, True, (180, 180, 180))
            self.screen.blit(text_surface, (50, 600 + i * 20))

        # Level progression indicator
        progress_y = 750
        level_width = 600 // len(self.levels)
        for i, level in enumerate(self.levels):
            x = 50 + i * level_width
            color = (0, 255, 0) if i < self.current_level else (100, 100, 100)
            if i == self.current_level:
                color = (255, 255, 0)

            pygame.draw.rect(self.screen, color, (x, progress_y, level_width - 2, 20))

            # Level number
            if level_width > 30:
                level_text = str(i + 1)
                level_surface = self.small_font.render(level_text, True, (0, 0, 0))
                level_rect = level_surface.get_rect(center=(x + level_width // 2, progress_y + 10))
                self.screen.blit(level_surface, level_rect)

    def draw(self):
        """Main drawing function."""
        self.screen.fill((40, 40, 60))  # Dark blue background

        # Draw puzzle area background
        pygame.draw.rect(self.screen, (80, 80, 100),
                        (self.puzzle_x - 5, self.puzzle_y - 5,
                         self.puzzle_width + 10, self.puzzle_height + 10))
        pygame.draw.rect(self.screen, (120, 120, 140),
                        (self.puzzle_x, self.puzzle_y, self.puzzle_width, self.puzzle_height))

        # Draw hint overlay first (behind pieces)
        self.draw_hint_overlay()

        # Draw pieces
        for piece in self.pieces:
            if piece.hint_revealed and not piece.is_placed:
                piece.draw(self.screen, alpha=220)  # Slightly transparent for hints
            else:
                piece.draw(self.screen)

        # Draw UI
        self.draw_ui()

        # Win message
        if self.puzzle_complete:
            if self.current_level >= len(self.levels) - 1:
                win_text = "🎉 ALL LEVELS COMPLETE! 🎉"
                color = (255, 215, 0)  # Gold
            else:
                win_text = "🎉 LEVEL COMPLETE! 🎉"
                color = (0, 255, 0)  # Green

            win_surface = self.large_font.render(win_text, True, color)
            win_rect = win_surface.get_rect(center=(self.screen_width // 2, 400))

            # Draw background for text
            bg_rect = win_rect.inflate(40, 20)
            # Create a surface for transparency
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(180)
            bg_surface.fill((0, 0, 0))
            self.screen.blit(bg_surface, bg_rect)
            pygame.draw.rect(self.screen, color, bg_rect, 3)

            self.screen.blit(win_surface, win_rect)

            # Show level score
            if hasattr(self, 'level_start_time') and self.level_start_time:
                level_score = self.calculate_level_score()
                score_text = f"Level Score: +{level_score} points!"
                score_surface = self.font.render(score_text, True, (255, 255, 255))
                score_rect = score_surface.get_rect(center=(self.screen_width // 2, 440))
                self.screen.blit(score_surface, score_rect)

    def run(self):
        """Main game loop."""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_mouse_down(event.pos)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left click release
                        self.handle_mouse_up(event.pos)

                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h:  # Hint key
                        if self.use_hint():
                            print("Hint revealed!")
                        else:
                            print("Hint not available yet!")
                    elif event.key == pygame.K_n and self.puzzle_complete:  # Next level shortcut
                        if self.current_level < len(self.levels) - 1:
                            self.next_level()
                        else:
                            self.current_level = 0
                            self.load_level(self.current_level)

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    print("Starting Jigsaw Puzzle Adventure...")
    print("Features:")
    print("- 8 unique levels with different themes")
    print("- Scoring system with time bonuses")
    print("- Hint system (every 2 hours)")
    print("- Progressive difficulty")
    print("- Save/load progress")
    print("\nControls:")
    print("- Mouse: Click and drag pieces")
    print("- H key: Use hint")
    print("- N key: Next level (when complete)")
    print("\nStarting game...")

    try:
        game = JigsawPuzzle()
        game.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        