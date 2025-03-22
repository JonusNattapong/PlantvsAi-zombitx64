import json
import os
import random
from copy import deepcopy

class Chess:
    """
    คลาสหลักสำหรับเกมหมากรุก (Chess)
    """
    def __init__(self):
        """Initialize Chess game"""
        self.ROWS = 8
        self.COLS = 8
        self.board = None
        self.game_over = False
        self.winner = None
        self.player_turn = True  # True for player (White), False for AI (Black)
        self.en_passant_target = None  # Square that can be captured via en passant
        self.castling_rights = {
            'K': True,  # White king-side
            'Q': True,  # White queen-side
            'k': True,  # Black king-side
            'q': True   # Black queen-side
        }
        self.halfmove_clock = 0  # For fifty-move rule
        self.fullmove_number = 1  # Increments after Black's move
        self.move_history = []  # List of moves in algebraic notation
        self.reset_game()
        self.stats = self.load_stats()
    
    def reset_game(self):
        """Reset the game to initial state"""
        # Create empty board
        self.board = [[None for _ in range(self.COLS)] for _ in range(self.ROWS)]
        
        # Place white pieces (player)
        # Pawns
        for col in range(self.COLS):
            self.board[6][col] = {'piece': 'P', 'color': 'white', 'moved': False}
        
        # Rooks
        self.board[7][0] = {'piece': 'R', 'color': 'white', 'moved': False}
        self.board[7][7] = {'piece': 'R', 'color': 'white', 'moved': False}
        
        # Knights
        self.board[7][1] = {'piece': 'N', 'color': 'white', 'moved': False}
        self.board[7][6] = {'piece': 'N', 'color': 'white', 'moved': False}
        
        # Bishops
        self.board[7][2] = {'piece': 'B', 'color': 'white', 'moved': False}
        self.board[7][5] = {'piece': 'B', 'color': 'white', 'moved': False}
        
        # Queen
        self.board[7][3] = {'piece': 'Q', 'color': 'white', 'moved': False}
        
        # King
        self.board[7][4] = {'piece': 'K', 'color': 'white', 'moved': False}
        
        # Place black pieces (AI)
        # Pawns
        for col in range(self.COLS):
            self.board[1][col] = {'piece': 'P', 'color': 'black', 'moved': False}
        
        # Rooks
        self.board[0][0] = {'piece': 'R', 'color': 'black', 'moved': False}
        self.board[0][7] = {'piece': 'R', 'color': 'black', 'moved': False}
        
        # Knights
        self.board[0][1] = {'piece': 'N', 'color': 'black', 'moved': False}
        self.board[0][6] = {'piece': 'N', 'color': 'black', 'moved': False}
        
        # Bishops
        self.board[0][2] = {'piece': 'B', 'color': 'black', 'moved': False}
        self.board[0][5] = {'piece': 'B', 'color': 'black', 'moved': False}
        
        # Queen
        self.board[0][3] = {'piece': 'Q', 'color': 'black', 'moved': False}
        
        # King
        self.board[0][4] = {'piece': 'K', 'color': 'black', 'moved': False}
        
        # Reset game state variables
        self.game_over = False
        self.winner = None
        self.player_turn = True
        self.en_passant_target = None
        self.castling_rights = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.move_history = []
    
    def load_stats(self):
        """Load game statistics from file"""
        stats_file = 'chess_stats.json'
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading Chess stats: {e}")
        
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
        stats_file = 'chess_stats.json'
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Error saving Chess stats: {e}")
    
    def update_stats(self, ai_mode_name):
        """Update game statistics after a game ends"""
        self.stats["total_games"] += 1
        
        # Initialize AI mode stats if not exists
        if ai_mode_name not in self.stats["ai_mode_stats"]:
            self.stats["ai_mode_stats"][ai_mode_name] = {"wins": 0, "losses": 0, "draws": 0}
        
        # Update based on winner
        if self.winner == 'black':  # AI wins
            self.stats["ai_wins"] += 1
            self.stats["ai_mode_stats"][ai_mode_name]["wins"] += 1
        elif self.winner == 'white':  # Player wins
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
        """
        Get all valid moves for a piece at the given position
        Returns:
            dict: Dictionary with valid destinations as keys and special move info as values
        """
        if (row < 0 or row >= self.ROWS or col < 0 or col >= self.COLS or 
            self.board[row][col] is None):
            return {}
        
        piece = self.board[row][col]
        
        # Check if it's the correct player's turn
        current_color = 'white' if self.player_turn else 'black'
        if piece['color'] != current_color:
            return {}
        
        piece_type = piece['piece']
        color = piece['color']
        
        # Calculate moves based on piece type
        valid_moves = {}
        
        if piece_type == 'P':
            valid_moves = self._get_pawn_moves(row, col, color)
        elif piece_type == 'R':
            valid_moves = self._get_rook_moves(row, col, color)
        elif piece_type == 'N':
            valid_moves = self._get_knight_moves(row, col, color)
        elif piece_type == 'B':
            valid_moves = self._get_bishop_moves(row, col, color)
        elif piece_type == 'Q':
            valid_moves = self._get_queen_moves(row, col, color)
        elif piece_type == 'K':
            valid_moves = self._get_king_moves(row, col, color)
        
        # Filter out moves that would leave the king in check
        valid_moves = self._filter_check_moves(row, col, valid_moves)
        
        return valid_moves
    
    def _get_pawn_moves(self, row, col, color):
        """Get valid pawn moves"""
        valid_moves = {}
        direction = -1 if color == 'white' else 1  # White moves up, black moves down
        start_row = 6 if color == 'white' else 1   # Starting row for pawns
        
        # Forward move
        if 0 <= row + direction < 8 and self.board[row + direction][col] is None:
            valid_moves[(row + direction, col)] = {}
            
            # Double move from starting position
            if (row == start_row and 
                0 <= row + 2*direction < 8 and 
                self.board[row + 2*direction][col] is None):
                
                valid_moves[(row + 2*direction, col)] = {'double_move': True}
                # Mark the skipped square as the en passant target
                valid_moves[(row + 2*direction, col)]['en_passant'] = (row + direction, col)
        
        # Capture moves (diagonal)
        for dc in [-1, 1]:
            if 0 <= row + direction < 8 and 0 <= col + dc < 8:
                # Regular capture
                if (self.board[row + direction][col + dc] is not None and 
                    self.board[row + direction][col + dc]['color'] != color):
                    valid_moves[(row + direction, col + dc)] = {'capture': True}
                
                # En passant capture
                elif (self.en_passant_target is not None and 
                      (row + direction, col + dc) == self.en_passant_target):
                    # Determine the position of the pawn to be captured
                    captured_row = row
                    captured_col = col + dc
                    valid_moves[(row + direction, col + dc)] = {
                        'en_passant_capture': True,
                        'captured_piece': (captured_row, captured_col)
                    }
        
        # Check for promotion
        promotion_row = 0 if color == 'white' else 7
        for move in list(valid_moves.keys()):
            if move[0] == promotion_row:
                valid_moves[move]['promotion'] = True
                
        return valid_moves
    
    def _get_rook_moves(self, row, col, color):
        """Get valid rook moves"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, down, left, right
        return self._get_sliding_moves(row, col, color, directions)
    
    def _get_bishop_moves(self, row, col, color):
        """Get valid bishop moves"""
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Diagonals
        return self._get_sliding_moves(row, col, color, directions)
    
    def _get_queen_moves(self, row, col, color):
        """Get valid queen moves (combination of rook and bishop)"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self._get_sliding_moves(row, col, color, directions)
    
    def _get_sliding_moves(self, row, col, color, directions):
        """Helper for calculating sliding piece moves (rook, bishop, queen)"""
        valid_moves = {}
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            
            while 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] is None:
                    # Empty square - valid move
                    valid_moves[(r, c)] = {}
                else:
                    # Square contains a piece
                    if self.board[r][c]['color'] != color:
                        # Enemy piece - can capture
                        valid_moves[(r, c)] = {'capture': True}
                    # Stop sliding in this direction
                    break
                
                # Continue sliding
                r += dr
                c += dc
        
        return valid_moves
    
    def _get_knight_moves(self, row, col, color):
        """Get valid knight moves"""
        valid_moves = {}
        moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        
        for dr, dc in moves:
            r, c = row + dr, col + dc
            
            if 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] is None:
                    # Empty square
                    valid_moves[(r, c)] = {}
                elif self.board[r][c]['color'] != color:
                    # Enemy piece
                    valid_moves[(r, c)] = {'capture': True}
        
        return valid_moves
    
    def _get_king_moves(self, row, col, color):
        """Get valid king moves including castling"""
        valid_moves = {}
        
        # Regular king moves - one square in any direction
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue  # Skip the current position
                
                r, c = row + dr, col + dc
                
                if 0 <= r < 8 and 0 <= c < 8:
                    if self.board[r][c] is None:
                        # Empty square
                        valid_moves[(r, c)] = {}
                    elif self.board[r][c]['color'] != color:
                        # Enemy piece
                        valid_moves[(r, c)] = {'capture': True}
        
        # Castling
        if not self.board[row][col]['moved']:
            # Check kingside castling
            castling_right = 'K' if color == 'white' else 'k'
            if self.castling_rights[castling_right]:
                # Check if squares between king and rook are empty
                if (self.board[row][col+1] is None and 
                    self.board[row][col+2] is None and 
                    self.board[row][7] is not None and 
                    self.board[row][7]['piece'] == 'R' and 
                    self.board[row][7]['color'] == color and 
                    not self.board[row][7]['moved']):
                    
                    # Check if king would pass through check
                    if (not self._is_square_attacked(row, col, color) and 
                        not self._is_square_attacked(row, col+1, color) and 
                        not self._is_square_attacked(row, col+2, color)):
                        
                        valid_moves[(row, col+2)] = {
                            'castling': 'kingside',
                            'rook_from': (row, 7),
                            'rook_to': (row, col+1)
                        }
            
            # Check queenside castling
            castling_right = 'Q' if color == 'white' else 'q'
            if self.castling_rights[castling_right]:
                # Check if squares between king and rook are empty
                if (self.board[row][col-1] is None and 
                    self.board[row][col-2] is None and 
                    self.board[row][col-3] is None and  # Extra empty square for queenside
                    self.board[row][0] is not None and 
                    self.board[row][0]['piece'] == 'R' and 
                    self.board[row][0]['color'] == color and 
                    not self.board[row][0]['moved']):
                    
                    # Check if king would pass through check
                    if (not self._is_square_attacked(row, col, color) and 
                        not self._is_square_attacked(row, col-1, color) and 
                        not self._is_square_attacked(row, col-2, color)):
                        
                        valid_moves[(row, col-2)] = {
                            'castling': 'queenside',
                            'rook_from': (row, 0),
                            'rook_to': (row, col-1)
                        }
        
        return valid_moves
    
    def _is_square_attacked(self, row, col, color):
        """Check if a square is attacked by any opponent pieces"""
        # Determine opponent color
        opponent_color = 'black' if color == 'white' else 'white'
        
        # Check for pawn attacks
        pawn_direction = 1 if color == 'white' else -1  # Direction pawns attack from
        for dc in [-1, 1]:
            r, c = row + pawn_direction, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if (piece is not None and piece['color'] == opponent_color and 
                    piece['piece'] == 'P'):
                    return True
        
        # Check for knight attacks
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if (piece is not None and piece['color'] == opponent_color and 
                    piece['piece'] == 'N'):
                    return True
        
        # Check for sliding attacks (queen, rook, bishop)
        # Rook directions
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if piece is not None:
                    if piece['color'] == opponent_color and (
                        piece['piece'] == 'R' or piece['piece'] == 'Q'):
                        return True
                    break  # Blocked by a piece
                r += dr
                c += dc
        
        # Bishop directions
        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if piece is not None:
                    if piece['color'] == opponent_color and (
                        piece['piece'] == 'B' or piece['piece'] == 'Q'):
                        return True
                    break  # Blocked by a piece
                r += dr
                c += dc
        
        # Check for king attacks
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    piece = self.board[r][c]
                    if (piece is not None and piece['color'] == opponent_color and 
                        piece['piece'] == 'K'):
                        return True
        
        return False
    
    def _filter_check_moves(self, from_row, from_col, valid_moves):
        """Filter out moves that would leave king in check"""
        filtered_moves = {}
        
        # Get color of moving piece
        color = self.board[from_row][from_col]['color']
        
        # Try each move and see if it leaves the king in check
        for (to_row, to_col), move_info in valid_moves.items():
            # Make a temporary copy of the board
            temp_board = deepcopy(self.board)
            
            # Execute the move temporarily
            temp_board[to_row][to_col] = temp_board[from_row][from_col]
            temp_board[from_row][from_col] = None
            
            # Handle special moves that capture in different ways
            if 'en_passant_capture' in move_info:
                captured_row, captured_col = move_info['captured_piece']
                temp_board[captured_row][captured_col] = None
            
            # If the move was castling, move the rook too
            if 'castling' in move_info:
                rook_from = move_info['rook_from']
                rook_to = move_info['rook_to']
                temp_board[rook_to[0]][rook_to[1]] = temp_board[rook_from[0]][rook_from[1]]
                temp_board[rook_from[0]][rook_from[1]] = None
            
            # Find king's position
            king_pos = self._find_king(temp_board, color)
            
            # If king wasn't found (shouldn't happen), skip this move
            if not king_pos:
                continue
            
            # Check if king is in check after this move
            king_row, king_col = king_pos
            
            # If the king is not in check after the move, it's valid
            if not self._is_square_attacked_on_board(temp_board, king_row, king_col, color):
                filtered_moves[(to_row, to_col)] = move_info
        
        return filtered_moves
    
    def _is_square_attacked_on_board(self, board, row, col, color):
        """Check if a square is attacked on a specific board configuration"""
        # Determine opponent color
        opponent_color = 'black' if color == 'white' else 'white'
        
        # Check for pawn attacks
        pawn_direction = 1 if color == 'white' else -1  # Direction pawns attack from
        for dc in [-1, 1]:
            r, c = row + pawn_direction, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = board[r][c]
                if (piece is not None and piece['color'] == opponent_color and 
                    piece['piece'] == 'P'):
                    return True
        
        # Check for knight attacks
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = board[r][c]
                if (piece is not None and piece['color'] == opponent_color and 
                    piece['piece'] == 'N'):
                    return True
        
        # Check for sliding attacks (queen, rook, bishop)
        # Rook directions
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = board[r][c]
                if piece is not None:
                    if piece['color'] == opponent_color and (
                        piece['piece'] == 'R' or piece['piece'] == 'Q'):
                        return True
                    break  # Blocked by a piece
                r += dr
                c += dc
        
        # Bishop directions
        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = board[r][c]
                if piece is not None:
                    if piece['color'] == opponent_color and (
                        piece['piece'] == 'B' or piece['piece'] == 'Q'):
                        return True
                    break  # Blocked by a piece
                r += dr
                c += dc
        
        # Check for king attacks
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    piece = board[r][c]
                    if (piece is not None and piece['color'] == opponent_color and 
                        piece['piece'] == 'K'):
                        return True
        
        return False
    
    def _find_king(self, board, color):
        """Find the position of a king of the specified color"""
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if (piece is not None and piece['color'] == color and 
                    piece['piece'] == 'K'):
                    return (row, col)
        return None
    
    def make_move(self, from_row, from_col, to_row, to_col, promotion_piece=None):
        """Make a move from one position to another
        
        Args:
            from_row, from_col: Starting position
            to_row, to_col: Ending position
            promotion_piece: Piece type for pawn promotion (Q, R, B, N)
            
        Returns:
            bool: True if move was successful, False otherwise
        """
        # Check if the move is valid
        valid_moves = self.get_valid_moves(from_row, from_col)
        
        if (to_row, to_col) not in valid_moves:
            return False
        
        move_info = valid_moves[(to_row, to_col)]
        piece = self.board[from_row][from_col]
        
        # Update halfmove clock
        if piece['piece'] == 'P' or 'capture' in move_info:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        
        # Handle en passant target
        self.en_passant_target = None
        if 'en_passant' in move_info:
            self.en_passant_target = move_info['en_passant']
        
        # Handle castling
        if 'castling' in move_info:
            rook_from = move_info['rook_from']
            rook_to = move_info['rook_to']
            
            # Move the rook
            self.board[rook_to[0]][rook_to[1]] = self.board[rook_from[0]][rook_from[1]]
            self.board[rook_from[0]][rook_from[1]] = None
            self.board[rook_to[0]][rook_to[1]]['moved'] = True
        
        # Update castling rights
        if piece['piece'] == 'K':
            if piece['color'] == 'white':
                self.castling_rights['K'] = False
                self.castling_rights['Q'] = False
            else:
                self.castling_rights['k'] = False
                self.castling_rights['q'] = False
        elif piece['piece'] == 'R':
            if from_row == 7 and from_col == 0:  # White queenside rook
                self.castling_rights['Q'] = False
            elif from_row == 7 and from_col == 7:  # White kingside rook
                self.castling_rights['K'] = False
            elif from_row == 0 and from_col == 0:  # Black queenside rook
                self.castling_rights['q'] = False
            elif from_row == 0 and from_col == 7:  # Black kingside rook
                self.castling_rights['k'] = False
        
        # Handle en passant capture
        if 'en_passant_capture' in move_info:
            captured_row, captured_col = move_info['captured_piece']
            self.board[captured_row][captured_col] = None
        
        # Move the piece
        piece['moved'] = True
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Handle pawn promotion
        if 'promotion' in move_info and piece['piece'] == 'P':
            # Default to Queen if no piece specified
            promotion = promotion_piece if promotion_piece else 'Q'
            self.board[to_row][to_col]['piece'] = promotion
        
        # Record the move in algebraic notation
        self._record_move(from_row, from_col, to_row, to_col, piece['piece'], 
                         'capture' in move_info, promotion_piece)
        
        # Update game state
        self._check_game_over()
        
        # Update fullmove number after black's move
        if not self.player_turn:  # After Black's move
            self.fullmove_number += 1
        
        # Switch turns if game not over
        if not self.game_over:
            self.player_turn = not self.player_turn
        
        return True
    
    def _record_move(self, from_row, from_col, to_row, to_col, piece_type, is_capture, promotion=None):
        """Record move in algebraic notation"""
        files = "abcdefgh"
        ranks = "87654321"
        
        from_square = files[from_col] + ranks[from_row]
        to_square = files[to_col] + ranks[to_row]
        
        notation = ""
        
        # Add piece type (except for pawns)
        if piece_type != 'P':
            notation += piece_type
        
        # Add capture symbol if applicable
        if is_capture:
            if piece_type == 'P':
                notation += files[from_col]  # Include the file for pawn captures
            notation += 'x'
        
        # Add destination square
        notation += to_square
        
        # Add promotion piece if applicable
        if promotion:
            notation += "=" + promotion
        
        # Check for check or checkmate (would need to check opponent's king status)
        # For simplicity, not implementing here
        
        # Add the move to the history
        self.move_history.append(notation)
    
    def _check_game_over(self):
        """Check if the game is over due to checkmate, stalemate, or other conditions"""
        current_color = 'white' if self.player_turn else 'black'
        king_pos = self._find_king(self.board, current_color)
        
        if not king_pos:
            # King not found (shouldn't happen in normal play)
            return
        
        king_row, king_col = king_pos
        
        # Check if king is in check
        in_check = self._is_square_attacked(king_row, king_col, current_color)
        
        # Check if the player has any valid moves
        has_valid_moves = False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece['color'] == current_color:
                    moves = self.get_valid_moves(row, col)
                    if moves:
                        has_valid_moves = True
                        break
            if has_valid_moves:
                break
        
        if not has_valid_moves:
            self.game_over = True
            if in_check:
                # Checkmate
                self.winner = 'black' if current_color == 'white' else 'white'
            else:
                # Stalemate
                self.winner = None
        
        # Check for 50-move rule
        elif self.halfmove_clock >= 50:
            self.game_over = True
            self.winner = None  # Draw
        
        # Check for insufficient material
        elif self._has_insufficient_material():
            self.game_over = True
            self.winner = None  # Draw
    
    def _has_insufficient_material(self):
        """Check for draw due to insufficient material"""
        # Count pieces
        white_pieces = []
        black_pieces = []
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    if piece['color'] == 'white':
                        white_pieces.append(piece['piece'])
                    else:
                        black_pieces.append(piece['piece'])
        
        # King vs King
        if len(white_pieces) == 1 and len(black_pieces) == 1:
            return True
        
        # King + Bishop/Knight vs King
        if (len(white_pieces) == 2 and len(black_pieces) == 1 and 
            ('B' in white_pieces or 'N' in white_pieces)):
            return True
        if (len(black_pieces) == 2 and len(white_pieces) == 1 and 
            ('B' in black_pieces or 'N' in black_pieces)):
            return True
        
        # King + Bishop vs King + Bishop on same color
        # (would need to check bishop square colors - simplifying here)
        
        return False
    
    def evaluate_board(self, color='black'):
        """Evaluate the current position from the perspective of the given color"""
        # Piece values
        piece_values = {
            'P': 1,   # Pawn
            'N': 3,   # Knight
            'B': 3,   # Bishop
            'R': 5,   # Rook
            'Q': 9,   # Queen
            'K': 0    # King (not included in material count)
        }
        
        # Position evaluation weights (piece-square tables)
        pawn_position = [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5],
            [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5],
            [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
            [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5],
            [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
            [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        ]
        
        knight_position = [
            [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
            [-4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0],
            [-3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0],
            [-3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0],
            [-3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0],
            [-3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0],
            [-4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0],
            [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
        ]
        
        bishop_position = [
            [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
            [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
            [-1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0],
            [-1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0],
            [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
            [-1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
            [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
        ]
        
        rook_position = [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0]
        ]
        
        queen_position = [
            [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
            [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
            [-1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
            [-0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
            [0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
            [-1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
            [-1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, -1.0],
            [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
        ]
        
        king_position_middlegame = [
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
            [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
            [2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
            [2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0]
        ]
        
        # Calculate score for each side
        white_score = 0
        black_score = 0
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    piece_type = piece['piece']
                    piece_color = piece['color']
                    
                    # Base piece value
                    value = piece_values[piece_type]
                    
                    # Add position-based evaluation
                    if piece_type == 'P':
                        position_value = pawn_position[row][col]
                    elif piece_type == 'N':
                        position_value = knight_position[row][col]
                    elif piece_type == 'B':
                        position_value = bishop_position[row][col]
                    elif piece_type == 'R':
                        position_value = rook_position[row][col]
                    elif piece_type == 'Q':
                        position_value = queen_position[row][col]
                    elif piece_type == 'K':
                        position_value = king_position_middlegame[row][col]
                    else:
                        position_value = 0
                    
                    # Add to appropriate score
                    if piece_color == 'white':
                        # Flip table for white pieces
                        adjusted_position_value = position_value if row < 4 else position_value * 0.5
                        white_score += value + adjusted_position_value
                    else:
                        # For black pieces, the tables are from their perspective
                        adjusted_position_value = position_value if row >= 4 else position_value * 0.5
                        black_score += value + adjusted_position_value
        
        # Return the score from the given color's perspective
        if color == 'black':
            return black_score - white_score
        else:
            return white_score - black_score
    
    def minimax(self, depth, alpha, beta, maximizing_player):
        """Minimax algorithm with alpha-beta pruning for chess AI
        
        Args:
            depth: Maximum depth to search
            alpha, beta: Alpha-beta pruning parameters
            maximizing_player: True for AI (black), False for player (white)
            
        Returns:
            tuple: (best_move, best_score) where move is ((from_row, from_col), (to_row, to_col))
        """
        if depth == 0 or self.game_over:
            # Evaluate the board and return
            return None, self.evaluate_board('black' if maximizing_player else 'white')
        
        # Determine the current color
        current_color = 'black' if maximizing_player else 'white'
        best_move = None
        
        if maximizing_player:  # AI's turn (black)
            best_score = float('-inf')
            
            # Generate all possible moves for black
            for from_row in range(8):
                for from_col in range(8):
                    piece = self.board[from_row][from_col]
                    if piece and piece['color'] == 'black':
                        moves = self.get_valid_moves(from_row, from_col)
                        
                        for to_pos, move_info in moves.items():
                            to_row, to_col = to_pos
                            
                            # Make temporary move
                            temp_board = deepcopy(self.board)
                            temp_game = Chess()
                            temp_game.board = temp_board
                            temp_game.player_turn = self.player_turn
                            temp_game.en_passant_target = self.en_passant_target
                            temp_game.castling_rights = self.castling_rights.copy()
                            
                            # Make the move
                            promotion = 'Q' if 'promotion' in move_info else None
                            if temp_game.make_move(from_row, from_col, to_row, to_col, promotion):
                                # Recursive call
                                _, score = temp_game.minimax(depth - 1, alpha, beta, False)
                                
                                # Update best move
                                if score > best_score:
                                    best_score = score
                                    best_move = ((from_row, from_col), (to_row, to_col))
                                
                                # Alpha-beta pruning
                                alpha = max(alpha, best_score)
                                if beta <= alpha:
                                    break
            
            return best_move, best_score
            
        else:  # Player's turn (white)
            best_score = float('inf')
            
            # Generate all possible moves for white
            for from_row in range(8):
                for from_col in range(8):
                    piece = self.board[from_row][from_col]
                    if piece and piece['color'] == 'white':
                        moves = self.get_valid_moves(from_row, from_col)
                        
                        for to_pos, move_info in moves.items():
                            to_row, to_col = to_pos
                            
                            # Make temporary move
                            temp_board = deepcopy(self.board)
                            temp_game = Chess()
                            temp_game.board = temp_board
                            temp_game.player_turn = self.player_turn
                            temp_game.en_passant_target = self.en_passant_target
                            temp_game.castling_rights = self.castling_rights.copy()
                            
                            # Make the move
                            promotion = 'Q' if 'promotion' in move_info else None
                            if temp_game.make_move(from_row, from_col, to_row, to_col, promotion):
                                # Recursive call
                                _, score = temp_game.minimax(depth - 1, alpha, beta, True)
                                
                                # Update best move
                                if score < best_score:
                                    best_score = score
                                    best_move = ((from_row, from_col), (to_row, to_col))
                                
                                # Alpha-beta pruning
                                beta = min(beta, best_score)
                                if beta <= alpha:
                                    break
            
            return best_move, best_score
    
    def ai_move_minimax(self, depth=2):
        """Make an AI move using minimax algorithm
        
        Args:
            depth: Search depth for minimax
            
        Returns:
            bool: True if move was successful, False otherwise
        """
        if self.game_over or self.player_turn:  # Only make moves if it's AI's turn
            return False
        
        # Use minimax to find the best move
        best_move, _ = self.minimax(depth, float('-inf'), float('inf'), True)
        
        if best_move:
            (from_row, from_col), (to_row, to_col) = best_move
            
            # Check if this is a promotion move
            promotion = None
            piece = self.board[from_row][from_col]
            if piece and piece['piece'] == 'P' and to_row == 7:  # Pawn reaching promotion rank
                promotion = 'Q'  # Always promote to queen for AI
            
            # Make the move
            return self.make_move(from_row, from_col, to_row, to_col, promotion)
        
        # No valid move found (shouldn't happen in normal play)
        return False


# Test function for Chess class
if __name__ == "__main__":
    game = Chess()
    
    # Display initial board
    print("Initial board:")
    for row in game.board:
        print([f"{p['piece']}{p['color'][0]}" if p else "..." for p in row])
    
    # Test getting valid moves
    valid_moves = game.get_valid_moves(6, 0)  # White pawn
    print(f"\nValid moves for pawn at (6,0): {valid_moves}")
    
    # Make a player move
    print("\nMaking a player move...")
    game.make_move(6, 0, 4, 0)  # Move pawn forward 2 squares
    
    # Display board after player move
    print("\nBoard after player move:")
    for row in game.board:
        print([f"{p['piece']}{p['color'][0]}" if p else "..." for p in row])
    
    # Make an AI move
    print("\nMaking an AI move...")
    game.ai_move_minimax(1)  # Depth 1 for quick testing
    
    # Display board after AI move
    print("\nBoard after AI move:")
    for row in game.board:
        print([f"{p['piece']}{p['color'][0]}" if p else "..." for p in row])
