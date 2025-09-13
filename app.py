from flask import Flask, render_template, jsonify, request, session
import random
import math
import time
import json
import os
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Any, Optional, Tuple
import base64
from io import BytesIO
from PIL import Image, ImageDraw
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

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
        self.image_section = image_section  # Will be base64 encoded image data
        self.correct_x = correct_x
        self.correct_y = correct_y
        self.piece_id = piece_id
        self.is_placed = False
        self.dragging = False
        self.hint_revealed = False
        self.rotation = 0

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'image_section': self.image_section,
            'correct_x': self.correct_x,
            'correct_y': self.correct_y,
            'piece_id': self.piece_id,
            'is_placed': self.is_placed,
            'dragging': self.dragging,
            'hint_revealed': self.hint_revealed,
            'rotation': self.rotation
        }

    def contains_point(self, px, py):
        return (self.x <= px <= self.x + self.width and
                self.y <= py <= self.y + self.height)

    def is_near_correct_position(self, tolerance=30):
        return (abs(self.x - self.correct_x) < tolerance and
                abs(self.y - self.correct_y) < tolerance)

class JigsawPuzzleGame:
    def __init__(self):
        self.screen_width = 1200
        self.screen_height = 800

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

        # Hint system
        self.save_file = "puzzle_progress.json"
        self.load_progress()

        # Load first level
        self.load_level(self.current_level)

    def create_levels(self):
        """Create puzzle levels with different themes and difficulties."""
        return [
            PuzzleLevel("Cute Cat", "cat", "Adorable orange tabby cat", 1, (3, 2), 100),
            PuzzleLevel("Mona Lisa", "monalisa", "Leonardo da Vinci's masterpiece", 2, (4, 3), 200),
            PuzzleLevel("Starry Night", "starry_night", "Van Gogh's swirling sky", 3, (4, 3), 300),
            PuzzleLevel("Sunflowers", "sunflower", "Bright yellow sunflower field", 2, (3, 3), 250),
            PuzzleLevel("Mountain Lake", "landscape", "Serene mountain reflection", 3, (5, 3), 350),
            PuzzleLevel("Abstract Art", "abstract", "Colorful geometric patterns", 4, (4, 4), 400),
            PuzzleLevel("City Skyline", "city", "Modern urban landscape", 4, (5, 4), 450),
            PuzzleLevel("Ocean Waves", "ocean", "Crashing ocean waves", 5, (6, 4), 500),
        ]

    def create_image(self, image_type):
        """Create different types of images using PIL."""
        img = Image.new('RGB', (600, 450), color=(135, 206, 235))
        draw = ImageDraw.Draw(img)

        if image_type == "cat":
            return self.create_cat_image_pil(img, draw)
        elif image_type == "monalisa":
            return self.create_monalisa_image_pil(img, draw)
        elif image_type == "starry_night":
            return self.create_starry_night_image_pil(img, draw)
        elif image_type == "sunflower":
            return self.create_sunflower_image_pil(img, draw)
        elif image_type == "landscape":
            return self.create_landscape_image_pil(img, draw)
        elif image_type == "abstract":
            return self.create_abstract_image_pil(img, draw)
        elif image_type == "city":
            return self.create_city_image_pil(img, draw)
        elif image_type == "ocean":
            return self.create_ocean_image_pil(img, draw)

        return img

    def create_cat_image_pil(self, img, draw):
        """Create a stylized cat image using PIL."""
        # Background
        draw.rectangle([0, 0, 600, 450], fill=(135, 206, 235))

        # Cat body (orange)
        draw.ellipse([200, 200, 400, 350], fill=(255, 140, 0))

        # Cat head
        draw.ellipse([220, 100, 380, 260], fill=(255, 140, 0))

        # Cat ears
        draw.polygon([(250, 120), (270, 160), (290, 140)], fill=(255, 140, 0))
        draw.polygon([(310, 140), (330, 160), (350, 120)], fill=(255, 140, 0))

        # Eyes
        draw.ellipse([265, 155, 295, 185], fill=(34, 139, 34))
        draw.ellipse([305, 155, 335, 185], fill=(34, 139, 34))
        draw.ellipse([272, 162, 288, 178], fill=(0, 0, 0))
        draw.ellipse([312, 162, 328, 178], fill=(0, 0, 0))

        # Nose
        draw.polygon([(295, 185), (305, 185), (300, 195)], fill=(255, 20, 147))

        # Stripes
        for i in range(5):
            y = 150 + i * 20
            draw.line([(250, y), (350, y)], fill=(200, 100, 0), width=3)

        # Grass
        for x in range(0, 600, 20):
            for blade in range(3):
                blade_x = x + random.randint(0, 15)
                draw.line([(blade_x, 400), (blade_x, 380 + random.randint(0, 20))],
                         fill=(34, 139, 34), width=2)

        return img

    def create_monalisa_image_pil(self, img, draw):
        """Create a simplified Mona Lisa inspired image."""
        # Background gradient effect
        for y in range(450):
            color_val = clamp_color(100 + 50 * (y / 450))
            draw.rectangle([0, y, 600, y+1], fill=(color_val, clamp_color(color_val - 20), clamp_color(color_val - 30)))

        # Face
        draw.ellipse([200, 120, 400, 370], fill=(245, 220, 177))

        # Hair
        draw.ellipse([180, 100, 420, 280], fill=(101, 67, 33))
        draw.ellipse([210, 130, 390, 350], fill=(245, 220, 177))

        # Eyes
        draw.ellipse([230, 180, 270, 200], fill=(255, 255, 255))
        draw.ellipse([330, 180, 370, 200], fill=(255, 255, 255))
        draw.ellipse([240, 185, 260, 195], fill=(101, 67, 33))
        draw.ellipse([340, 185, 360, 195], fill=(101, 67, 33))

        # Nose
        draw.polygon([(290, 200), (310, 200), (300, 220)], fill=(235, 210, 167))

        # Dress
        draw.rectangle([180, 280, 420, 450], fill=(60, 60, 100))

        return img

    def create_starry_night_image_pil(self, img, draw):
        """Create a Van Gogh Starry Night inspired image."""
        # Night sky
        for y in range(300):
            blue_val = clamp_color(25 + 30 * math.sin(y / 20))
            draw.rectangle([0, y, 600, y+1], fill=(blue_val, clamp_color(blue_val + 10), clamp_color(blue_val + 40)))

        # Ground
        draw.rectangle([0, 300, 600, 450], fill=(40, 40, 80))

        # Stars
        for i in range(30):
            x = random.randint(0, 600)
            y = random.randint(0, 250)
            draw.ellipse([x-3, y-3, x+3, y+3], fill=(255, 255, 200))

        # Moon
        draw.ellipse([460, 40, 540, 120], fill=(255, 255, 200))

        # Village houses
        for i in range(4):
            x = 150 + i * 100
            draw.rectangle([x, 320, x+80, 400], fill=(60, 40, 20))
            draw.polygon([(x, 320), (x + 40, 300), (x + 80, 320)], fill=(80, 60, 40))
            # Windows
            draw.rectangle([x+10, 340, x+25, 360], fill=(255, 255, 100))
            draw.rectangle([x+55, 340, x+70, 360], fill=(255, 255, 100))

        return img

    def create_sunflower_image_pil(self, img, draw):
        """Create a sunflower field image."""
        # Sky
        draw.rectangle([0, 0, 600, 350], fill=(135, 206, 235))

        # Ground
        draw.rectangle([0, 350, 600, 450], fill=(34, 139, 34))

        # Sunflowers
        sunflower_positions = [(150, 250), (350, 200), (500, 280), (80, 300), (420, 320)]

        for x, y in sunflower_positions:
            size = random.randint(40, 70)

            # Petals (simplified as circles around center)
            for angle in range(0, 360, 45):
                petal_x = x + math.cos(math.radians(angle)) * size
                petal_y = y + math.sin(math.radians(angle)) * size
                draw.ellipse([petal_x-15, petal_y-8, petal_x+15, petal_y+8], fill=(255, 215, 0))

            # Center
            draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=(139, 69, 19))

            # Stem
            draw.line([(x, y + size // 2), (x, 450)], fill=(34, 139, 34), width=8)

        # Clouds
        for i in range(3):
            cloud_x = 100 + i * 200
            cloud_y = 50 + random.randint(0, 30)
            draw.ellipse([cloud_x-30, cloud_y-30, cloud_x+30, cloud_y+30], fill=(255, 255, 255))
            draw.ellipse([cloud_x-5, cloud_y-35, cloud_x+55, cloud_y+35], fill=(255, 255, 255))
            draw.ellipse([cloud_x+20, cloud_y-30, cloud_x+80, cloud_y+30], fill=(255, 255, 255))

        return img

    def create_landscape_image_pil(self, img, draw):
        """Create a mountain lake landscape."""
        # Sky gradient
        for y in range(200):
            blue = clamp_color(135 + 100 * (1 - y / 200))
            draw.rectangle([0, y, 600, y+1], fill=(blue, clamp_color(blue + 50), 255))

        # Mountains
        draw.polygon([(0, 200), (150, 80), (300, 120), (450, 60), (600, 180), (600, 200)], fill=(100, 100, 100))

        # Snow caps
        draw.polygon([(120, 100), (150, 80), (180, 100)], fill=(255, 255, 255))
        draw.polygon([(420, 80), (450, 60), (480, 80)], fill=(255, 255, 255))

        # Lake
        draw.ellipse([50, 200, 550, 350], fill=(30, 144, 255))

        # Trees
        for i in range(8):
            x = 80 + i * 60
            height = random.randint(40, 80)
            draw.rectangle([x, 200 - height, x + 10, 200], fill=(139, 69, 19))
            draw.ellipse([x-10, 200 - height - 15, x + 20, 200 - height + 15], fill=(34, 139, 34))

        return img

    def create_abstract_image_pil(self, img, draw):
        """Create a colorful abstract art image."""
        draw.rectangle([0, 0, 600, 450], fill=(240, 240, 240))

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
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
            elif shape_type == 2:  # Rectangle
                w = random.randint(30, 100)
                h = random.randint(30, 100)
                draw.rectangle([x, y, x+w, y+h], fill=color)
            elif shape_type == 3:  # Triangle
                points = [(x, y), (x + random.randint(20, 80), y + random.randint(20, 80)),
                         (x - random.randint(20, 80), y + random.randint(20, 80))]
                draw.polygon(points, fill=color)
            else:  # Lines
                end_x = x + random.randint(-100, 100)
                end_y = y + random.randint(-100, 100)
                draw.line([(x, y), (end_x, end_y)], fill=color, width=5)

        return img

    def create_city_image_pil(self, img, draw):
        """Create a city skyline image."""
        # Sky gradient (sunset)
        for y in range(300):
            red = clamp_color(255 * (1 - y / 300))
            blue = clamp_color(100 + 155 * (y / 300))
            draw.rectangle([0, y, 600, y+1], fill=(red, 100, blue))

        # Ground
        draw.rectangle([0, 300, 600, 450], fill=(50, 50, 50))

        # Buildings
        building_heights = [180, 220, 160, 200, 240, 190, 170, 210]
        building_width = 75

        for i, height in enumerate(building_heights):
            x = i * building_width
            y = 300 - height

            # Building
            draw.rectangle([x, y, x + building_width, 300], fill=(80, 80, 80))

            # Windows
            for row in range(height // 25):
                for col in range(building_width // 20):
                    window_x = x + 5 + col * 20
                    window_y = y + 10 + row * 25
                    if random.random() > 0.3:  # Some windows are lit
                        draw.rectangle([window_x, window_y, window_x + 10, window_y + 15], fill=(255, 255, 100))
                    else:
                        draw.rectangle([window_x, window_y, window_x + 10, window_y + 15], fill=(30, 30, 30))

        # Sun
        draw.ellipse([460, 60, 540, 140], fill=(255, 200, 0))

        return img

    def create_ocean_image_pil(self, img, draw):
        """Create an ocean waves image."""
        # Sky
        draw.rectangle([0, 0, 600, 150], fill=(135, 206, 235))

        # Ocean layers
        ocean_colors = [(0, 100, 150), (0, 120, 170), (0, 140, 190), (0, 160, 210)]

        for i, color in enumerate(ocean_colors):
            y = 150 + i * 75
            draw.rectangle([0, y, 600, y + 75], fill=color)

        # Clouds
        for i in range(4):
            x = 50 + i * 140
            y = 30 + random.randint(0, 40)
            for j in range(3):
                draw.ellipse([x + j * 20 - 15, y + random.randint(-10, 10) - 15,
                            x + j * 20 + 15, y + random.randint(-10, 10) + 15], fill=(255, 255, 255))

        return img

    def image_to_base64(self, pil_image):
        """Convert PIL image to base64 string."""
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

    def load_level(self, level_index):
        """Load a specific puzzle level."""
        if level_index >= len(self.levels):
            return False

        level = self.levels[level_index]
        self.grid_cols, self.grid_rows = level.grid_size
        self.piece_width = self.puzzle_width // self.grid_cols
        self.piece_height = self.puzzle_height // self.grid_rows

        # Generate the image
        pil_image = self.create_image(level.image_url)
        pil_image = pil_image.resize((self.puzzle_width, self.puzzle_height))
        self.original_image_base64 = self.image_to_base64(pil_image)

        self.pieces = []
        self.puzzle_complete = False
        self.level_start_time = time.time()

        self.create_pieces(pil_image)
        self.scramble_pieces()
        return True

    def create_pieces(self, pil_image):
        """Create puzzle pieces from the current image."""
        piece_id = 0
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                # Extract piece from original image
                left = col * self.piece_width
                top = row * self.piece_height
                right = left + self.piece_width
                bottom = top + self.piece_height

                piece_image = pil_image.crop((left, top, right, bottom))
                piece_base64 = self.image_to_base64(piece_image)

                # Correct position in puzzle
                correct_x = self.puzzle_x + col * self.piece_width
                correct_y = self.puzzle_y + row * self.piece_height

                # Create piece
                piece = PuzzlePiece(0, 0, self.piece_width, self.piece_height,
                                  piece_base64, correct_x, correct_y, piece_id)
                self.pieces.append(piece)
                piece_id += 1

    def scramble_pieces(self):
        """Scramble pieces randomly across the pieces area."""
        available_positions = []
        cols = 4
        rows = (len(self.pieces) + cols - 1) // cols

        for row in range(rows + 2):
            for col in range(cols):
                x = self.pieces_area_x + col * (self.piece_width + 15) + random.randint(-20, 20)
                y = self.pieces_area_y + row * (self.piece_height + 15) + random.randint(-10, 10)
                available_positions.append((x, y))

        random.shuffle(available_positions)

        for i, piece in enumerate(self.pieces):
            if not piece.is_placed and i < len(available_positions):
                piece.x, piece.y = available_positions[i]
                piece.x += random.randint(-30, 30)
                piece.y += random.randint(-20, 20)
                piece.x = max(self.pieces_area_x - 50, min(self.screen_width - piece.width, piece.x))
                piece.y = max(50, min(self.screen_height - piece.height - 100, piece.y))

    def calculate_level_score(self):
        """Calculate score based on time and hints used."""
        if not self.level_start_time:
            return 0

        time_taken = time.time() - self.level_start_time
        base_score = self.levels[self.current_level].points
        time_bonus = max(0, base_score // 2 - int(time_taken // 10))
        hint_penalty = self.hints_used * 20
        final_score = max(50, base_score + time_bonus - hint_penalty)
        return final_score

    def complete_level(self):
        """Handle level completion."""
        level_score = self.calculate_level_score()
        self.total_score += level_score
        self.puzzle_complete = True
        self.save_progress()
        return level_score

    def next_level(self):
        """Move to the next level."""
        if self.current_level < len(self.levels) - 1:
            self.current_level += 1
            self.hints_used = 0
            if self.load_level(self.current_level):
                return True
        return False

    def load_progress(self):
        """Load game progress from session and file."""
        self.last_hint_time = session.get('last_hint_time')
        if self.last_hint_time:
            self.last_hint_time = datetime.fromisoformat(self.last_hint_time)
        else:
            self.last_hint_time = None

        self.hints_used = session.get('hints_used', 0)
        self.current_level = session.get('current_level', 0)
        self.total_score = session.get('total_score', 0)

    def save_progress(self):
        """Save game progress to session."""
        session['hints_used'] = self.hints_used
        session['current_level'] = self.current_level
        session['total_score'] = self.total_score
        if self.last_hint_time:
            session['last_hint_time'] = self.last_hint_time.isoformat()

    def can_use_hint(self):
        """Check if hint can be used (every 2 hours)."""
        if self.last_hint_time is None:
            return True
        time_since_last_hint = datetime.now() - self.last_hint_time
        return time_since_last_hint >= timedelta(hours=2)

    def use_hint(self):
        """Use a hint to reveal a piece's correct position."""
        if not self.can_use_hint():
            return False

        unrevealed_pieces = [p for p in self.pieces if not p.hint_revealed and not p.is_placed]
        if unrevealed_pieces:
            piece = random.choice(unrevealed_pieces)
            piece.hint_revealed = True
            self.hints_used += 1
            self.last_hint_time = datetime.now()
            self.save_progress()
            return True
        return False

    def get_game_state(self):
        """Get current game state as dictionary."""
        return {
            'pieces': [piece.to_dict() for piece in self.pieces],
            'current_level': self.current_level,
            'level_info': asdict(self.levels[self.current_level]),
            'total_score': self.total_score,
            'puzzle_complete': self.puzzle_complete,
            'hints_used': self.hints_used,
            'can_use_hint': self.can_use_hint(),
            'original_image': self.original_image_base64,
            'puzzle_dimensions': {
                'width': self.puzzle_width,
                'height': self.puzzle_height,
                'x': self.puzzle_x,
                'y': self.puzzle_y
            },
            'pieces_area': {
                'x': self.pieces_area_x,
                'y': self.pieces_area_y
            }
        }

# Global game instance
game = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game_state')
def get_game_state():
    global game
    if game is None:
        game = JigsawPuzzleGame()
    return jsonify(game.get_game_state())

@app.route('/api/move_piece', methods=['POST'])
def move_piece():
    global game
    if game is None:
        return jsonify({'error': 'Game not initialized'}), 400

    data = request.json
    piece_id = data.get('piece_id')
    x = data.get('x')
    y = data.get('y')

    if piece_id is not None and x is not None and y is not None:
        for piece in game.pieces:
            if piece.piece_id == piece_id and not piece.is_placed:
                piece.x = x
                piece.y = y

                # Check if piece is near correct position
                if piece.is_near_correct_position():
                    piece.x = piece.correct_x
                    piece.y = piece.correct_y
                    piece.is_placed = True

                    # Check if puzzle is complete
                    if all(p.is_placed for p in game.pieces):
                        level_score = game.complete_level()
                        return jsonify({
                            'success': True,
                            'piece_placed': True,
                            'puzzle_complete': True,
                            'level_score': level_score,
                            'game_state': game.get_game_state()
                        })
                    else:
                        return jsonify({
                            'success': True,
                            'piece_placed': True,
                            'puzzle_complete': False,
                            'game_state': game.get_game_state()
                        })
                break

        return jsonify({'success': True, 'game_state': game.get_game_state()})

    return jsonify({'error': 'Invalid data'}), 400

@app.route('/api/use_hint', methods=['POST'])
def use_hint():
    global game
    if game is None:
        return jsonify({'error': 'Game not initialized'}), 400

    if game.use_hint():
        return jsonify({
            'success': True,
            'message': 'Hint revealed!',
            'game_state': game.get_game_state()
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Hint not available yet!',
            'game_state': game.get_game_state()
        })

@app.route('/api/next_level', methods=['POST'])
def next_level():
    global game
    if game is None:
        return jsonify({'error': 'Game not initialized'}), 400

    if game.puzzle_complete:
        if game.current_level < len(game.levels) - 1:
            game.next_level()
        else:
            # Restart from level 1
            game.current_level = 0
            game.load_level(game.current_level)

        return jsonify({
            'success': True,
            'game_state': game.get_game_state()
        })

    return jsonify({'error': 'Level not complete'}), 400

@app.route('/api/reset_game', methods=['POST'])
def reset_game():
    global game
    game = JigsawPuzzleGame()
    return jsonify({
        'success': True,
        'game_state': game.get_game_state()
    })

if __name__ == '__main__':
    app.run(debug=True)
