import pygame
import random
import math
import time
import json
import os
from datetime import datetime, timedelta

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
        
    def draw(self, screen, alpha=255):
        if self.image_section:
            temp_surface = self.image_section.copy()
            temp_surface.set_alpha(alpha)
            screen.blit(temp_surface, (self.x, self.y))
            
            # Draw border
            color = (0, 255, 0) if self.is_placed else (255, 255, 255)
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), 2)
    
    def contains_point(self, px, py):
        return (self.x <= px <= self.x + self.width and 
                self.y <= py <= self.y + self.height)
    
    def is_near_correct_position(self, tolerance=30):
        return (abs(self.x - self.correct_x) < tolerance and 
                abs(self.y - self.correct_y) < tolerance)

class JigsawPuzzle:
    def __init__(self, image_path, grid_size=(4, 3)):
        pygame.init()
        self.screen_width = 1200
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Jigsaw Puzzle Game")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Load and scale image
        self.original_image = pygame.image.load(image_path)
        self.puzzle_width = 600
        self.puzzle_height = 450
        self.original_image = pygame.transform.scale(self.original_image, 
                                                   (self.puzzle_width, self.puzzle_height))
        
        self.grid_cols, self.grid_rows = grid_size
        self.piece_width = self.puzzle_width // self.grid_cols
        self.piece_height = self.puzzle_height // self.grid_rows
        
        # Puzzle area (left side)
        self.puzzle_x = 50
        self.puzzle_y = 100
        
        # Pieces area (right side)
        self.pieces_area_x = 700
        self.pieces_area_y = 100
        
        self.pieces = []
        self.selected_piece = None
        self.mouse_offset_x = 0
        self.mouse_offset_y = 0
        
        # Hint system
        self.save_file = "puzzle_progress.json"
        self.load_progress()
        
        self.create_pieces()
        self.shuffle_pieces()
        
    def create_pieces(self):
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
    
    def shuffle_pieces(self):
        # Place pieces randomly in the pieces area
        for i, piece in enumerate(self.pieces):
            if not piece.is_placed:
                piece.x = self.pieces_area_x + (i % 4) * (self.piece_width + 10)
                piece.y = self.pieces_area_y + (i // 4) * (self.piece_height + 10)
    
    def load_progress(self):
        self.last_hint_time = None
        self.hints_used = 0
        
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    if 'last_hint_time' in data:
                        self.last_hint_time = datetime.fromisoformat(data['last_hint_time'])
                    self.hints_used = data.get('hints_used', 0)
            except:
                pass
    
    def save_progress(self):
        data = {
            'hints_used': self.hints_used
        }
        if self.last_hint_time:
            data['last_hint_time'] = self.last_hint_time.isoformat()
        
        with open(self.save_file, 'w') as f:
            json.dump(data, f)
    
    def can_use_hint(self):
        if self.last_hint_time is None:
            return True
        
        time_since_last_hint = datetime.now() - self.last_hint_time
        return time_since_last_hint >= timedelta(hours=4)
    
    def use_hint(self):
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
        if self.selected_piece:
            # Check if piece is near its correct position
            if self.selected_piece.is_near_correct_position():
                self.selected_piece.x = self.selected_piece.correct_x
                self.selected_piece.y = self.selected_piece.correct_y
                self.selected_piece.is_placed = True
            
            self.selected_piece.dragging = False
            self.selected_piece = None
    
    def handle_mouse_motion(self, pos):
        if self.selected_piece and self.selected_piece.dragging:
            self.selected_piece.x = pos[0] - self.mouse_offset_x
            self.selected_piece.y = pos[1] - self.mouse_offset_y
    
    def draw_hint_overlay(self):
        # Draw semi-transparent overlay showing the complete picture for hinted pieces
        overlay = pygame.Surface((self.puzzle_width, self.puzzle_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        
        for piece in self.pieces:
            if piece.hint_revealed and not piece.is_placed:
                # Draw the piece in its correct position with transparency
                piece_x = piece.correct_x - self.puzzle_x
                piece_y = piece.correct_y - self.puzzle_y
                overlay.blit(piece.image_section, (piece_x, piece_y))
        
        self.screen.blit(overlay, (self.puzzle_x, self.puzzle_y))
    
    def draw_ui(self):
        # Title
        title = self.font.render("Jigsaw Puzzle Game", True, (255, 255, 255))
        self.screen.blit(title, (50, 20))
        
        # Progress
        placed_pieces = sum(1 for piece in self.pieces if piece.is_placed)
        total_pieces = len(self.pieces)
        progress_text = f"Progress: {placed_pieces}/{total_pieces} pieces"
        progress_surface = self.small_font.render(progress_text, True, (255, 255, 255))
        self.screen.blit(progress_surface, (50, 60))
        
        # Hint button and timer
        hint_y = 600
        if self.can_use_hint():
            hint_text = "Click H for Hint (Available)"
            color = (0, 255, 0)
        else:
            time_left = timedelta(hours=4) - (datetime.now() - self.last_hint_time)
            hours = int(time_left.total_seconds() // 3600)
            minutes = int((time_left.total_seconds() % 3600) // 60)
            hint_text = f"Next hint in: {hours}h {minutes}m"
            color = (255, 255, 0)
        
        hint_surface = self.small_font.render(hint_text, True, color)
        self.screen.blit(hint_surface, (50, hint_y))
        
        # Hints used
        hints_text = f"Hints used: {self.hints_used}"
        hints_surface = self.small_font.render(hints_text, True, (255, 255, 255))
        self.screen.blit(hints_surface, (50, hint_y + 30))
        
        # Instructions
        instructions = [
            "Drag pieces to assemble the puzzle",
            "Press H for hints (every 4 hours)",
            "Green border = correctly placed"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = self.small_font.render(instruction, True, (200, 200, 200))
            self.screen.blit(text_surface, (700, 500 + i * 25))
    
    def draw(self):
        self.screen.fill((50, 50, 50))
        
        # Draw puzzle area background
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (self.puzzle_x, self.puzzle_y, self.puzzle_width, self.puzzle_height))
        
        # Draw hint overlay first
        self.draw_hint_overlay()
        
        # Draw pieces
        for piece in self.pieces:
            if piece.hint_revealed and not piece.is_placed:
                piece.draw(self.screen, alpha=180)  # Semi-transparent for hints
            else:
                piece.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        # Check win condition
        if all(piece.is_placed for piece in self.pieces):
            win_text = self.font.render("Congratulations! Puzzle Complete!", True, (0, 255, 0))
            text_rect = win_text.get_rect(center=(self.screen_width // 2, 50))
            self.screen.blit(win_text, text_rect)
    
    def run(self):
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
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    # You'll need to provide an image file
    try:
        game = JigsawPuzzle("puzzle_image.jpg")
        game.run()
    except pygame.error:
        print("Error: Could not load 'puzzle_image.jpg'")
        print("Please add an image file named 'puzzle_image.jpg' to the same directory")