import numpy as np
import tensorflow as tf
from tensorflow import keras
import os
import json

class NeuralNetworkAgent:
    def __init__(self, load_existing=True):
        """
        Initialize neural network agent
        load_existing: whether to load an existing model if available
        """
        self.model_file = 'tictactoe_model'
        self.history_file = 'training_history.json'
        self.game_history = []
        self.training_stats = {
            'games_played': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'training_history': []
        }
        
        if load_existing and os.path.exists(self.model_file):
            try:
                self.model = keras.models.load_model(self.model_file)
                print("Loaded existing model")
                self.load_training_stats()
            except:
                print("Error loading model, creating new one")
                self.create_model()
        else:
            self.create_model()
    
    def create_model(self):
        """Create a new neural network model"""
        # Input: 9 cells in the board (3x3)
        # Each cell is represented by: empty (0), player (1), AI (-1)
        self.model = keras.Sequential([
            keras.layers.Dense(27, activation='relu', input_shape=(9,)),
            keras.layers.Dense(18, activation='relu'),
            keras.layers.Dense(9, activation='linear')  # Output for each cell
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['accuracy']
        )
        print("Created new neural network model")
    
    def board_to_input(self, board):
        """Convert board to neural network input format"""
        input_data = []
        for row in board:
            for cell in row:
                if cell is None:
                    input_data.append(0)  # Empty
                elif cell == 'O':  # Player
                    input_data.append(1)
                elif cell == 'X':  # AI
                    input_data.append(-1)
        return np.array([input_data])
    
    def choose_action(self, board):
        """Choose an action based on neural network prediction"""
        valid_actions = []
        for i in range(3):
            for j in range(3):
                if board[i][j] is None:
                    valid_actions.append((i, j))
        
        if not valid_actions:
            return None  # No valid actions
        
        # Get neural network prediction
        board_input = self.board_to_input(board)
        predictions = self.model.predict(board_input, verbose=0)[0]
        
        # Filter predictions to only valid moves
        valid_indices = [(i * 3 + j) for i, j in valid_actions]
        valid_predictions = [(idx, predictions[idx]) for idx in valid_indices]
        
        # Choose best valid move
        best_idx, _ = max(valid_predictions, key=lambda x: x[1])
        return (best_idx // 3, best_idx % 3)
    
    def record_move(self, board, action, player_mark):
        """Record a move for training"""
        self.game_history.append({
            'board': self.board_to_input(board)[0].tolist(),
            'action': action[0] * 3 + action[1],
            'player': 1 if player_mark == 'O' else -1
        })
    
    def train_on_game(self, outcome):
        """Train the model based on game outcome
        outcome: 1 if AI won, -1 if player won, 0 for draw
        """
        if not self.game_history:
            return
        
        X = []  # Input boards
        y = []  # Target outputs
        
        # Record game result
        self.training_stats['games_played'] += 1
        if outcome == 1:
            self.training_stats['wins'] += 1
            reward = 1.0
        elif outcome == -1:
            self.training_stats['losses'] += 1
            reward = -1.0
        else:
            self.training_stats['draws'] += 1
            reward = 0.2
        
        # Process each move in reverse to calculate rewards
        for move in reversed(self.game_history):
            board = np.array(move['board'])
            action = move['action']
            
            X.append(board)
            
            # Create target output - initially all zeros
            target = np.zeros(9)
            
            # Set the reward for the chosen action
            target[action] = reward
            
            # For opponent moves, we reverse the logic
            if move['player'] == 1:  # Player move
                target[action] = -reward  # Opposite reward for player moves
            
            y.append(target)
            
            # Diminish reward for earlier moves
            reward *= 0.9
        
        # Train the model
        history = self.model.fit(
            np.array(X), 
            np.array(y), 
            epochs=5, 
            batch_size=min(len(X), 32),
            verbose=0
        )
        
        # Record training stats
        self.training_stats['training_history'].append({
            'loss': float(history.history['loss'][-1]),
            'accuracy': float(history.history['accuracy'][-1])
        })
        
        # Save model and stats
        self.save_model()
        self.save_training_stats()
        
        # Clear history for next game
        self.game_history = []
    
    def save_model(self):
        """Save the model to file"""
        self.model.save(self.model_file)
    
    def save_training_stats(self):
        """Save training statistics to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.training_stats, f)
    
    def load_training_stats(self):
        """Load training statistics from file"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.training_stats = json.load(f)
    
    def reset_for_new_game(self):
        """Reset history for a new game"""
        self.game_history = []
    
    def get_stats(self):
        """Return model statistics"""
        return {
            'games_played': self.training_stats['games_played'],
            'wins': self.training_stats['wins'],
            'losses': self.training_stats['losses'],
            'draws': self.training_stats['draws'],
            'recent_accuracy': self.training_stats['training_history'][-1]['accuracy'] if self.training_stats['training_history'] else 0,
            'recent_loss': self.training_stats['training_history'][-1]['loss'] if self.training_stats['training_history'] else 0
        }


def test_neural_network():
    """Function to test neural network agent"""
    agent = NeuralNetworkAgent(load_existing=False)
    # Create a simple board state
    board = [[None, None, None], [None, 'X', None], [None, None, None]]
    action = agent.choose_action(board)
    print(f"For center X board, chosen action: {action}")
    agent.record_move(board, action, 'X')
    agent.train_on_game(1)  # Pretend we won


if __name__ == "__main__":
    test_neural_network()
