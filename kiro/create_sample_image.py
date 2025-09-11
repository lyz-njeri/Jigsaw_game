import pygame
import random

def create_sample_puzzle_image():
    """Create a colorful sample image for testing the puzzle game"""
    pygame.init()
    
    width, height = 600, 450
    surface = pygame.Surface((width, height))
    
    # Create a gradient background
    for y in range(height):
        color_value = int(255 * (y / height))
        color = (color_value, 100, 255 - color_value)
        pygame.draw.line(surface, color, (0, y), (width, y))
    
    # Add some geometric shapes for visual interest
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    
    # Draw circles
    for i in range(8):
        x = random.randint(50, width - 50)
        y = random.randint(50, height - 50)
        radius = random.randint(20, 60)
        color = random.choice(colors)
        pygame.draw.circle(surface, color, (x, y), radius)
    
    # Draw rectangles
    for i in range(6):
        x = random.randint(0, width - 100)
        y = random.randint(0, height - 80)
        w = random.randint(40, 100)
        h = random.randint(30, 80)
        color = random.choice(colors)
        pygame.draw.rect(surface, color, (x, y, w, h))
    
    # Add some text
    font = pygame.font.Font(None, 48)
    text = font.render("PUZZLE", True, (255, 255, 255))
    text_rect = text.get_rect(center=(width // 2, height // 2))
    surface.blit(text, text_rect)
    
    # Save the image
    pygame.image.save(surface, "puzzle_image.jpg")
    print("Sample puzzle image created: puzzle_image.jpg")
    
    pygame.quit()

if __name__ == "__main__":
    create_sample_puzzle_image()