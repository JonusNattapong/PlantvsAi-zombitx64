# Tictactoe-zombitx64

A Tic-tac-toe game with an AI opponent implemented using Python and Pygame.

## Features

- Interactive 3x3 Tic-tac-toe board
- Player vs AI gameplay
- AI opponent using minimax algorithm (unbeatable)
- Clean, modern user interface
- Game state tracking (win, lose, draw)
- Restart functionality

## How to Play

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Run the game:
   ```
   python tictactoe.py
   ```

3. Game Controls:
   - Click on a square to place an 'O'
   - AI will automatically place 'X' after your move
   - Press 'r' to restart the game

## Technical Details

The AI opponent uses the minimax algorithm, which is a decision-making algorithm that recursively searches through all possible game states to determine the optimal move, assuming both players play optimally.