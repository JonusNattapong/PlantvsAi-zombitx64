import numpy as np
import json
import os
import random
from copy import deepcopy

class ConnectFour:
    """
    คลาสหลักสำหรับเกม Connect Four
    """
    def __init__(self):
        """Initialize Connect Four game"""
        self.ROWS = 6
        self.COLS = 7
        self.board = None
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.player_turn = True  # True for player (O), False for AI (X)
        self.reset_game()
        self.stats = self.load_stats()
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.board = [[None for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.player_turn = True
    
    def load_stats(self):
        """Load game statistics from file"""
        stats_file = 'connect_four_stats.json'
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading Connect Four stats: {e}")
        
        # Default stats
        return {
            "total_games": 0,
            "player_wins": 0,
            "ai_wins": 0,
            "draws": 0,
            "win_rate": 0,
            "ai_mode_stats": {}
        }
    
    def save_stats(self):
        """Save game statistics to file"""
        stats_file = 'connect_four_stats.json'
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Error saving Connect Four stats: {e}")
    
    def update_stats(self, ai_mode_name):
        """Update game statistics after a game ends"""
        self.stats["total_games"] += 1
        
        # Initialize AI mode stats if not exists
        if ai_mode_name not in self.stats["ai_mode_stats"]:
            self.stats["ai_mode_stats"][ai_mode_name] = {"wins": 0, "losses": 0, "draws": 0}
        
        # Update based on winner
        if self.winner == 'X':  # AI wins
            self.stats["ai_wins"] += 1
            self.stats["ai_mode_stats"][ai_mode_name]["wins"] += 1
        elif self.winner == 'O':  # Player wins
            self.stats["player_wins"] += 1
            self.stats["ai_mode_stats"][ai_mode_name]["losses"] += 1
        else:  # Draw
            self.stats["draws"] += 1
            self.stats["ai_mode_stats"][ai_mode_name]["draws"] += 1
        
        # Update win rate
        total_games = self.stats["total_games"]
        if total_games > 0:
            self.stats["win_rate"] = round((self.stats["player_wins"] / total_games) * 100)
        
        # Save updated stats
        self.save_stats()
    
    def make_move(self, col, player):
        """Make a move on the board
        
        Args:
            col: Column to drop the disc
            player: 'O' for player, 'X' for AI
            
        Returns:
            bool: True if move was successful, False otherwise
        """
        if col < 0 or col >= self.COLS or self.game_over:
            return False
        
        # Check if column is full
        if self.board[0][col] is not None:
            return False
        
        # Find the lowest empty cell in the column
        for row in range(self.ROWS - 1, -1, -1):
            if self.board[row][col] is None:
                self.board[row][col] = player
                self.last_move = (row, col)
                break
        
        # Check for win or draw
        self.check_game_over()
        
        # Switch turns if game not over
        if not self.game_over:
            self.player_turn = not self.player_turn
        
        return True
    
    def check_game_over(self):
        """Check if the game is over (win or draw)"""
        # Check for win
        if self.last_move is not None:
            row, col = self.last_move
            player = self.board[row][col]
            
            # Check horizontal
            if self.check_horizontal(row, player):
                self.game_over = True
                self.winner = player
                return
            
            # Check vertical
            if self.check_vertical(col, player):
                self.game_over = True
                self.winner = player
                return
            
            # Check diagonal (down-right)
            if self.check_diagonal_down_right(row, col, player):
                self.game_over = True
                self.winner = player
                return
            
            # Check diagonal (up-right)
            if self.check_diagonal_up_right(row, col, player):
                self.game_over = True
                self.winner = player
                return
        
        # Check for draw (board is full)
        is_full = all(self.board[0][col] is not None for col in range(self.COLS))
        if is_full:
            self.game_over = True
            self.winner = None  # Draw
    
    def check_horizontal(self, row, player):
        """Check for horizontal win"""
        for c in range(self.COLS - 3):
            if (self.board[row][c] == player and
                self.board[row][c+1] == player and
                self.board[row][c+2] == player and
                self.board[row][c+3] == player):
                return True
        return False
    
    def check_vertical(self, col, player):
        """Check for vertical win"""
        for r in range(self.ROWS - 3):
            if (self.board[r][col] == player and
                self.board[r+1][col] == player and
                self.board[r+2][col] == player and
                self.board[r+3][col] == player):
                return True
        return False
    
    def check_diagonal_down_right(self, row, col, player):
        """Check for diagonal win (down-right)"""
        # Find the top-left cell of this diagonal
        while row > 0 and col > 0 and row < self.ROWS and col < self.COLS:
            row -= 1
            col -= 1
        
        # Check diagonal from top-left to bottom-right
        consecutive = 0
        r, c = row, col
        while r < self.ROWS and c < self.COLS:
            if self.board[r][c] == player:
                consecutive += 1
                if consecutive == 4:
                    return True
            else:
                consecutive = 0
            r += 1
            c += 1
        
        return False
    
    def check_diagonal_up_right(self, row, col, player):
        """Check for diagonal win (up-right)"""
        # Find the bottom-left cell of this diagonal
        while row < self.ROWS - 1 and col > 0:
            row += 1
            col -= 1
        
        # Check diagonal from bottom-left to top-right
        consecutive = 0
        r, c = row, col
        while r >= 0 and c < self.COLS:
            if self.board[r][c] == player:
                consecutive += 1
                if consecutive == 4:
                    return True
            else:
                consecutive = 0
            r -= 1
            c += 1
        
        return False
    
    def get_valid_columns(self):
        """Return a list of valid columns to make a move"""
        valid_cols = []
        for col in range(self.COLS):
            if self.board[0][col] is None:  # Top cell is empty
                valid_cols.append(col)
        return valid_cols
    
    def evaluate_window(self, window, player):
        """Evaluate a window of 4 cells for heuristic scoring"""
        opponent = 'O' if player == 'X' else 'X'
        
        if window.count(player) == 4:
            return 100  # Win
        elif window.count(player) == 3 and window.count(None) == 1:
            return 5  # Three in a row + empty
        elif window.count(player) == 2 and window.count(None) == 2:
            return 2  # Two in a row + empty
        elif window.count(opponent) == 3 and window.count(None) == 1:
            return -20  # Block opponent's three
        
        return 0
    
    def evaluate_board(self, player):
        """Heuristic evaluation of the board for minimax algorithm"""
        if self.winner == player:
            return 1000
        elif self.winner is not None:
            return -1000
        elif self.winner is None and self.game_over:  # Draw
            return 0
        
        score = 0
        
        # Score center column (preferred position)
        center_col = self.COLS // 2
        center_count = sum(1 for row in range(self.ROWS) if self.board[row][center_col] == player)
        score += center_count * 3
        
        # Score horizontal
        for row in range(self.ROWS):
            for col in range(self.COLS - 3):
                window = [self.board[row][col+i] for i in range(4)]
                score += self.evaluate_window(window, player)
        
        # Score vertical
        for col in range(self.COLS):
            for row in range(self.ROWS - 3):
                window = [self.board[row+i][col] for i in range(4)]
                score += self.evaluate_window(window, player)
        
        # Score diagonal (down-right)
        for row in range(self.ROWS - 3):
            for col in range(self.COLS - 3):
                window = [self.board[row+i][col+i] for i in range(4)]
                score += self.evaluate_window(window, player)
        
        # Score diagonal (up-right)
        for row in range(3, self.ROWS):
            for col in range(self.COLS - 3):
                window = [self.board[row-i][col+i] for i in range(4)]
                score += self.evaluate_window(window, player)
        
        return score
    
    def is_terminal_node(self):
        """Check if the current state is a terminal node (game over)"""
        return self.game_over or len(self.get_valid_columns()) == 0
    
    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """Minimax algorithm with alpha-beta pruning"""
        # Create a temporary game state
        temp_game = ConnectFour()
        temp_game.board = deepcopy(board)
        temp_game.check_game_over()  # Update game_over and winner
        
        # Check if terminal node or max depth
        if depth == 0 or temp_game.is_terminal_node():
            if temp_game.winner == 'X':  # AI wins
                return (None, 1000000)
            elif temp_game.winner == 'O':  # Player wins
                return (None, -1000000)
            elif temp_game.is_terminal_node():  # Draw
                return (None, 0)
            else:  # Max depth reached, evaluate the board
                return (None, temp_game.evaluate_board('X'))
        
        valid_columns = temp_game.get_valid_columns()
        
        if maximizing_player:  # AI's turn (X)
            value = -float('inf')
            column = random.choice(valid_columns) if valid_columns else None
            
            for col in valid_columns:
                # Make a move in a temporary game
                temp_board = deepcopy(board)
                temp_game = ConnectFour()
                temp_game.board = temp_board
                temp_game.make_move(col, 'X')
                
                # Recursive call
                new_score = temp_game.minimax(temp_game.board, depth - 1, alpha, beta, False)[1]
                
                # Update best move
                if new_score > value:
                    value = new_score
                    column = col
                
                # Alpha-beta pruning
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            
            return (column, value)
        
        else:  # Player's turn (O)
            value = float('inf')
            column = random.choice(valid_columns) if valid_columns else None
            
            for col in valid_columns:
                # Make a move in a temporary game
                temp_board = deepcopy(board)
                temp_game = ConnectFour()
                temp_game.board = temp_board
                temp_game.make_move(col, 'O')
                
                # Recursive call
                new_score = temp_game.minimax(temp_game.board, depth - 1, alpha, beta, True)[1]
                
                # Update best move
                if new_score < value:
                    value = new_score
                    column = col
                
                # Alpha-beta pruning
                beta = min(beta, value)
                if alpha >= beta:
                    break
            
            return (column, value)


# Test function for ConnectFour class
if __name__ == "__main__":
    game = ConnectFour()
    
    # Display initial board
    print("Initial board:")
    for row in game.board:
        print([cell if cell else ' ' for cell in row])
    
    # Make some moves
    print("\nMaking moves...")
    game.make_move(3, 'O')  # Player drops in middle
    game.make_move(2, 'X')  # AI drops next to it
    game.make_move(3, 'O')  # Player stacks on middle
    
    # Display board after moves
    print("\nBoard after moves:")
    for row in game.board:
        print([cell if cell else ' ' for cell in row])
    
    # Test minimax
    print("\nCalculating best AI move...")
    best_col, score = game.minimax(game.board, depth=3, alpha=float('-inf'), beta=float('inf'), maximizing_player=True)
    print(f"Best move: column {best_col} with score {score}")
    
    # Make the best move
    game.make_move(best_col, 'X')
    
    # Display final board
    print("\nBoard after AI move:")
    for row in game.board:
        print([cell if cell else ' ' for cell in row])
