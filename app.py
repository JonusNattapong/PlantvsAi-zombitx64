from flask import Flask, render_template, jsonify, request, session
import random
import json
import os
from algorithm.q_learning import QLearningAgent
from algorithm.pattern_recognition import PatternRecognitionAgent
from algorithm.neural_network import NeuralNetworkAgent
from algorithm.mcts import MCTS
from algorithm.genetic_algorithm import GeneticAlgorithm
from game.connect_four import ConnectFour
from game.checkers import Checkers
from game.tictactoe import TicTacToe
from game.chess import Chess
from game.poker import PokerGame, Card, Deck, PokerHand, PokerPlayer
import uuid
import sys

# กำหนดพาธสำหรับบันทึกสถิติ
STATISTICS_PATH = "D:/Zombitx64/Tictactoe-zombitx64/statistics"

# ตรวจสอบว่าโฟลเดอร์มีอยู่หรือไม่ ถ้าไม่มีให้สร้างใหม่
if not os.path.exists(STATISTICS_PATH):
    os.makedirs(STATISTICS_PATH)

# Add the DatasetPokerzombitx64 directory to the Python path
sys.path.append('DatasetPokerzombitx64')

# Import the ZomPokerX64 model
try:
    from DatasetPokerzombitx64.poker_ml.models.zompokerx64 import ZomPokerX64
    ML_MODEL_AVAILABLE = True
except ImportError:
    ML_MODEL_AVAILABLE = False
    print("Warning: ZomPokerX64 model not available. Using fallback AI.")

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Game state will be stored on the server side
game_states = {}

# AI modes
AI_MODES = ["Minimax", "Pattern Recognition", "Q-Learning", "Neural Network", "MCTS", "Genetic Algorithm"]

# Game types
GAME_TYPES = ["TicTacToe", "ConnectFour", "Checkers"]

# Initialize AI agents
q_learning_agent = QLearningAgent()
pattern_recognition_agent = PatternRecognitionAgent()
neural_network_agent = NeuralNetworkAgent()
mcts_agent = MCTS()
genetic_algorithm_agent = GeneticAlgorithm()

# Game instances storage
tictactoe_games = {}  # Store Tic Tac Toe game instances
connect_four_games = {}  # Store Connect Four game instances
checkers_games = {}  # Store Checkers game instances

# Dictionary เก็บเกมของผู้เล่น
games = {}

# Initialize the AI model if available
ai_model = None
if ML_MODEL_AVAILABLE:
    try:
        ai_model = ZomPokerX64(name="PokerAI", models_dir="DatasetPokerzombitx64/poker_ml/models")
        print("ZomPokerX64 AI model initialized successfully!")
    except Exception as e:
        print(f"Error initializing ZomPokerX64 model: {e}")
        ML_MODEL_AVAILABLE = False

# Load pattern data
def load_pattern_data():
    try:
        pattern_file = os.path.join(STATISTICS_PATH, 'player_patterns.json')
        if os.path.exists(pattern_file):
            with open(pattern_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading pattern data: {e}")
    
    # Default pattern data
    return {}

# Save pattern data
def save_pattern_data(player_patterns):
    try:
        pattern_file = os.path.join(STATISTICS_PATH, 'player_patterns.json')
        with open(pattern_file, 'w') as f:
            json.dump(player_patterns, f, indent=2)
    except Exception as e:
        print(f"Error saving pattern data: {e}")

# Record a move for pattern analysis (for TicTacToe)
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
        for row in range(3):  # Assuming 3x3 board for TicTacToe
            for col in range(3):
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
    """หน้าหลักของเว็บไซต์"""
    return render_template('index.html')

@app.route('/tictactoe')
def tictactoe():
    ai = request.args.get('ai', '0')
    return render_template('tictactoe.html', ai_mode=ai)

@app.route('/connect_four')
def connect_four():
    ai = request.args.get('ai', '0')
    return render_template('connect_four.html', ai_mode=ai)

@app.route('/checkers')
def checkers():
    ai = request.args.get('ai', '0')
    return render_template('checkers.html', ai_mode=ai)

@app.route('/poker')
def poker():
    """หน้าเกม Poker"""
    # สร้าง session ID ถ้ายังไม่มี
    if 'game_id' not in session:
        session['game_id'] = str(random.randint(10000, 99999))
    
    return render_template('poker.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    data = request.get_json()
    session_id = data.get('session_id', str(random.randint(10000, 99999)))
    ai_mode = data.get('ai_mode', 0)  # Default to Minimax
    game_type = data.get('game_type', 'TicTacToe')  # Default to Tic Tac Toe
    
    if game_type == 'TicTacToe':
        # Initialize Tic Tac Toe game
        tictactoe_games[session_id] = TicTacToe()
        game = tictactoe_games[session_id]
        
        # Store game state reference
        game_states[session_id] = {
            "board": game.board,
            "player_turn": True,
            "game_over": False,
            "winner": None,
            "ai_mode": ai_mode,
            "game_type": game_type
        }
        
        # Reset AI agents for new game
        q_learning_agent.reset_for_new_game()
        pattern_recognition_agent.reset_for_new_game()
        neural_network_agent.reset_for_new_game()
        
        return jsonify({
            "session_id": session_id,
            "board": game.board,
            "player_turn": True,
            "game_over": False,
            "winner": None,
            "ai_mode": ai_mode,
            "game_type": game_type
        })
    
    elif game_type == 'ConnectFour':
        # Initialize Connect Four game
        connect_four_games[session_id] = ConnectFour()
        game = connect_four_games[session_id]
        
        # Store game state reference
        game_states[session_id] = {
            "board": game.board,
            "player_turn": True,
            "game_over": False,
            "winner": None,
            "ai_mode": ai_mode,
            "game_type": game_type
        }
        
        return jsonify({
            "session_id": session_id,
            "board": game.board,
            "player_turn": True,
            "game_over": False,
            "winner": None,
            "ai_mode": ai_mode,
            "game_type": game_type,
            "rows": game.ROWS,
            "cols": game.COLS
        })
    
    elif game_type == 'Checkers':
        # Initialize Checkers game
        checkers_games[session_id] = Checkers()
        game = checkers_games[session_id]
        
        # Store game state reference
        game_states[session_id] = {
            "board": game.get_board_state(),
            "player_turn": True,
            "game_over": False,
            "winner": None,
            "ai_mode": ai_mode,
            "game_type": game_type
        }
        
        return jsonify({
            "session_id": session_id,
            "board": game.get_board_state(),
            "player_turn": True,
            "game_over": False,
            "winner": None,
            "ai_mode": ai_mode,
            "game_type": game_type,
            "rows": game.ROWS,
            "cols": game.COLS
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

@app.route('/api/get_valid_moves', methods=['POST'])
def get_valid_moves():
    data = request.get_json()
    session_id = data.get('session_id')
    row = data.get('row')
    col = data.get('col')
    
    if session_id not in game_states:
        return jsonify({"error": "Game session not found"}), 404
    
    game_state = game_states[session_id]
    game_type = game_state.get("game_type", "TicTacToe")
    
    if game_type == "Checkers":
        if session_id not in checkers_games:
            return jsonify({"error": "Checkers game not found"}), 404
        
        game = checkers_games[session_id]
        valid_moves = game.get_valid_moves(row, col)
        
        valid_moves_dict = {}
        for end_pos, captured in valid_moves.items():
            to_row, to_col = end_pos
            valid_moves_dict[f"{to_row},{to_col}"] = [f"{cap_row},{cap_col}" for cap_row, cap_col in captured]
        
        return jsonify({
            "valid_moves": valid_moves_dict
        })
    
    return jsonify({"error": "Game type does not support this operation"}), 400

@app.route('/api/make_move', methods=['POST'])
def make_move():
    data = request.get_json()
    session_id = data.get('session_id')
    
    if session_id not in game_states:
        return jsonify({"error": "Game session not found"}), 404
    
    game_state = game_states[session_id]
    game_type = game_state.get("game_type", "TicTacToe")
    
    if game_type == "TicTacToe":
        return make_move_tictactoe(data, session_id, game_state)
    elif game_type == "ConnectFour":
        return make_move_connect_four(data, session_id, game_state)
    elif game_type == "Checkers":
        return make_move_checkers(data, session_id, game_state)
    else:
        return jsonify({"error": "Unknown game type"}), 400

def make_move_tictactoe(data, session_id, game_state):
    """Handle move for Tic Tac Toe game"""
    row = data.get('row')
    col = data.get('col')
    
    if session_id not in tictactoe_games:
        return jsonify({"error": "Game session not found"}), 404
    
    game = tictactoe_games[session_id]
    board = game.board
    ai_mode = game_state["ai_mode"]
    
    # Make player's move
    success = game.make_move(row, col, 'O')
    
    if not success:
        return jsonify({"error": "Invalid move"}), 400
    
    # Record move for pattern analysis
    record_move(session_id, row, col, True)
    
    # Update game state from game instance
    game_state["board"] = game.board
    game_state["player_turn"] = game.player_turn
    game_state["game_over"] = game.game_over
    game_state["winner"] = game.winner
    
    # Check if game ended after player's move
    if game.game_over:
        if game.winner:
            game.update_stats(AI_MODES[ai_mode])
        
        return jsonify({
            "board": game.board,
            "player_turn": game.player_turn,
            "game_over": True,
            "winner": game.winner
        })
    
    # AI's turn - determine which AI algorithm to use
    if ai_mode == 0:  # Minimax (built into TicTacToe class)
        game.ai_move_minimax()
    elif ai_mode == 1:  # Pattern Recognition
        # Use pattern recognition logic here
        player_patterns = load_pattern_data()
        move = pattern_recognition_agent.choose_counter_move(game.board, session_id)
        if move:
            game.make_move(move[0], move[1], 'X')
    elif ai_mode == 2:  # Q-Learning
        move = q_learning_agent.choose_action(game.board)
        if move:
            game.make_move(move[0], move[1], 'X')
            q_learning_agent.record_move(game.board, move)
    elif ai_mode == 3:  # Neural Network
        move = neural_network_agent.choose_action(game.board)
        if move:
            game.make_move(move[0], move[1], 'X')
            neural_network_agent.record_move(game.board, move, 'X')
    elif ai_mode == 4:  # MCTS
        move = mcts_agent.choose_action(game.board)
        if move:
            game.make_move(move[0], move[1], 'X')
    elif ai_mode == 5:  # Genetic Algorithm
        move = genetic_algorithm_agent.choose_action(game.board)
        if move:
            game.make_move(move[0], move[1], 'X')
    
    # Update game state after AI move
    game_state["board"] = game.board
    game_state["player_turn"] = game.player_turn
    game_state["game_over"] = game.game_over
    game_state["winner"] = game.winner
    
    # Check if game ended after AI move
    if game.game_over:
        # Update stats and AI learning
        if game.winner:
            game.update_stats(AI_MODES[ai_mode])
        
        # Learning update for AI agents
        if game.winner == 'X':  # AI won
            if ai_mode == 2:  # Q-Learning
                q_learning_agent.learn_from_game(1.0)
            elif ai_mode == 3:  # Neural Network
                neural_network_agent.train_on_game(1)
        elif game.winner == 'O':  # Player won
            if ai_mode == 2:  # Q-Learning
                q_learning_agent.learn_from_game(-1.0)
            elif ai_mode == 3:  # Neural Network
                neural_network_agent.train_on_game(-1)
        else:  # Draw
            if ai_mode == 2:  # Q-Learning
                q_learning_agent.learn_from_game(0.1)
            elif ai_mode == 3:  # Neural Network
                neural_network_agent.train_on_game(0)
    
    return jsonify({
        "board": game.board,
        "player_turn": game.player_turn,
        "game_over": game.game_over,
        "winner": game.winner,
        "move": {"row": row, "col": col} if success else None
    })

def make_move_connect_four(data, session_id, game_state):
    """Handle move for Connect Four game"""
    col = data.get('col')
    
    if session_id not in connect_four_games:
        return jsonify({"error": "Game session not found"}), 404
    
    game = connect_four_games[session_id]
    
    # Check if game is already over
    if game.game_over:
        return jsonify({"error": "Game is already over"}), 400
    
    # Make player's move
    success = game.make_move(col, 'O')
    
    if not success:
        return jsonify({"error": "Invalid move"}), 400
    
    # Check if game ended after player's move
    if game.game_over:
        # Update game state
        game_state["board"] = game.board
        game_state["game_over"] = True
        game_state["winner"] = game.winner
        game_state["player_turn"] = False
        
        # Update stats
        game.update_stats(AI_MODES[game_state["ai_mode"]])
        
        return jsonify({
            "board": game.board,
            "player_turn": False,
            "game_over": True,
            "winner": game.winner
        })
    
    # Switch to AI turn
    game_state["player_turn"] = False
    
    # Make AI move
    ai_result = ai_move_connect_four(session_id)
    
    return jsonify(ai_result)

def make_move_checkers(data, session_id, game_state):
    """Handle move for Checkers game"""
    from_row = data.get('from_row')
    from_col = data.get('from_col')
    to_row = data.get('to_row')
    to_col = data.get('to_col')
    
    if session_id not in checkers_games:
        return jsonify({"error": "Checkers game not found"}), 404
    
    game = checkers_games[session_id]
    
    # Check if game is already over
    if game.game_over:
        return jsonify({"error": "Game is already over"}), 400
    
    # Make player's move
    success = game.make_move(from_row, from_col, to_row, to_col)
    
    if not success:
        return jsonify({"error": "Invalid move"}), 400
    
    # Update game state
    game_state["board"] = game.get_board_state()
    game_state["player_turn"] = game.player_turn
    game_state["game_over"] = game.game_over
    game_state["winner"] = game.winner
    
    # Check if game ended after player's move
    if game.game_over:
        game.update_stats(AI_MODES[game_state["ai_mode"]])
        
        return jsonify({
            "board": game.get_board_state(),
            "player_turn": game.player_turn,
            "game_over": True,
            "winner": game.winner
        })
    
    # If it's AI's turn, make the AI move
    if not game.player_turn:
        # AI move will be handled by a separate endpoint
        pass
    
    return jsonify({
        "board": game.get_board_state(),
        "player_turn": game.player_turn,
        "game_over": game.game_over,
        "winner": game.winner
    })

# AI move function for Connect Four
def ai_move_connect_four(session_id):
    if session_id not in connect_four_games:
        return {"error": "Game session not found"}
    
    game = connect_four_games[session_id]
    game_state = game_states[session_id]
    ai_mode = game_state["ai_mode"]
    
    # Get column based on AI mode
    if ai_mode == 0:  # Minimax (built into Connect Four class)
        col, _ = game.minimax(game.board, 4, float('-inf'), float('inf'), True)
    else:
        # For now, all other AI modes use the basic minimax in Connect Four
        col, _ = game.minimax(game.board, 4, float('-inf'), float('inf'), True)
    
    # Make AI move
    success = game.make_move(col, 'X')
    
    if not success:
        # If move failed, try another column
        valid_cols = game.get_valid_columns()
        if valid_cols:
            col = random.choice(valid_cols)
            game.make_move(col, 'X')
    
    # Update game state
    game_over = game.game_over
    winner = game.winner
    
    # Update game state in dictionary
    game_state["board"] = game.board
    game_state["player_turn"] = True
    game_state["game_over"] = game_over
    game_state["winner"] = winner
    
    # Update stats if game is over
    if game_over:
        game.update_stats(AI_MODES[ai_mode])
    
    return {
        "board": game.board,
        "player_turn": True,
        "game_over": game_over,
        "winner": winner,
        "move": {"col": col}
    }

@app.route('/api/ai_move', methods=['POST'])
def ai_move():
    data = request.get_json()
    session_id = data.get('session_id')
    game_type = data.get('game_type', 'TicTacToe')
    
    if session_id not in game_states:
        return jsonify({"error": "Game session not found"}), 404
    
    game_state = game_states[session_id]
    
    if game_type == 'Checkers':
        if session_id not in checkers_games:
            return jsonify({"error": "Checkers game not found"}), 404
        
        game = checkers_games[session_id]
        ai_mode = game_state["ai_mode"]
        
        # Make AI move
        game.ai_move_minimax()
        
        # Update game state
        game_state["board"] = game.get_board_state()
        game_state["player_turn"] = game.player_turn
        game_state["game_over"] = game.game_over
        game_state["winner"] = game.winner
        
        # Check if game ended after AI move
        if game.game_over:
            game.update_stats(AI_MODES[ai_mode])
        
        return jsonify({
            "board": game.get_board_state(),
            "player_turn": game.player_turn,
            "game_over": game.game_over,
            "winner": game.winner
        })
    
    return jsonify({"error": "Game type not supported"}), 400

@app.route('/api/reset_game', methods=['POST'])
def reset_game():
    data = request.get_json()
    session_id = data.get('session_id')
    
    if session_id not in game_states:
        return jsonify({"error": "Game session not found"}), 404
    
    # Keep AI mode and game type, reset everything else
    ai_mode = game_states[session_id]["ai_mode"]
    game_type = game_states[session_id].get("game_type", "TicTacToe")
    
    if game_type == "TicTacToe":
        if session_id in tictactoe_games:
            tictactoe_games[session_id].reset_game()
            game = tictactoe_games[session_id]
        else:
            tictactoe_games[session_id] = TicTacToe()
            game = tictactoe_games[session_id]
        
        game_states[session_id] = {
            "board": game.board,
            "player_turn": True,
            "game_over": False,
            "winner": None,
            "ai_mode": ai_mode,
            "game_type": game_type
        }
        
        # Reset AI agents
        q_learning_agent.reset_for_new_game()
        pattern_recognition_agent.reset_for_new_game()
        neural_network_agent.reset_for_new_game()
        
        return jsonify({
            "session_id": session_id,
            "board": game.board,
            "player_turn": True,
            "game_over": False,
            "winner": None,
            "ai_mode": ai_mode,
            "game_type": game_type
        })
    
    elif game_type == "ConnectFour":
        if session_id in connect_four_games:
            connect_four_games[session_id].reset_game()
            game = connect_four_games[session_id]
        else:
            connect_four_games[session_id] = ConnectFour()
            game = connect_four_games[session_id]
        
        game_states[session_id] = {
            "board": game.board,
            "player_turn": True,
            "game_over": False,
            "winner": None,
            "ai_mode": ai_mode,
            "game_type": game_type
        }
        
        return jsonify({
            "session_id": session_id,
            "board": game.board,
            "player_turn": True,
            "game_over": False,
            "winner": None,
            "ai_mode": ai_mode,
            "game_type": game_type,
            "rows": game.ROWS,
            "cols": game.COLS
        })
    
    elif game_type == "Checkers":
        if session_id in checkers_games:
            checkers_games[session_id].reset_game()
            game = checkers_games[session_id]
        else:
            checkers_games[session_id] = Checkers()
            game = checkers_games[session_id]
        
        game_states[session_id] = {
            "board": game.get_board_state(),
            "player_turn": True,
            "game_over": False,
            "winner": None,
            "ai_mode": ai_mode,
            "game_type": game_type
        }
        
        return jsonify({
            "session_id": session_id,
            "board": game.get_board_state(),
            "player_turn": True,
            "game_over": False,
            "winner": None,
            "ai_mode": ai_mode,
            "game_type": game_type,
            "rows": game.ROWS,
            "cols": game.COLS
        })

@app.route('/api/get_stats', methods=['GET'])
def get_stats():
    """ดึงสถิติเกมโป๊กเกอร์ที่มีอยู่แล้ว พร้อมจัดเก็บลงไฟล์ในโฟลเดอร์สถิติ"""
    session_id = session.get('session_id')
    if not session_id or session_id not in games:
        return jsonify({'status': 'error', 'message': 'No active game found'}), 404
    
    game = games[session_id]
    stats = game.get_stats()
    
    # บันทึกสถิติลงในไฟล์
    stats_file = os.path.join(STATISTICS_PATH, f"poker_stats_{session_id}.json")
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=4)
    
    return jsonify({'status': 'success', 'stats': stats})

@app.route('/api/get_game_types', methods=['GET'])
def get_game_types():
    return jsonify({
        "game_types": GAME_TYPES,
        "ai_modes": AI_MODES
    })

@app.route('/api/poker/start', methods=['POST'])
def start_game():
    """เริ่มเกมใหม่"""
    game_id = session.get('game_id')
    if not game_id:
        return jsonify({'error': 'Session not found'}), 400
    
    # รับข้อมูล AI level จาก request
    data = request.get_json()
    ai_level = data.get('ai_level', 1)
    
    # สร้างเกมใหม่
    game = PokerGame()
    game.setup_new_game()
    games[game_id] = game
    
    # ส่งข้อมูลเริ่มต้นกลับไปยังผู้เล่น
    return jsonify(get_game_state(game_id))

@app.route('/api/poker/state', methods=['GET'])
def get_game_state_route():
    """รับข้อมูลสถานะเกมปัจจุบัน"""
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    return jsonify(get_game_state(game_id))

@app.route('/api/player-action', methods=['POST'])
def player_action():
    data = request.json
    session_id = data.get('sessionId', session.get('session_id'))
    action = data.get('action')
    amount = data.get('amount', 0)
    
    if session_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[session_id]
    
    # Process player action
    if action == 'fold':
        game.players[0].fold()
    elif action == 'check':
        game.players[0].check()
    elif action == 'call':
        game.players[0].call(amount)
    elif action == 'raise':
        game.players[0].raise_bet(amount)
    
    # Check if it's AI's turn
    if game.current_player == 1 and not game.is_round_over():
        # Get the current game state
        current_game_state = get_game_state(session_id)
        
        # Use the ML model for AI decision
        ai_action = make_ai_decision(current_game_state)
        
        # Process AI action
        if ai_action == 'fold':
            game.players[1].fold()
        elif ai_action == 'check':
            game.players[1].check()
        elif ai_action == 'call':
            game.players[1].call(game.current_bet - game.players[1].current_bet)
        elif ai_action == 'raise':
            # For raise, we can use a simple rule to determine the amount
            min_raise = max(game.current_bet * 2, 20)
            max_raise = min(game.players[1].chips, min_raise * 3)
            raise_amount = random.randint(min_raise, max_raise)
            game.players[1].raise_bet(raise_amount)
    
    # Move to next stage if round is over
    if game.is_round_over():
        game.next_stage()
    
    return jsonify(get_game_state(session_id))

@app.route('/api/poker/new_hand', methods=['POST'])
def new_hand():
    """เริ่มเกมใหม่โดยใช้ชิปที่เหลืออยู่"""
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    
    # เก็บชิปปัจจุบันของผู้เล่น
    player_chips = game.players[0].chips
    ai_chips = game.players[1].chips
    
    # ถ้าผู้เล่นฝ่ายใดฝ่ายหนึ่งหมดชิป ให้เริ่มใหม่ด้วย 1000 ชิป
    if player_chips <= 0 or ai_chips <= 0:
        player_chips = 1000
        ai_chips = 1000
    
    # เริ่มเกมใหม่
    game.setup_new_game(player_chips, ai_chips)
    
    return jsonify(get_game_state(game_id))

@app.route('/api/poker/stats', methods=['GET'])
def get_stats():
    """รับข้อมูลสถิติเกม"""
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    return jsonify(game.stats)

def get_game_state(game_id):
    """แปลงข้อมูลสถานะเกมให้อยู่ในรูปแบบที่ส่งกลับไปยัง client ได้"""
    if game_id not in games:
        return {'error': 'Game not found'}
    
    game = games[game_id]
    state = game.get_game_state(show_ai_cards=game.winner is not None or game.game_stage == 'showdown')
    
    # แปลงข้อมูลไพ่ให้อยู่ในรูปแบบที่ JavaScript เข้าใจได้
    formatted_state = {
        'pot': state['pot'],
        'currentBet': state['current_bet'],
        'gameStage': state['game_stage'],
        'communityCards': [card for card in state['community_cards']],
        'players': [
            {
                'name': player['name'],
                'chips': player['chips'],
                'currentBet': player['current_bet'],
                'isFolded': player['is_folded'],
                'isAllIn': player['is_all_in'],
                'hand': player['hand'],
                'handName': player['hand_name'],
            }
            for player in state['players']
        ],
        'currentPlayer': state['current_player'],
        'winner': state['winner'],
        'handDescriptions': state['hand_descriptions'],
        'betHistory': state['bet_history'],
        'actionLog': state['action_log']
    }
    
    return formatted_state

def make_ai_decision(game_state):
    """
    Make AI decision using the ML model if available, otherwise use a simple rule-based approach
    """
    if ML_MODEL_AVAILABLE and ai_model:
        try:
            # Convert game_state to the format expected by the model
            model_state = {
                # Hand information
                'hand': game_state['players'][1]['hand'],
                'community_cards': game_state['communityCards'],
                
                # Game state information
                'pot_size': game_state['pot'],
                'bet_to_call': game_state['currentBet'] - game_state['players'][1]['currentBet'],
                'stack_size': game_state['players'][1]['chips'],
                'position': 'BTN' if game_state['currentPlayer'] == 'AI' else 'BB',
                'street': _convert_game_stage(game_state['gameStage']),
                
                # Additional information
                'available_actions': _get_available_actions(game_state),
                'current_bet': game_state['currentBet'],
                'player_bet': game_state['players'][1]['currentBet'],
                'opponent_chips': game_state['players'][0]['chips'],
                'opponent_bet': game_state['players'][0]['currentBet'],
                'is_all_in': game_state['players'][1]['isAllIn'],
                'is_folded': game_state['players'][1]['isFolded']
            }
            
            # Get action from the model
            action = ai_model.predict_action(model_state)
            print(f"AI model decided: {action}")
            return action
        except Exception as e:
            print(f"Error using ML model for AI decision: {e}")
            # Fall back to simple AI if there's an error
            return simple_ai_decision(game_state)
    else:
        # Use simple rule-based AI
        return simple_ai_decision(game_state)

def _convert_game_stage(game_stage):
    """
    Convert game stage from our format to the format expected by the model
    """
    stage_mapping = {
        'pre_flop': 'preflop',
        'flop': 'flop',
        'turn': 'turn',
        'river': 'river',
        'showdown': 'river'  # Treat showdown as river for decision making
    }
    return stage_mapping.get(game_stage, 'preflop')

def _get_available_actions(game_state):
    """
    Determine available actions based on game state
    """
    available_actions = ['fold']
    
    # If player can check (current bet equals player's bet)
    if game_state['currentBet'] <= game_state['players'][1]['currentBet']:
        available_actions.append('check')
    else:
        available_actions.append('call')
    
    # Can always raise unless AI is all-in or has less chips than the minimum raise
    if not game_state['players'][1]['isAllIn'] and game_state['players'][1]['chips'] > 0:
        available_actions.append('raise')
    
    return available_actions

def simple_ai_decision(game_state):
    """
    Simple rule-based AI decision making as a fallback.
    This function uses basic poker strategy rules based on:
    1. Hand strength
    2. Position
    3. Pot odds
    4. Game stage
    """
    ai_player = game_state['players'][1]
    player = game_state['players'][0]
    
    # Extract relevant information
    hand = ai_player['hand']
    community_cards = game_state['communityCards']
    pot = game_state['pot']
    current_bet = game_state['currentBet']
    ai_chips = ai_player['chips']
    player_chips = player['chips']
    game_stage = game_state['gameStage']
    current_player = game_state['currentPlayer']
    
    # Calculate how much AI needs to call
    call_amount = current_bet - ai_player['currentBet']
    
    # If AI is all-in or folded, no decision needed
    if ai_player['isAllIn'] or ai_player['isFolded']:
        return 'check'
        
    # Calculate basic hand strength (0-10 scale)
    hand_strength = calculate_hand_strength(hand, community_cards, game_stage)
    
    # Pre-flop strategy
    if game_stage == 'pre_flop':
        # Strong starting hand
        if hand_strength >= 7:
            if random.random() < 0.7:  # 70% chance to raise with strong hand
                return 'raise'
            else:
                return 'call'
        # Medium strength hand
        elif hand_strength >= 4:
            if call_amount <= ai_chips * 0.1:  # Call if less than 10% of stack
                return 'call'
            else:
                return 'fold'
        # Weak hand
        else:
            if call_amount == 0:  # Free to see flop
                return 'check'
            elif call_amount <= ai_chips * 0.05:  # Small bet, might call occasionally
                return 'call' if random.random() < 0.3 else 'fold'
            else:
                return 'fold'
    
    # Post-flop strategy
    else:
        # Strong hand
        if hand_strength >= 8:
            # Value bet/raise
            if random.random() < 0.8:
                return 'raise'
            else:
                return 'call'
        # Decent hand
        elif hand_strength >= 5:
            # Pot odds consideration - call if getting good odds
            pot_odds = call_amount / (pot + call_amount)
            win_probability = hand_strength / 10  # Simplified win probability
            
            if win_probability > pot_odds:
                return 'call'
            elif call_amount == 0:
                return random.choice(['check', 'raise'])  # Mix of checking and raising
            else:
                return 'fold'
        # Weak hand
        else:
            if call_amount == 0:
                return 'check'
            # Occasionally bluff
            elif random.random() < 0.2 and game_stage == 'river':
                return 'raise'
            else:
                return 'fold'

def calculate_hand_strength(hand, community_cards, game_stage):
    """
    Calculate a simplified hand strength on a scale of 0-10.
    
    Args:
        hand: List of player's hole cards
        community_cards: List of community cards
        game_stage: Current stage of the game
        
    Returns:
        float: Hand strength value between 0-10
    """
    # Check if we have valid cards
    if not hand or len(hand) < 2:
        return 0
    
    # Convert card representation if needed
    # This depends on your card representation format
    
    # Pre-flop hand strength based on common starting hands
    if game_stage == 'pre_flop':
        # Check for pairs
        if hand[0]['rank'] == hand[1]['rank']:
            rank_value = card_rank_to_value(hand[0]['rank'])
            # High pairs (AA, KK, QQ, JJ)
            if rank_value >= 11:
                return 9.0 + (rank_value - 11) / 3.0  # AA=10, KK=9.67, QQ=9.33, JJ=9
            # Medium pairs (TT through 77)
            elif rank_value >= 7:
                return 7.0 + (rank_value - 7) / 3.0
            # Low pairs
            else:
                return 5.0 + rank_value / 7.0
        
        # Check for suited cards
        elif hand[0]['suit'] == hand[1]['suit']:
            rank1 = card_rank_to_value(hand[0]['rank'])
            rank2 = card_rank_to_value(hand[1]['rank'])
            high_card = max(rank1, rank2)
            low_card = min(rank1, rank2)
            
            # Suited high cards
            if high_card >= 12 and low_card >= 10:  # AK, AQ, KQ suited
                return 8.0
            elif high_card >= 14 and low_card >= 8:  # AJ, AT, A9, KJ, KT suited
                return 7.0
            elif high_card >= 11:  # Other suited with face card
                return 6.0
            else:
                # Suited connectors
                if high_card - low_card == 1:
                    return 5.5
                # Suited one-gappers
                elif high_card - low_card == 2:
                    return 4.5
                # Other suited
                else:
                    return 4.0
        
        # Unsuited cards
        else:
            rank1 = card_rank_to_value(hand[0]['rank'])
            rank2 = card_rank_to_value(hand[1]['rank'])
            high_card = max(rank1, rank2)
            low_card = min(rank1, rank2)
            
            # High unsuited cards
            if high_card >= 14 and low_card >= 12:  # AK, AQ unsuited
                return 7.0
            elif high_card >= 14 and low_card >= 10:  # AJ, AT unsuited
                return 6.0
            elif high_card >= 13 and low_card >= 10:  # KQ, KJ, QJ unsuited
                return 5.5
            elif high_card >= 14:  # Ax unsuited
                return 3.0 + low_card / 7.0
            # Connectors
            elif high_card - low_card == 1 and high_card >= 9:
                return 4.0
            # Other trash hands
            else:
                return 2.0
    
    # Post-flop simplified evaluation
    else:
        # In a real implementation, you would evaluate the complete hand
        # including community cards to determine made hands and draws
        
        # This is a simplified placeholder that returns mid-range strength
        # In production, replace with proper hand evaluator
        return 5.0  # Placeholder - implement real evaluation logic

def card_rank_to_value(rank):
    """Convert card rank to numeric value"""
    if isinstance(rank, int) or rank.isdigit():
        return int(rank)
    
    if rank == 'A':
        return 14
    elif rank == 'K':
        return 13
    elif rank == 'Q':
        return 12
    elif rank == 'J':
        return 11
    elif rank == 'T':
        return 10
    else:
        # Default case
        return 2

@app.route('/api/stats/save', methods=['POST'])
def save_game_stats():
    """บันทึกสถิติเกม"""
    game_type = request.json.get('game_type')
    session_id = request.json.get('session_id')
    stats = request.json.get('stats', {})
    
    if not game_type or not session_id:
        return jsonify({'status': 'error', 'message': 'Missing game_type or session_id'}), 400
    
    # สร้างชื่อไฟล์ตามประเภทเกมและ session ID
    filename = f"{game_type}_stats_{session_id}.json"
    file_path = os.path.join(STATISTICS_PATH, filename)
    
    # บันทึกสถิติลงไฟล์
    with open(file_path, 'w') as f:
        json.dump(stats, f, indent=4)
    
    return jsonify({'status': 'success', 'message': f'Statistics for {game_type} saved successfully'})

@app.route('/api/stats/load', methods=['GET'])
def load_game_stats():
    """โหลดสถิติเกม"""
    game_type = request.args.get('game_type')
    session_id = request.args.get('session_id')
    
    if not game_type or not session_id:
        return jsonify({'status': 'error', 'message': 'Missing game_type or session_id'}), 400
    
    # สร้างชื่อไฟล์ตามประเภทเกมและ session ID
    filename = f"{game_type}_stats_{session_id}.json"
    file_path = os.path.join(STATISTICS_PATH, filename)
    
    # ตรวจสอบว่าไฟล์มีอยู่หรือไม่
    if not os.path.exists(file_path):
        return jsonify({'status': 'error', 'message': 'Statistics not found'}), 404
    
    # โหลดข้อมูลสถิติ
    try:
        with open(file_path, 'r') as f:
            stats = json.load(f)
        return jsonify({'status': 'success', 'stats': stats})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error loading statistics: {str(e)}'}), 500

@app.route('/api/stats/all', methods=['GET'])
def get_all_stats():
    """ดึงสถิติทั้งหมดของทุกเกม"""
    all_stats = {
        'tictactoe': [],
        'connect_four': [],
        'checkers': [],
        'chess': [],
        'poker': []
    }
    
    # อ่านและรวบรวมไฟล์สถิติทั้งหมด
    try:
        for filename in os.listdir(STATISTICS_PATH):
            if not filename.endswith('.json'):
                continue
            
            file_path = os.path.join(STATISTICS_PATH, filename)
            
            try:
                with open(file_path, 'r') as f:
                    stats = json.load(f)
                
                if filename.startswith('tictactoe_'):
                    all_stats['tictactoe'].append(stats)
                elif filename.startswith('connect_four_'):
                    all_stats['connect_four'].append(stats)
                elif filename.startswith('checkers_'):
                    all_stats['checkers'].append(stats)
                elif filename.startswith('chess_'):
                    all_stats['chess'].append(stats)
                elif filename.startswith('poker_'):
                    all_stats['poker'].append(stats)
            except Exception as e:
                print(f"Error loading stats file {filename}: {str(e)}")
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error reading statistics directory: {str(e)}'}), 500
    
    return jsonify({'status': 'success', 'stats': all_stats})

@app.route('/api/stats/summary', methods=['GET'])
def get_stats_summary():
    """สรุปสถิติโดยรวมของทุกเกม"""
    game_type = request.args.get('game_type')
    
    summary = {
        'total_games': 0,
        'player_wins': 0,
        'ai_wins': 0,
        'draws': 0,
        'ai_mode_stats': {}
    }
    
    try:
        pattern = f"{game_type}_stats_" if game_type else ""
        
        for filename in os.listdir(STATISTICS_PATH):
            if not filename.endswith('.json') or (pattern and not filename.startswith(pattern)):
                continue
            
            file_path = os.path.join(STATISTICS_PATH, filename)
            
            try:
                with open(file_path, 'r') as f:
                    stats = json.load(f)
                
                # สรุปข้อมูลตามรูปแบบของสถิติที่คาดว่าจะมี
                if 'result' in stats:
                    summary['total_games'] += 1
                    
                    if stats['result'] == 'win':
                        summary['player_wins'] += 1
                    elif stats['result'] == 'loss':
                        summary['ai_wins'] += 1
                    elif stats['result'] == 'draw':
                        summary['draws'] += 1
                
                # บันทึกสถิติตามโหมด AI
                if 'ai_mode' in stats:
                    ai_mode = stats['ai_mode']
                    if ai_mode not in summary['ai_mode_stats']:
                        summary['ai_mode_stats'][ai_mode] = {
                            'wins': 0,
                            'losses': 0,
                            'draws': 0
                        }
                    
                    if stats.get('result') == 'win':
                        summary['ai_mode_stats'][ai_mode]['losses'] += 1
                    elif stats.get('result') == 'loss':
                        summary['ai_mode_stats'][ai_mode]['wins'] += 1
                    elif stats.get('result') == 'draw':
                        summary['ai_mode_stats'][ai_mode]['draws'] += 1
            except Exception as e:
                print(f"Error processing stats file {filename}: {str(e)}")
        
        # คำนวณอัตราชนะ
        if summary['total_games'] > 0:
            summary['win_rate'] = (summary['player_wins'] / summary['total_games']) * 100
        
        # บันทึกข้อมูลสรุปลงไฟล์
        summary_file = os.path.join(STATISTICS_PATH, f"{'game_stats' if not game_type else game_type + '_summary'}.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return jsonify({'status': 'success', 'summary': summary})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error generating statistics summary: {str(e)}'}), 500

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
