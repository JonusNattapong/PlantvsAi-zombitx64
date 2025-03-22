import json
import os
import random
import time
from copy import deepcopy
from game_settings import GameSettings

class Checkers:
    """
    คลาสหลักสำหรับเกม Checkers (หมากฮอต)
    """
    def __init__(self):
        """Initialize Checkers game"""
        self.ROWS = 8
        self.COLS = 8
        self.board = None
        self.game_over = False
        self.winner = None
        self.player_turn = True  # True for player (O), False for AI (X)
        self.must_jump = False
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
        # สร้างกระดานเปล่า
        self.board = [[None for _ in range(self.COLS)] for _ in range(self.ROWS)]
        
        # วางหมากเริ่มต้น
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if row % 2 == col % 2:  # ช่องสีเดียวกัน
                    if row < 3:  # บน 3 แถวแรก - AI
                        self.board[row][col] = {'piece': 'X', 'king': False}
                    elif row > 4:  # ล่าง 3 แถวสุดท้าย - Player
                        self.board[row][col] = {'piece': 'O', 'king': False}
        
        self.game_over = False
        self.winner = None
        self.player_turn = True
        self.must_jump = False
    
    def load_stats(self):
        """Load game statistics from file"""
        stats_file = 'checkers_stats.json'
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading Checkers stats: {e}")
        
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
        stats_file = 'checkers_stats.json'
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Error saving Checkers stats: {e}")
    
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
    
    def get_board_state(self):
        """Return the current board state (for API)"""
        return self.board
    
    def get_valid_moves(self, row, col):
        """Get all valid moves for a piece at the given position
        
        Returns:
            dict: Dictionary where key is destination (row,col) and value is list of captured pieces
        """
        if (row < 0 or row >= self.ROWS or col < 0 or col >= self.COLS or 
            self.board[row][col] is None):
            return {}
        
        piece = self.board[row][col]
        
        # Check if it's the player's turn and the selected piece belongs to the player
        if (self.player_turn and piece['piece'] != 'O') or (not self.player_turn and piece['piece'] != 'X'):
            return {}
        
        # If there's a mandatory jump, only return jump moves
        jumps = self._get_jump_moves(row, col)
        if self.must_jump or jumps:
            return jumps
        
        # Otherwise, also include regular moves
        return {**self._get_regular_moves(row, col), **jumps}
    
    def _get_regular_moves(self, row, col):
        """Get non-capture moves for a piece
        
        Returns:
            dict: Dictionary where key is destination (row,col) and value is an empty list
        """
        valid_moves = {}
        piece = self.board[row][col]
        
        # Movement directions
        directions = []
        if piece['piece'] == 'O' or piece['king']:  # Player or any king (move up)
            directions.extend([(-1, -1), (-1, 1)])
        if piece['piece'] == 'X' or piece['king']:  # AI or any king (move down)
            directions.extend([(1, -1), (1, 1)])
        
        # Check valid moves in each direction
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < self.ROWS and 0 <= c < self.COLS and self.board[r][c] is None:
                valid_moves[(r, c)] = []  # No pieces captured for regular moves
        
        return valid_moves
    
    def _get_jump_moves(self, row, col, captured=None):
        """Get possible jump moves (capturing opponent's pieces)
        
        Args:
            row, col: Current piece position
            captured: Optional list of already captured positions in this sequence
            
        Returns:
            dict: Dictionary where key is destination (row,col) and value is list of captured pieces
        """
        if captured is None:
            captured = []
        
        valid_jumps = {}
        piece = self.board[row][col]
        
        # Jumping directions
        directions = []
        if piece['piece'] == 'O' or piece['king']:  # Player or any king (move up)
            directions.extend([(-1, -1), (-1, 1)])
        if piece['piece'] == 'X' or piece['king']:  # AI or any king (move down)
            directions.extend([(1, -1), (1, 1)])
        
        # Check for jumps in each direction
        opponent = 'X' if piece['piece'] == 'O' else 'O'
        
        for dr, dc in directions:
            # Position to jump over (opponent)
            r1, c1 = row + dr, col + dc
            # Landing position
            r2, c2 = row + 2*dr, col + 2*dc
            
            # Check if jump is valid
            if (0 <= r1 < self.ROWS and 0 <= c1 < self.COLS and 
                0 <= r2 < self.ROWS and 0 <= c2 < self.COLS and
                self.board[r1][c1] is not None and self.board[r1][c1]['piece'] == opponent and
                self.board[r2][c2] is None and (r1, c1) not in captured):
                
                # This is a valid jump
                new_captured = captured + [(r1, c1)]
                valid_jumps[(r2, c2)] = new_captured
                
                # Recursively check for multi-jumps
                # Temporarily move piece to check for further jumps
                original_piece = self.board[r1][c1]
                self.board[r2][c2] = piece
                self.board[row][col] = None
                self.board[r1][c1] = None
                
                # Get more jumps from the new position
                more_jumps = self._get_jump_moves(r2, c2, new_captured)
                
                # Restore original board state
                self.board[row][col] = piece
                self.board[r1][c1] = original_piece
                self.board[r2][c2] = None
                
                # Add multi-jumps to valid moves
                valid_jumps.update(more_jumps)
        
        return valid_jumps
    
    def make_move(self, from_row, from_col, to_row, to_col):
        """Make a move from one position to another
        
        Returns:
            bool: True if move was successful, False otherwise
        """
        # Check if the move is valid
        valid_moves = self.get_valid_moves(from_row, from_col)
        
        if (to_row, to_col) not in valid_moves:
            return False
        
        # Get the piece being moved
        piece = self.board[from_row][from_col]
        
        # Check for promotion to king (reaching the opposite side)
        if (piece['piece'] == 'O' and to_row == 0) or (piece['piece'] == 'X' and to_row == self.ROWS - 1):
            piece['king'] = True
        
        # Execute the move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Handle captures
        captured = valid_moves[(to_row, to_col)]
        for r, c in captured:
            self.board[r][c] = None
        
        # Check for end of game
        if self.check_game_over():
            return True
        
        # Check if another jump is possible from the new position
        possible_jumps = self._get_jump_moves(to_row, to_col)
        
        # Switch turns if no more jumps or different piece
        if not captured or not possible_jumps:
            self.player_turn = not self.player_turn
            
            # Check if the next player has any valid moves
            if not self.has_valid_moves():
                # No valid moves means game over
                self.game_over = True
                self.winner = 'X' if self.player_turn else 'O'  # Winner is the opposite player
        
        return True
    
    def has_valid_moves(self):
        """Check if the current player has any valid moves
        
        Returns:
            bool: True if valid moves exist, False otherwise
        """
        piece_type = 'O' if self.player_turn else 'X'
        
        # First check for any jump moves (they're mandatory)
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if (self.board[row][col] is not None and 
                    self.board[row][col]['piece'] == piece_type and
                    self._get_jump_moves(row, col)):
                    return True
        
        # If no jumps, check for any regular moves
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if (self.board[row][col] is not None and 
                    self.board[row][col]['piece'] == piece_type and
                    self._get_regular_moves(row, col)):
                    return True
        
        return False
    
    def check_game_over(self):
        """Check if the game is over (one player has no pieces or no valid moves)
        
        Returns:
            bool: True if game is over, False otherwise
        """
        # Count pieces
        player_pieces = 0
        ai_pieces = 0
        
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if self.board[row][col] is not None:
                    if self.board[row][col]['piece'] == 'O':
                        player_pieces += 1
                    else:
                        ai_pieces += 1
        
        # Check if one player has no pieces left
        if player_pieces == 0:
            self.game_over = True
            self.winner = 'X'  # AI wins
            return True
        elif ai_pieces == 0:
            self.game_over = True
            self.winner = 'O'  # Player wins
            return True
        
        # Game continues
        return False
    
    def calculate_board_complexity(self, board):
        """คำนวณความซับซ้อนของกระดาน"""
        # นับจำนวนช่องว่าง
        empty_cells = sum(1 for row in board for cell in row if cell is None)
        
        # นับจำนวนชิ้นที่ยังเหลืออยู่
        ai_pieces = sum(1 for row in board for cell in row 
                       if cell and cell['piece'] == 'X')
        player_pieces = sum(1 for row in board for cell in row 
                          if cell and cell['piece'] == 'O')
        
        # นับจำนวนการจับที่เป็นไปได้
        possible_jumps = 0
        for row in range(self.ROWS):
            for col in range(self.COLS):
                piece = board[row][col]
                if piece and piece['piece'] == 'X':
                    # ตรวจสอบการจับในทิศทางต่างๆ
                    directions = [
                        (-2, -2), (-2, 2), (2, -2), (2, 2)
                    ]
                    for dr, dc in directions:
                        new_row, new_col = row + dr, col + dc
                        mid_row, mid_col = row + dr//2, col + dc//2
                        
                        if (0 <= new_row < self.ROWS and 0 <= new_col < self.COLS and
                            self.board[new_row][new_col] is None and
                            self.board[mid_row][mid_col] and
                            self.board[mid_row][mid_col]['piece'] == 'O'):
                            possible_jumps += 1
        
        # คำนวณความซับซ้อนโดยรวม
        complexity = (empty_cells + possible_jumps + 
                     abs(ai_pieces - player_pieces)) / 20.0
        return complexity
    
    def get_ai_move(self):
        """รับการเคลื่อนที่ของ AI"""
        settings = self.game_settings.adjust_settings('checkers')
        
        # คำนวณเวลาคิดตามความซับซ้อนของกระดาน
        move_count = sum(1 for row in self.board for cell in row if cell is not None)
        complexity = self.calculate_board_complexity(self.board)
        thinking_time = self.game_settings.calculate_thinking_time('checkers', move_count, complexity)
        
        # ปรับความลึกของการค้นหาตามเวลาคิด
        search_depth = min(settings['search_depth'], int(thinking_time * 1.5))
        
        # ใช้ MCTS สำหรับการค้นหาการเคลื่อนที่ที่ดีที่สุด
        from algorithm.mcts import MCTS
        mcts = MCTS()
        
        # ปรับพารามิเตอร์ตามระดับความยาก
        mcts.set_parameters(
            search_depth=search_depth,
            time_limit=thinking_time,
            pattern_weight=settings['pattern_weight'],
            randomness=settings['randomness'],
            king_capture_bonus=settings['king_capture_bonus']
        )
        
        # ทำให้ AI ช้าลงในโหมดง่ายเพื่อให้ผู้เล่นมีเวลาคิด
        if settings['ai_delay'] > 0:
            time.sleep(settings['ai_delay'])
        
        # ค้นหาการเคลื่อนที่ที่ดีที่สุด
        best_move = mcts.search(self.board, self.player_turn)
        return best_move
    
    def evaluate_board(self, board):
        """ประเมินค่ากระดาน"""
        settings = self.game_settings.adjust_settings('checkers')
        
        score = 0
        for row in range(self.ROWS):
            for col in range(self.COLS):
                piece = board[row][col]
                if piece:
                    if piece['piece'] == 'O':  # Player piece
                        score -= 1
                        if piece['king']:
                            score -= 2
                    else:  # AI piece
                        score += 1
                        if piece['king']:
                            score += 2
        
        # เพิ่มโบนัสสำหรับการจับกษัตริย์
        if self.must_jump:
            score += settings['king_capture_bonus']
        
        # ปรับคะแนนตามความซับซ้อนของกระดาน
        complexity = self.calculate_board_complexity(board)
        score *= (1 + complexity * 0.1)
        
        return score
    
    def minimax(self, depth, alpha, beta, maximizing_player):
        """Minimax algorithm with alpha-beta pruning
        
        Args:
            depth: Depth to search
            alpha, beta: Alpha-beta pruning parameters
            maximizing_player: True for AI's turn (maximizing), False for player's turn (minimizing)
            
        Returns:
            tuple: (best_move, best_score) where move is ((from_row, from_col), (to_row, to_col))
        """
        # Terminal cases
        if depth == 0 or self.game_over:
            return None, self.evaluate_board(self.board)
        
        # Find all valid moves for current player
        all_moves = {}  # (from_pos, to_pos): captured_list
        piece_type = 'X' if maximizing_player else 'O'
        
        # First check for jumps (they're mandatory)
        jumps_found = False
        
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if (self.board[row][col] is not None and 
                    self.board[row][col]['piece'] == piece_type):
                    jumps = self._get_jump_moves(row, col)
                    if jumps:
                        jumps_found = True
                        for to_pos, captured in jumps.items():
                            all_moves[((row, col), to_pos)] = captured
        
        # If no jumps, get regular moves
        if not jumps_found:
            for row in range(self.ROWS):
                for col in range(self.COLS):
                    if (self.board[row][col] is not None and 
                        self.board[row][col]['piece'] == piece_type):
                        regular_moves = self._get_regular_moves(row, col)
                        for to_pos, _ in regular_moves.items():
                            all_moves[((row, col), to_pos)] = []
        
        # If no valid moves, game is over for this player
        if not all_moves:
            # No moves means player loses
            return None, float('inf') if maximizing_player else float('-inf')
        
        # Track best move and score
        best_move = None
        
        if maximizing_player:
            best_score = float('-inf')
            for move, captured in all_moves.items():
                (from_row, from_col), (to_row, to_col) = move
                
                # Make the move
                self._make_temp_move(from_row, from_col, to_row, to_col, captured)
                
                # Recursive call
                _, score = self.minimax(depth - 1, alpha, beta, False)
                
                # Undo the move
                self._undo_temp_move(from_row, from_col, to_row, to_col, captured)
                
                # Update best score and move
                if score > best_score:
                    best_score = score
                    best_move = move
                
                # Alpha-beta pruning
                alpha = max(alpha, best_score)
                if alpha >= beta:
                    break
            
            return best_move, best_score
        
        else:  # Minimizing player
            best_score = float('inf')
            for move, captured in all_moves.items():
                (from_row, from_col), (to_row, to_col) = move
                
                # Make the move
                self._make_temp_move(from_row, from_col, to_row, to_col, captured)
                
                # Recursive call
                _, score = self.minimax(depth - 1, alpha, beta, True)
                
                # Undo the move
                self._undo_temp_move(from_row, from_col, to_row, to_col, captured)
                
                # Update best score and move
                if score < best_score:
                    best_score = score
                    best_move = move
                
                # Alpha-beta pruning
                beta = min(beta, best_score)
                if alpha >= beta:
                    break
            
            return best_move, best_score
    
    def _make_temp_move(self, from_row, from_col, to_row, to_col, captured):
        """Make a temporary move for the minimax algorithm"""
        # Store original board state
        self.original_board = deepcopy(self.board)
        self.original_turn = self.player_turn
        
        # Make the move
        piece = self.board[from_row][from_col]
        
        # Check for promotion
        if (piece['piece'] == 'O' and to_row == 0) or (piece['piece'] == 'X' and to_row == self.ROWS - 1):
            piece['king'] = True
        
        # Execute the move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Handle captures
        for r, c in captured:
            self.board[r][c] = None
        
        # Change turn
        self.player_turn = not self.player_turn
    
    def _undo_temp_move(self, from_row, from_col, to_row, to_col, captured):
        """Undo a temporary move made for the minimax algorithm"""
        # Restore original board state
        self.board = self.original_board
        self.player_turn = self.original_turn
    
    def ai_move_minimax(self):
        """Make an AI move using minimax algorithm
        
        Returns:
            bool: True if move was successful, False otherwise
        """
        if self.game_over or self.player_turn:
            return False
        
        # Use minimax to find the best move
        best_move, _ = self.minimax(depth=3, alpha=float('-inf'), beta=float('inf'), maximizing_player=True)
        
        if best_move:
            (from_row, from_col), (to_row, to_col) = best_move
            return self.make_move(from_row, from_col, to_row, to_col)
        else:
            # No valid moves for AI
            self.game_over = True
            self.winner = 'O'  # Player wins
            return True


# Test function for Checkers class
if __name__ == "__main__":
    game = Checkers()
    
    # Display initial board
    print("Initial board:")
    for row in game.board:
        print(row)
    
    # Test getting valid moves
    valid_moves = game.get_valid_moves(5, 0)
    print(f"\nValid moves for piece at (5,0): {valid_moves}")
    
    # Make a move
    print("\nMaking a move from (5,0) to (4,1)...")
    game.make_move(5, 0, 4, 1)
    
    # Display board after move
    print("\nBoard after move:")
    for row in game.board:
        print(row)
    
    # Test AI move
    print("\nMaking AI move...")
    game.ai_move_minimax()
    
    # Display final board
    print("\nBoard after AI move:")
    for row in game.board:
        print(row)
