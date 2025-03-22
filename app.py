from flask import Flask, render_template, jsonify, request
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
from game.poker import PokerGame

app = Flask(__name__)

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

# เก็บข้อมูลเกมตาม session
game_sessions = {}

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

# Save pattern data
def save_pattern_data(player_patterns):
    try:
        with open('player_patterns.json', 'w') as f:
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
    game_type = request.args.get('game_type', 'TicTacToe')
    
    if game_type == 'TicTacToe':
        # Create a temporary game to get stats
        temp_game = TicTacToe()
        return jsonify(temp_game.stats)
    elif game_type == 'ConnectFour':
        # Create a temporary game to get stats
        temp_game = ConnectFour()
        return jsonify(temp_game.stats)
    elif game_type == 'Checkers':
        # Create a temporary game to get stats
        temp_game = Checkers()
        return jsonify(temp_game.stats)
    
    return jsonify({"error": "Unknown game type"}), 400

@app.route('/api/get_game_types', methods=['GET'])
def get_game_types():
    return jsonify({
        "game_types": GAME_TYPES,
        "ai_modes": AI_MODES
    })

@app.route('/api/poker_action', methods=['POST'])
def poker_action():
    data = request.json
    session_id = data.get('session_id')
    action = data.get('action')
    bet_amount = data.get('bet_amount', 0)
    
    if session_id not in game_sessions:
        return jsonify({'error': 'Invalid session ID'})
    
    game = game_sessions[session_id]
    
    # ตรวจสอบว่าเป็นเกม Poker หรือไม่
    if not isinstance(game, PokerGame):
        return jsonify({'error': 'Invalid game type'})
    
    # ดำเนินการตามแอคชั่นของผู้เล่น (fold, call, check, raise)
    game.player_action(action, bet_amount)
    
    # Return current game state
    return jsonify({
        'pot': game.pot,
        'current_bet': game.current_bet,
        'game_stage': game.game_stage,
        'community_cards': [card.to_dict() for card in game.community_cards],
        'players': [
            {
                'name': player.name,
                'chips': player.chips,
                'current_bet': player.current_bet,
                'is_folded': player.is_folded,
                'is_all_in': player.is_all_in,
                'hand': player.hand.to_dict() if player.name == 'Player' else []
            }
            for player in game.players
        ],
        'current_player': game.players[game.current_player_idx].name if game.current_player_idx < len(game.players) else None,
        'winner': game.winner
    })

@app.route('/api/get_stats', methods=['GET'])
def get_stats():
    game_type = request.args.get('game_type', 'TicTacToe')
    
    # ดึงสถิติตามประเภทเกม
    if game_type == 'TicTacToe':
        # สร้างเกม TicTacToe เพื่อเข้าถึงสถิติ
        temp_game = TicTacToe()
        stats = temp_game.stats
    elif game_type == 'ConnectFour':
        temp_game = ConnectFour()
        stats = temp_game.stats
    elif game_type == 'Checkers':
        temp_game = Checkers()
        stats = temp_game.stats
    elif game_type == 'Chess':
        temp_game = Chess()
        stats = temp_game.stats
    elif game_type == 'Poker':
        temp_game = PokerGame()
        stats = temp_game.stats
    else:
        return jsonify({'error': 'Invalid game type'})
    
    return jsonify(stats)

@app.route('/api/change_ai_mode', methods=['POST'])
def change_ai_mode():
    data = request.json
    session_id = data.get('session_id')
    ai_mode = data.get('ai_mode', 0)
    
    if session_id not in game_sessions:
        return jsonify({'error': 'Invalid session ID'})
    
    game = game_sessions[session_id]
    
    # อัปเดต AI mode
    # เนื่องจากแต่ละเกมอาจมีการเก็บ AI mode ต่างกัน เราจะต้องตรวจสอบประเภทเกม
    if hasattr(game, 'ai_mode'):
        game.ai_mode = ai_mode
    
    return jsonify({
        'ai_mode': ai_mode,
        'ai_name': AI_MODES[ai_mode] if 0 <= ai_mode < len(AI_MODES) else "Unknown"
    })

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
