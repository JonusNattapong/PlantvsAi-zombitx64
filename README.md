# Tictactoe-zombitx64

A Tic-tac-toe game with multiple AI opponent strategies implemented using Python and Pygame.

## Features

- Interactive 3x3 Tic-tac-toe board
- Player vs AI gameplay 
- Four different AI strategies:
  1. **Minimax Algorithm**: Traditional unbeatable algorithm
  2. **Q-Learning (Reinforcement Learning)**: AI that learns from experience
  3. **Neural Network**: Deep learning approach using TensorFlow
  4. **Pattern Recognition**: Analyzes and adapts to player patterns
- Game statistics tracking
- Real-time performance analysis
- Strategy switching during gameplay
- Modern user interface

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
   - Click on the AI strategy buttons at the bottom to change AI opponents
   - Press 'r' to restart the game

## AI Approaches

### Minimax Algorithm
The classic approach that recursively searches through all possible game states to determine the optimal move, always resulting in a draw or AI win if played optimally.

### Q-Learning (Reinforcement Learning)
- Uses a Q-table to store state-action values
- Learns by playing and adjusting Q-values based on game outcomes
- Improves over time through exploration and exploitation

### Neural Network
- Implemented with TensorFlow
- Trained to predict optimal moves based on board state
- Learning progress displayed in real-time statistics

### Pattern Recognition
- Analyzes and records player move patterns
- Builds a database of strategies and counter-responses
- Adapts to individual player styles

## Technical Details

The game demonstrates multiple AI concepts:
- Game theory and decision trees (Minimax)
- Reinforcement learning principles (Q-Learning)
- Neural networks for strategic decision-making
- Pattern recognition and adaptive learning

Game statistics and AI model data are saved between sessions for continuous learning.