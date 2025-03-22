import numpy as np
import pickle
import os
from itertools import permutations

class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1):
        """
        Initialize Q-learning agent with parameters:
        alpha: learning rate
        gamma: discount factor
        epsilon: exploration rate
        """
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}  # State-action value table
        self.history = []  # To track game states for learning
        self.load_q_table()
    
    def load_q_table(self):
        """Load Q-table from file if it exists"""
        if os.path.exists('q_table.pkl'):
            try:
                with open('q_table.pkl', 'rb') as f:
                    self.q_table = pickle.load(f)
                print("Loaded Q-table with", len(self.q_table), "state-action pairs")
            except:
                print("Error loading Q-table, starting fresh")
    
    def save_q_table(self):
        """Save Q-table to file"""
        with open('q_table.pkl', 'wb') as f:
            pickle.dump(self.q_table, f)
        print("Saved Q-table with", len(self.q_table), "state-action pairs")
    
    def board_to_state(self, board):
        """Convert board state to a hashable representation"""
        state = []
        for row in board:
            for cell in row:
                if cell is None:
                    state.append(' ')
                else:
                    state.append(cell)
        return tuple(state)
    
    def get_valid_actions(self, board):
        """Get all valid actions (empty cells) for the current board state"""
        actions = []
        for i in range(3):
            for j in range(3):
                if board[i][j] is None:
                    actions.append((i, j))
        return actions
    
    def get_q_value(self, state, action):
        """Get Q-value for a state-action pair, or 0 if not found"""
        if (state, action) not in self.q_table:
            self.q_table[(state, action)] = 0.0
        return self.q_table[(state, action)]
    
    def choose_action(self, board):
        """Choose an action using epsilon-greedy strategy"""
        state = self.board_to_state(board)
        valid_actions = self.get_valid_actions(board)
        
        if not valid_actions:
            return None  # No valid actions available
        
        # With probability epsilon, choose random action (exploration)
        if np.random.random() < self.epsilon:
            return valid_actions[np.random.randint(0, len(valid_actions))]
        
        # Otherwise, choose the best action (exploitation)
        q_values = [self.get_q_value(state, action) for action in valid_actions]
        max_q = max(q_values)
        # If multiple actions have the max Q-value, choose randomly among them
        best_actions = [action for action, q in zip(valid_actions, q_values) if q == max_q]
        return best_actions[np.random.randint(0, len(best_actions))]
    
    def record_move(self, board, action):
        """Record the state and action for learning"""
        state = self.board_to_state(board)
        self.history.append((state, action))
    
    def learn_from_game(self, reward):
        """Update Q-values based on game outcome and recorded history"""
        if not self.history:
            return
        
        # Start with the final reward (1 for win, -1 for loss, 0 for draw)
        for i in range(len(self.history) - 1, -1, -1):
            state, action = self.history[i]
            if (state, action) not in self.q_table:
                self.q_table[(state, action)] = 0.0
            
            # Q-learning update: Q(s,a) = Q(s,a) + alpha * [reward + gamma * max_a' Q(s',a') - Q(s,a)]
            self.q_table[(state, action)] += self.alpha * (reward - self.q_table[(state, action)])
            # For next iteration, reward becomes discounted future reward
            reward = self.gamma * reward
        
        # Clear history for next game
        self.history = []
    
    def reset_for_new_game(self):
        """Reset history for a new game"""
        self.history = []
    
    def get_stats(self):
        """Return statistics about the Q-table"""
        return {
            'q_table_size': len(self.q_table),
            'avg_q_value': np.mean(list(self.q_table.values())) if self.q_table else 0,
            'max_q_value': np.max(list(self.q_table.values())) if self.q_table else 0,
            'min_q_value': np.min(list(self.q_table.values())) if self.q_table else 0
        }


def test_q_learning():
    """Function to test Q-learning agent"""
    agent = QLearningAgent()
    # Create a simple board state
    board = [[None, None, None], [None, 'X', None], [None, None, None]]
    action = agent.choose_action(board)
    print(f"For center X board, chosen action: {action}")
    agent.record_move(board, action)
    agent.learn_from_game(1.0)  # Pretend we won
    agent.save_q_table()


if __name__ == "__main__":
    test_q_learning()
