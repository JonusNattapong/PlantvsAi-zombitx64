from flask import Flask, render_template, jsonify, request
import random
import json
import os

app = Flask(__name__)

# Game state will be stored on the server side
game_states = {}

# AI modes
AI_MODES = ["Minimax", "Pattern Recognition"]

# Board dimensions
BOARD_ROWS = 3
BOARD_COLS = 3

# Load game stats
def load_game_stats():
    try:
        if os.path.exists('game_stats.json'):
            with open('game_stats.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading game stats: {e}")
    
    # Default stats
    return {
        "total_games": 0,
        "player_wins": 0,
        "ai_wins": 0,
        "draws": 0,
        "win_rate": 0,
        "ai_mode_stats": {
            "Minimax": {"wins": 0, "losses": 0, "draws": 0},
            "Pattern Recognition": {"wins": 0, "losses": 0, "draws": 0}
        }
    }

# Load pattern data
def load_pattern_data():
    try:
        if os.path.exists('player_patterns.json'):
            with open('player_patterns.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading pattern data: {e}")
    
    # Default pattern data
    return {}

# Save game stats
def save_game_stats(game_stats):
    try:
        with open('game_stats.json', 'w') as f:
            json.dump(game_stats, f, indent=2)
    except Exception as e:
        print(f"Error saving game stats: {e}")

# Save pattern data
def save_pattern_data(player_patterns):
    try:
        with open('player_patterns.json', 'w') as f:
            json.dump(player_patterns, f, indent=2)
    except Exception as e:
        print(f"Error saving pattern data: {e}")

# Check for win condition
def check_win(board):
    # Check horizontal
    for row in range(BOARD_ROWS):
        if board[row][0] == board[row][1] == board[row][2] and board[row][0] is not None:
            return board[row][0]
    
    # Check vertical
    for col in range(BOARD_COLS):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] is not None:
            return board[0][col]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]
    
    return None

# Check if board is full
def is_board_full(board):
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] is None:
                return False
    return True

# Minimax algorithm
def minimax(board, depth, is_maximizing):
    # Check terminal states
    winner = check_win(board)
    if winner == 'X':  # AI
        return 10 - depth
    if winner == 'O':  # Player
        return depth - 10
    
    # Check for draw
    if is_board_full(board):
        return 0
    
    if is_maximizing:
        best_score = float('-inf')
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if board[row][col] is None:
                    board[row][col] = 'X'  # AI
                    score = minimax(board, depth + 1, False)
                    board[row][col] = None  # Undo move
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if board[row][col] is None:
                    board[row][col] = 'O'  # Player
                    score = minimax(board, depth + 1, True)
                    board[row][col] = None  # Undo move
                    best_score = min(score, best_score)
        return best_score

# Find best move using minimax
def best_move_minimax(board):
    # For first AI move, use a predefined strategy for better performance
    empty_count = sum(1 for row in range(BOARD_ROWS) for col in range(BOARD_COLS) if board[row][col] is None)
    
    if empty_count == 9:  # First move of the game
        # Start with a corner for variety
        return random.choice([(0, 0), (0, 2), (2, 0), (2, 2)])
    
    if empty_count == 8:  # Second move of the game
        # If player took center, take a corner
        if board[1][1] == 'O':
            return random.choice([(0, 0), (0, 2), (2, 0), (2, 2)])
        # If player took a corner, take center
        elif board[0][0] == 'O' or board[0][2] == 'O' or board[2][0] == 'O' or board[2][2] == 'O':
            return (1, 1)
        # If player took a side, take center
        else:
            return (1, 1)
    
    # For other moves, use minimax
    best_score = float('-inf')
    move = None
    
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] is None:
                board[row][col] = 'X'  # AI
                score = minimax(board, 0, False)
                board[row][col] = None  # Undo move
                if score > best_score:
                    best_score = score
                    move = (row, col)
    
    return move

# Pattern recognition move
def pattern_recognition_move(board, player_patterns, player_id):
    # Convert board to string representation
    def board_to_string(board):
        result = ""
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if board[row][col] is None:
                    result += "_"
                else:
                    result += board[row][col]
        return result
    
    board_str = board_to_string(board)
    
    # Check if we have pattern data for this player
    if player_id not in player_patterns:
        # Fallback to minimax if no pattern data
        return best_move_minimax(board)
    
    # Look for board in patterns
    board_patterns = player_patterns[player_id].get("board_patterns", {})
    
    if board_str in board_patterns:
        # Pattern found - analyze player's likely moves
        moves = board_patterns[board_str]
        
        # Count move frequencies
        move_counts = {}
        for move in moves:
            if move in move_counts:
                move_counts[move] += 1
            else:
                move_counts[move] = 1
        
        # Find the most common move
        most_common_move = None
        highest_count = 0
        
        for move, count in move_counts.items():
            if count > highest_count:
                row, col = map(int, move.split(","))
                if board[row][col] is None:  # Make sure the move is still valid
                    most_common_move = (row, col)
                    highest_count = count
        
        # If we found a valid move, make it
        if most_common_move is not None:
            row, col = most_common_move
            
            # Check if this is a winning move for player
            board[row][col] = 'O'  # Temporarily place player's mark
            if check_win(board) == 'O':
                board[row][col] = None  # Reset
                
                # Block this move
                return (row, col)
            
            board[row][col] = None  # Reset
            
            # Make a move elsewhere
            # First check if AI can win in next move
            for r in range(BOARD_ROWS):
                for c in range(BOARD_COLS):
                    if board[r][c] is None:
                        board[r][c] = 'X'  # Try AI move
                        if check_win(board) == 'X':
                            board[r][c] = None  # Reset
                            return (r, c)  # Winning move, take it
                        board[r][c] = None  # Reset
            
            # If not, block the player's predicted move
            return (row, col)
    
    # Fallback to minimax if pattern not found or no valid move
    return best_move_minimax(board)

# AI move function
def ai_move(session_id):
    if session_id not in game_states:
        return {"error": "Game session not found"}
    
    game_state = game_states[session_id]
    board = game_state["board"]
    ai_mode = game_state["ai_mode"]
    
    # Make a move based on the selected AI mode
    if ai_mode == 0:  # Minimax
        row, col = best_move_minimax(board)
    else:  # Pattern Recognition
        player_patterns = load_pattern_data()
        row, col = pattern_recognition_move(board, player_patterns, session_id)
    
    # Place the AI's mark
    board[row][col] = 'X'
    
    # Check for win or draw
    winner = check_win(board)
    game_over = winner is not None or is_board_full(board)
    
    # Update game state
    game_state["board"] = board
    game_state["player_turn"] = True
    game_state["game_over"] = game_over
    game_state["winner"] = winner
    
    # Update game stats if game is over
    if game_over:
        update_game_stats(session_id)
    
    return {
        "board": board,
        "player_turn": True,
        "game_over": game_over,
        "winner": winner,
        "move": {"row": row, "col": col}
    }

# Update game stats
def update_game_stats(session_id):
    if session_id not in game_states:
        return
    
    game_state = game_states[session_id]
    winner = game_state["winner"]
    ai_mode = game_state["ai_mode"]
    ai_mode_name = AI_MODES[ai_mode]
    
    # Load current stats
    game_stats = load_game_stats()
    
    # Update total games
    game_stats["total_games"] += 1
    
    # Update mode-specific stats
    if ai_mode_name not in game_stats["ai_mode_stats"]:
        game_stats["ai_mode_stats"][ai_mode_name] = {"wins": 0, "losses": 0, "draws": 0}
    
    # Update winner stats
    if winner == 'X':  # AI wins
        game_stats["ai_wins"] += 1
        game_stats["ai_mode_stats"][ai_mode_name]["wins"] += 1
    elif winner == 'O':  # Player wins
        game_stats["player_wins"] += 1
        game_stats["ai_mode_stats"][ai_mode_name]["losses"] += 1
    else:  # Draw
        game_stats["draws"] += 1
        game_stats["ai_mode_stats"][ai_mode_name]["draws"] += 1
    
    # Calculate win rate
    if game_stats["total_games"] > 0:
        game_stats["win_rate"] = round((game_stats["player_wins"] / game_stats["total_games"]) * 100)
    
    # Save updated stats
    save_game_stats(game_stats)

# Record a move for pattern analysis
def record_move(session_id, row, col, is_player):
    if session_id not in game_states:
        return
    
    # Load current patterns
    player_patterns = load_pattern_data()
    
    # Get the board state before the move
    game_state = game_states[session_id]
    board = game_state["board"]
    
    # Convert board to string representation
    def board_to_string(board):
        result = ""
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if board[row][col] is None:
                    result += "_"
                else:
                    result += board[row][col]
        return result
    
    board_str = board_to_string(board)
    
    # Initialize player pattern data if not exists
    if session_id not in player_patterns:
        player_patterns[session_id] = {
            "games_played": 0,
            "win_rate": 0,
            "draw_rate": 0,
            "loss_rate": 0,
            "board_patterns": {},
            "first_moves": {},
            "favorite_moves": {}
        }
    
    # Record move in board patterns
    if is_player:
        if board_str not in player_patterns[session_id]["board_patterns"]:
            player_patterns[session_id]["board_patterns"][board_str] = []
        
        player_patterns[session_id]["board_patterns"][board_str].append(f"{row},{col}")
    
    # Save updated patterns
    save_pattern_data(player_patterns)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    data = request.get_json()
    session_id = data.get('session_id', str(random.randint(10000, 99999)))
    ai_mode = data.get('ai_mode', 0)  # Default to Minimax
    
    # Initialize game state
    game_states[session_id] = {
        "board": [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)],
        "player_turn": True,
        "game_over": False,
        "winner": None,
        "ai_mode": ai_mode
    }
    
    return jsonify({
        "session_id": session_id,
        "board": game_states[session_id]["board"],
        "player_turn": True,
        "game_over": False,
        "winner": None,
        "ai_mode": ai_mode
    })

@app.route('/api/change_ai_mode', methods=['POST'])
def change_ai_mode():
    data = request.get_json()
    session_id = data.get('session_id')
    ai_mode = data.get('ai_mode', 0)
    
    if session_id not in game_states:
        return jsonify({"error": "Game session not found"}), 404
    
    game_states[session_id]["ai_mode"] = ai_mode
    
    return jsonify({
        "session_id": session_id,
        "ai_mode": ai_mode
    })

@app.route('/api/make_move', methods=['POST'])
def make_move():
    data = request.get_json()
    session_id = data.get('session_id')
    row = data.get('row')
    col = data.get('col')
    
    if session_id not in game_states:
        return jsonify({"error": "Game session not found"}), 404
    
    game_state = game_states[session_id]
    
    # Check if the move is valid
    if (not game_state["player_turn"] or 
        game_state["game_over"] or 
        game_state["board"][row][col] is not None):
        return jsonify({"error": "Invalid move"}), 400
    
    # Make the player's move
    game_state["board"][row][col] = 'O'
    
    # Record move for pattern analysis
    record_move(session_id, row, col, True)
    
    # Check for win or draw
    winner = check_win(game_state["board"])
    game_over = winner is not None or is_board_full(game_state["board"])
    
    if game_over:
        game_state["game_over"] = True
        game_state["winner"] = winner
        update_game_stats(session_id)
        
        return jsonify({
            "board": game_state["board"],
            "player_turn": False,
            "game_over": True,
            "winner": winner
        })
    
    # Switch turn to AI
    game_state["player_turn"] = False
    
    # Make AI move
    ai_result = ai_move(session_id)
    
    # Record AI move for pattern analysis
    if "move" in ai_result:
        record_move(session_id, ai_result["move"]["row"], ai_result["move"]["col"], False)
    
    return jsonify(ai_result)

@app.route('/api/reset_game', methods=['POST'])
def reset_game():
    data = request.get_json()
    session_id = data.get('session_id')
    
    if session_id not in game_states:
        return jsonify({"error": "Game session not found"}), 404
    
    # Keep AI mode, reset everything else
    ai_mode = game_states[session_id]["ai_mode"]
    
    game_states[session_id] = {
        "board": [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)],
        "player_turn": True,
        "game_over": False,
        "winner": None,
        "ai_mode": ai_mode
    }
    
    return jsonify({
        "session_id": session_id,
        "board": game_states[session_id]["board"],
        "player_turn": True,
        "game_over": False,
        "winner": None,
        "ai_mode": ai_mode
    })

@app.route('/api/get_stats', methods=['GET'])
def get_stats():
    game_stats = load_game_stats()
    return jsonify(game_stats)

if __name__ == '__main__':
    app.run(debug=True)
