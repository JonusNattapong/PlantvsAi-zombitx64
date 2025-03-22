import json
import os
import numpy as np
from collections import defaultdict, Counter

class PatternRecognitionAgent:
    def __init__(self, load_existing=True):
        """
        Initialize pattern recognition agent
        load_existing: whether to load existing pattern data if available
        """
        self.patterns_file = 'player_patterns.json'
        self.current_game = []
        
        # Pattern database structure:
        # player_id -> pattern -> next_move -> count
        self.patterns = defaultdict(lambda: defaultdict(Counter))
        self.player_stats = defaultdict(lambda: {
            'games_played': 0,
            'starting_positions': Counter(),
            'favorite_moves': Counter(),
            'response_patterns': defaultdict(Counter),
            'win_rate': 0,
            'draw_rate': 0,
            'lose_rate': 0
        })
        
        if load_existing and os.path.exists(self.patterns_file):
            self.load_patterns()
    
    def load_patterns(self):
        """Load pattern data from file"""
        try:
            with open(self.patterns_file, 'r') as f:
                data = json.load(f)
                # Convert from JSON to our data structure
                for player_id, patterns in data['patterns'].items():
                    for pattern, next_moves in patterns.items():
                        for move, count in next_moves.items():
                            self.patterns[player_id][pattern][move] = count
                
                self.player_stats = defaultdict(lambda: {
                    'games_played': 0,
                    'starting_positions': Counter(),
                    'favorite_moves': Counter(),
                    'response_patterns': defaultdict(Counter),
                    'win_rate': 0,
                    'draw_rate': 0,
                    'lose_rate': 0
                })
                
                for player_id, stats in data['player_stats'].items():
                    self.player_stats[player_id] = stats
                    # Convert back to Counter objects
                    self.player_stats[player_id]['starting_positions'] = Counter(stats['starting_positions'])
                    self.player_stats[player_id]['favorite_moves'] = Counter(stats['favorite_moves'])
                    self.player_stats[player_id]['response_patterns'] = defaultdict(Counter)
                    for pattern, responses in stats['response_patterns'].items():
                        self.player_stats[player_id]['response_patterns'][pattern] = Counter(responses)
                
                print(f"Loaded patterns for {len(self.patterns)} players")
        except Exception as e:
            print(f"Error loading patterns: {e}, starting fresh")
    
    def save_patterns(self):
        """Save pattern data to file"""
        # Convert data structure to JSON-serializable format
        data = {
            'patterns': {},
            'player_stats': {}
        }
        
        for player_id, patterns in self.patterns.items():
            data['patterns'][player_id] = {}
            for pattern, next_moves in patterns.items():
                data['patterns'][player_id][pattern] = dict(next_moves)
        
        for player_id, stats in self.player_stats.items():
            data['player_stats'][player_id] = {
                'games_played': stats['games_played'],
                'starting_positions': dict(stats['starting_positions']),
                'favorite_moves': dict(stats['favorite_moves']),
                'response_patterns': {k: dict(v) for k, v in stats['response_patterns'].items()},
                'win_rate': stats['win_rate'],
                'draw_rate': stats['draw_rate'],
                'lose_rate': stats['lose_rate']
            }
        
        with open(self.patterns_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def board_to_pattern(self, board):
        """Convert board to pattern string"""
        pattern = ''
        for row in board:
            for cell in row:
                if cell is None:
                    pattern += '_'
                else:
                    pattern += cell
        return pattern
    
    def move_to_str(self, move):
        """Convert move (row, col) to string representation"""
        return f"{move[0]},{move[1]}"
    
    def str_to_move(self, move_str):
        """Convert string representation to move (row, col)"""
        row, col = move_str.split(',')
        return (int(row), int(col))
    
    def record_move(self, board, move, player_id, player_mark):
        """Record a move for pattern recognition"""
        pattern = self.board_to_pattern(board)
        move_str = self.move_to_str(move)
        
        # Record current game
        self.current_game.append({
            'pattern': pattern,
            'move': move_str,
            'player': player_id,
            'mark': player_mark
        })
        
        # Update favorite moves counter
        self.player_stats[player_id]['favorite_moves'][move_str] += 1
        
        # If this is the first move of the game, record starting position
        if len(self.current_game) <= 2:  # First move by each player
            if player_mark == 'O':  # Assuming O goes first
                self.player_stats[player_id]['starting_positions'][move_str] += 1
    
    def analyze_game(self, player_id, outcome):
        """Analyze completed game and update pattern database
        outcome: 'win', 'loss', or 'draw' from player's perspective
        """
        if not self.current_game:
            return
        
        # Update game stats
        self.player_stats[player_id]['games_played'] += 1
        
        # Update win/loss/draw stats
        total_games = self.player_stats[player_id]['games_played']
        if outcome == 'win':
            self.player_stats[player_id]['win_rate'] = (
                self.player_stats[player_id]['win_rate'] * (total_games - 1) + 1) / total_games
        elif outcome == 'loss':
            self.player_stats[player_id]['lose_rate'] = (
                self.player_stats[player_id]['lose_rate'] * (total_games - 1) + 1) / total_games
        else:  # draw
            self.player_stats[player_id]['draw_rate'] = (
                self.player_stats[player_id]['draw_rate'] * (total_games - 1) + 1) / total_games
        
        # Analyze move patterns
        for i in range(len(self.current_game) - 1):
            current_move = self.current_game[i]
            next_move = self.current_game[i + 1]
            
            # Only consider player's patterns for prediction
            if current_move['player'] == player_id:
                pattern = current_move['pattern']
                next_pattern = next_move['pattern']
                next_move_str = next_move['move']
                
                # Record that after seeing pattern, opponent responds with next_move
                self.patterns[player_id][pattern][next_move_str] += 1
                
                # Also record response patterns (what player does after opponent makes a move)
                self.player_stats[player_id]['response_patterns'][next_pattern][next_move_str] += 1
        
        # Save updated patterns
        self.save_patterns()
        
        # Reset for next game
        self.current_game = []
    
    def predict_move(self, board, player_id):
        """Predict the player's next move based on past patterns"""
        pattern = self.board_to_pattern(board)
        
        # Check if we've seen this pattern before
        if pattern in self.patterns[player_id]:
            # Get the most common next move for this pattern
            most_common = self.patterns[player_id][pattern].most_common(1)
            if most_common:
                move_str, _ = most_common[0]
                return self.str_to_move(move_str)
        
        # If no pattern match, fall back to player's favorite moves
        valid_moves = []
        for i in range(3):
            for j in range(3):
                if board[i][j] is None:
                    valid_moves.append((i, j))
        
        if not valid_moves:
            return None
        
        # Check if player has favorite valid moves
        favorite_moves = self.player_stats[player_id]['favorite_moves']
        if favorite_moves:
            valid_move_strs = [self.move_to_str(move) for move in valid_moves]
            # Filter to only valid moves and sort by frequency
            valid_favorites = [(move, count) for move, count in favorite_moves.items() 
                              if move in valid_move_strs]
            if valid_favorites:
                # Return the most common valid favorite move
                return self.str_to_move(max(valid_favorites, key=lambda x: x[1])[0])
        
        # If no patterns or favorites, return a random valid move
        return valid_moves[np.random.randint(0, len(valid_moves))]
    
    def choose_counter_move(self, board, player_id):
        """Choose a counter move based on predicted player pattern"""
        predicted_player_move = self.predict_move(board, player_id)
        
        if predicted_player_move is None:
            return None
        
        # Make a temporary board with the predicted player move
        temp_board = [row[:] for row in board]
        row, col = predicted_player_move
        temp_board[row][col] = 'O'  # Assuming player is O
        
        # Choose a blocking or winning move
        valid_moves = []
        for i in range(3):
            for j in range(3):
                if temp_board[i][j] is None:
                    valid_moves.append((i, j))
        
        if not valid_moves:
            return None
        
        # Check for winning move
        for move in valid_moves:
            row, col = move
            temp_board[row][col] = 'X'  # Try AI move
            if self.check_win(temp_board, 'X'):
                return move
            temp_board[row][col] = None  # Undo move
        
        # Check for blocking move - if player would win with their predicted move
        row, col = predicted_player_move
        temp_board = [row[:] for row in board]
        temp_board[row][col] = 'O'
        for i in range(3):
            for j in range(3):
                if temp_board[i][j] is None:
                    temp_board[i][j] = 'O'
                    if self.check_win(temp_board, 'O'):
                        return (i, j)  # Block this winning move
                    temp_board[i][j] = None
        
        # If no winning or blocking move, choose center if available
        if temp_board[1][1] is None:
            return (1, 1)
        
        # Otherwise, choose a random valid move
        return valid_moves[np.random.randint(0, len(valid_moves))]
    
    def check_win(self, board, player):
        """Check if player has won on the board"""
        # Check rows
        for row in range(3):
            if board[row][0] == board[row][1] == board[row][2] == player:
                return True
        
        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] == player:
                return True
        
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] == player:
            return True
        if board[0][2] == board[1][1] == board[2][0] == player:
            return True
        
        return False
    
    def reset_for_new_game(self):
        """Reset for a new game"""
        self.current_game = []
    
    def get_player_stats(self, player_id):
        """Get statistics for a specific player"""
        stats = self.player_stats[player_id]
        
        # Get player's most common starting positions
        starting_positions = stats['starting_positions'].most_common(3)
        
        # Get player's favorite moves
        favorite_moves = stats['favorite_moves'].most_common(5)
        
        # Get player's most common patterns
        patterns = {}
        for pattern, next_moves in self.patterns[player_id].items():
            patterns[pattern] = next_moves.most_common(3)
        
        return {
            'games_played': stats['games_played'],
            'win_rate': stats['win_rate'],
            'draw_rate': stats['draw_rate'],
            'lose_rate': stats['lose_rate'],
            'starting_positions': starting_positions,
            'favorite_moves': favorite_moves,
            'common_patterns': patterns
        }


def test_pattern_recognition():
    """Function to test pattern recognition agent"""
    agent = PatternRecognitionAgent(load_existing=False)
    
    # Simulate a game
    player_id = "player1"
    
    # First move by player
    board = [[None, None, None], [None, None, None], [None, None, None]]
    move = (0, 0)
    agent.record_move(board, move, player_id, 'O')
    
    # AI response
    board[0][0] = 'O'
    ai_move = (1, 1)
    board[1][1] = 'X'
    
    # Second player move
    move = (0, 1)
    agent.record_move(board, move, player_id, 'O')
    
    # AI response
    board[0][1] = 'O'
    ai_move = (2, 2)
    board[2][2] = 'X'
    
    # Third player move
    move = (0, 2)
    agent.record_move(board, move, player_id, 'O')
    
    # Analyze the game - player won
    agent.analyze_game(player_id, 'win')
    
    # Now predict for a similar board
    new_board = [[None, None, None], [None, 'X', None], [None, None, None]]
    predicted_move = agent.predict_move(new_board, player_id)
    print(f"Predicted move for player: {predicted_move}")
    
    counter_move = agent.choose_counter_move(new_board, player_id)
    print(f"Counter move for AI: {counter_move}")
    
    print(f"Player stats: {agent.get_player_stats(player_id)}")


if __name__ == "__main__":
    test_pattern_recognition()
