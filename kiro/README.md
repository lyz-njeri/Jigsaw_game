# Jigsaw Puzzle Game

A Python-based jigsaw puzzle game with a hint system that reveals parts of the complete picture every 4 hours.

## Features

- **Interactive Puzzle**: Drag and drop pieces to solve the puzzle
- **Hint System**: Get hints every 4 hours that reveal pieces in their correct positions
- **Progress Tracking**: See how many pieces you've placed correctly
- **Auto-Save**: Game automatically saves your hint usage and timing
- **Visual Feedback**: Green borders indicate correctly placed pieces

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Add your puzzle image:
   - Place an image file named `puzzle_image.jpg` in the same directory
   - Supported formats: JPG, PNG, BMP, GIF

3. Run the game:
```bash
python jigsaw_puzzle.py
```

## How to Play

- **Drag pieces** from the right side to the puzzle area on the left
- **Drop pieces** near their correct position to snap them into place
- **Press 'H'** to use a hint (available every 4 hours)
- **Green borders** indicate correctly placed pieces
- Complete the puzzle by placing all pieces correctly

## Hint System

- Hints are available every 4 hours
- Each hint reveals one piece in its correct position with transparency
- The game tracks your hint usage and saves progress
- Revealed pieces help you see the bigger picture of what you're solving

## Customization

You can modify the puzzle difficulty by changing the grid size in the code:
```python
game = JigsawPuzzle("puzzle_image.jpg", grid_size=(6, 4))  # 6x4 = 24 pieces
```

Default is 4x3 (12 pieces) for easier gameplay.