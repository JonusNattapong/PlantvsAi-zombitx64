import numpy as np
import json
import os
import random
from copy import deepcopy
from game_settings import GameSettings
import time

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
        self.game_settings = GameSettings()
        self.settings = self.game_settings.get_settings()
        self.reset_game()
        self.stats = self.load_stats()
    
    def set_difficulty(self, difficulty):
        """ตั้งค่าระดับความยาก"""
        self.game_settings.set_difficulty(difficulty)
        self.settings = self.game_settings.get_settings()
    
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
    
    def get_ai_move(self):
        """รับการเคลื่อนที่ของ AI"""
        settings = self.game_settings.adjust_settings('connect_four')
        
        # คำนวณเวลาคิดตามความซับซ้อนของกระดาน
        move_count = sum(1 for row in self.board for cell in row if cell is not None)
        complexity = self.calculate_board_complexity(self.board)
        thinking_time = self.game_settings.calculate_thinking_time('connect_four', move_count, complexity)
        
        # ปรับความลึกของการค้นหาตามเวลาคิด
        search_depth = min(settings['search_depth'], int(thinking_time * 1.3))
        
        # ใช้ MCTS สำหรับการค้นหาการเคลื่อนที่ที่ดีที่สุด
        from algorithm.mcts import MCTS
        mcts = MCTS()
        
        # ปรับพารามิเตอร์ตามระดับความยาก
        mcts.set_parameters(
            search_depth=search_depth,
            time_limit=thinking_time,
            pattern_weight=settings['pattern_weight'],
            randomness=settings['randomness'],
            connect_bonus=settings['connect_bonus']
        )
        
        # ทำให้ AI ช้าลงในโหมดง่ายเพื่อให้ผู้เล่นมีเวลาคิด
        if settings['ai_delay'] > 0:
            time.sleep(settings['ai_delay'])
        
        # ค้นหาการเคลื่อนที่ที่ดีที่สุด
        best_move = mcts.search(self.board, self.player_turn)
        return best_move
    
    def calculate_board_complexity(self, board):
        """คำนวณความซับซ้อนของกระดาน"""
        # นับจำนวนช่องว่าง
        empty_cells = sum(1 for row in board for cell in row if cell is None)
        
        # นับจำนวนการจัดเรียงที่เป็นไปได้
        possible_lines = 0
        
        # ตรวจสอบแนวนอน
        for row in range(self.ROWS):
            for col in range(self.COLS - 3):
                window = [board[row][col + i] for i in range(4)]
                if None in window:
                    possible_lines += 1
        
        # ตรวจสอบแนวตั้ง
        for col in range(self.COLS):
            for row in range(self.ROWS - 3):
                window = [board[row + i][col] for i in range(4)]
                if None in window:
                    possible_lines += 1
        
        # ตรวจสอบแนวทแยง
        for row in range(self.ROWS - 3):
            for col in range(self.COLS - 3):
                window = [board[row + i][col + i] for i in range(4)]
                if None in window:
                    possible_lines += 1
                window = [board[row + i][col - i] for i in range(4)]
                if None in window:
                    possible_lines += 1
        
        # คำนวณความซับซ้อนโดยรวม
        complexity = (empty_cells + possible_lines) / 50.0
        return complexity
    
    def evaluate_board(self, board):
        """ประเมินค่ากระดาน"""
        settings = self.game_settings.adjust_settings('connect_four')
        
        score = 0
        
        # ตรวจสอบแนวตั้ง
        for col in range(self.COLS):
            for row in range(self.ROWS - 3):
                window = [board[row + i][col] for i in range(4)]
                score += self.evaluate_window(window, settings['connect_bonus'])
        
        # ตรวจสอบแนวนอน
        for row in range(self.ROWS):
            for col in range(self.COLS - 3):
                window = [board[row][col + i] for i in range(4)]
                score += self.evaluate_window(window, settings['connect_bonus'])
        
        # ตรวจสอบแนวทแยง (จากซ้ายล่างไปขวาบน)
        for row in range(self.ROWS - 3):
            for col in range(self.COLS - 3):
                window = [board[row + i][col + i] for i in range(4)]
                score += self.evaluate_window(window, settings['connect_bonus'])
        
        # ตรวจสอบแนวทแยง (จากขวาล่างไปซ้ายบน)
        for row in range(self.ROWS - 3):
            for col in range(3, self.COLS):
                window = [board[row + i][col - i] for i in range(4)]
                score += self.evaluate_window(window, settings['connect_bonus'])
        
        # ปรับคะแนนตามความซับซ้อนของกระดาน
        complexity = self.calculate_board_complexity(board)
        score *= (1 + complexity * 0.1)
        
        return score
    
    def evaluate_window(self, window, connect_bonus):
        """ประเมินค่าของช่อง 4 ช่องที่ติดกัน"""
        score = 0
        ai_pieces = window.count('X')
        player_pieces = window.count('O')
        empty_spaces = window.count(None)
        
        if ai_pieces == 4:
            score += 100 + connect_bonus
        elif ai_pieces == 3 and empty_spaces == 1:
            score += 5 + connect_bonus
        elif ai_pieces == 2 and empty_spaces == 2:
            score += 2
        
        if player_pieces == 3 and empty_spaces == 1:
            score -= 4
        elif player_pieces == 2 and empty_spaces == 2:
            score -= 1
        
        return score
    
    def get_valid_moves(self):
        """รับการเคลื่อนที่ที่ถูกต้อง"""
        settings = self.game_settings.adjust_settings('connect_four')
        
        valid_moves = []
        for col in range(self.COLS):
            if self.board[0][col] is None:
                valid_moves.append(col)
        
        # เพิ่มความสุ่มตามระดับความยาก
        if settings['randomness'] > random.random():
            random.shuffle(valid_moves)
        
        return valid_moves
    
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
