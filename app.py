from flask import Flask, render_template, jsonify, request, session, url_for
import random
import json
import os
import sys
import uuid

# กำหนดพาธสำหรับบันทึกสถิติ
STATISTICS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "statistics")

# ตรวจสอบว่าโฟลเดอร์มีอยู่หรือไม่ ถ้าไม่มีให้สร้างใหม่
if not os.path.exists(STATISTICS_PATH):
    os.makedirs(STATISTICS_PATH)

# Add the game directory to the Python path (for API routes)
current_dir = os.path.dirname(os.path.abspath(__file__))
game_dir = os.path.join(current_dir, "src", "PlantvsAi_zombitx64", "game")
sys.path.append(game_dir)

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tictactoe')
def tictactoe():
    ai = request.args.get('ai', '0')
    return render_template('tictactoe.html', ai_mode=ai)


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

@app.route('/api/change_ai_mode', methods=['POST'])
def change_ai_mode():
    """เปลี่ยนโหมด AI ผ่าน API"""
    data = request.get_json()
    if 'game' not in data or 'mode' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    game = data['game']
    mode = data['mode']
    
    # บันทึกโหมด AI ใหม่ใน session
    if 'ai_modes' not in session:
        session['ai_modes'] = {}
    session['ai_modes'][game] = mode
    
    return jsonify({'success': True, 'mode': mode})

@app.route('/api/get_ai_mode')
def get_ai_mode():
    """รับค่าโหมด AI ปัจจุบัน"""
    game = request.args.get('game')
    if not game:
        return jsonify({'error': 'Missing game parameter'}), 400
    
    mode = session.get('ai_modes', {}).get(game, '0')
    return jsonify({'mode': mode})

@app.route('/api/new_game', methods=['POST'])
def new_game():
    """เริ่มเกมใหม่"""
    data = request.get_json()
    game_type = data.get('game_type', 'TicTacToe')
    difficulty = data.get('difficulty', 0)
    
    # สร้าง game state ใหม่
    game_state = {
        'board': [['' for _ in range(3)] for _ in range(3)] if game_type == 'TicTacToe' else [],
        'current_player': 'X' if game_type == 'TicTacToe' else 'player',
        'status': 'active',
        'difficulty': difficulty
    }
    
    # บันทึกเกมใน session
    if 'games' not in session:
        session['games'] = {}
    session['games'][game_type] = game_state
    
    return jsonify({
        'success': True,
        'game_state': game_state
    })

@app.route('/api/make_move', methods=['POST'])
def make_move():
    """AI ทำการเดิน"""
    data = request.get_json()
    game_type = data.get('game_type', 'TicTacToe')
    board = data.get('board', [])
    difficulty = data.get('difficulty', 0)
    
    # ดำเนินการตามประเภทของเกม
    if game_type == 'TicTacToe':
        # TicTacToe AI logic
        # จำลองตรรกะอย่างง่าย (ในโปรดักชั่นจริงอาจใช้อัลกอริทึมที่ซับซ้อนกว่านี้)
        available_moves = []
        for i in range(3):
            for j in range(3):
                if not board[i][j]:
                    available_moves.append((i, j))
        
        if available_moves:
            # ใช้กลยุทธ์ที่แตกต่างกันตามระดับความยาก
            if difficulty == 0:  # ง่าย: สุ่ม
                move = random.choice(available_moves)
            elif difficulty == 1:  # กลาง: พยายามชนะหรือป้องกัน
                # จำลองตรรกะง่ายๆ สำหรับระดับกลาง
                move = random.choice(available_moves)
            else:  # ยาก: ใช้กลยุทธ์ที่ดีที่สุด
                # จำลองตรรกะง่ายๆ สำหรับระดับยาก
                move = random.choice(available_moves)
                
            row, col = move
            return jsonify({
                'success': True,
                'move': {'row': row, 'col': col}
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No available moves'
            })
    
    return jsonify({
        'success': False,
        'message': 'Unsupported game type'
    })

@app.route('/api/get_stats', methods=['GET'])
def get_stats():
    game_type = request.args.get('game_type')
    if not game_type:
        return jsonify({'error': 'Missing game_type parameter'}), 400
    
    # พาธไปยังไฟล์สถิติ
    stats_file = os.path.join(STATISTICS_PATH, f"{game_type.lower()}_stats.json")
    
    # ถ้าไม่มีไฟล์ ให้สร้างสถิติว่างเปล่า
    if not os.path.exists(stats_file):
        stats = {
            'total_games': 0,
            'player_wins': 0,
            'ai_wins': 0,
            'draws': 0,
            'win_rate': 0
        }
    else:
        # อ่านสถิติจากไฟล์
        try:
            with open(stats_file, 'r') as f:
                stats = json.load(f)
        except:
            stats = {
                'total_games': 0,
                'player_wins': 0,
                'ai_wins': 0,
                'draws': 0,
                'win_rate': 0
            }
    
    # คำนวณ win rate ใหม่เสมอ เพื่อให้แน่ใจว่าถูกต้อง
    total_games = stats.get('total_games', 0)
    player_wins = stats.get('player_wins', 0)
    
    # ป้องกันการหารด้วย 0
    win_rate = 0
    if total_games > 0:
        win_rate = round((player_wins / total_games) * 100)
    
    stats['win_rate'] = win_rate
    
    return jsonify(stats)

@app.route('/api/update_stats', methods=['POST'])
def update_stats():
    """อัปเดตสถิติของเกม"""
    data = request.get_json()
    game_type = data.get('game_type')
    result = data.get('result')  # 'player', 'ai', 'draw'
    
    if not game_type or not result:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # พาธไปยังไฟล์สถิติ
    stats_file = os.path.join(STATISTICS_PATH, f"{game_type.lower()}_stats.json")
    
    # อ่านสถิติปัจจุบัน
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r') as f:
                stats = json.load(f)
        except:
            stats = {
                'total_games': 0,
                'player_wins': 0,
                'ai_wins': 0,
                'draws': 0
            }
    else:
        stats = {
            'total_games': 0,
            'player_wins': 0,
            'ai_wins': 0,
            'draws': 0
        }
    
    # อัปเดตสถิติ
    stats['total_games'] += 1
    if result == 'player':
        stats['player_wins'] += 1
    elif result == 'ai':
        stats['ai_wins'] += 1
    else:  # draw
        stats['draws'] += 1
    
    # บันทึกสถิติลงไฟล์
    try:
        with open(stats_file, 'w') as f:
            json.dump(stats, f)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/checkers/valid_moves', methods=['POST'])
def checkers_valid_moves():
    """ดึงข้อมูลการเคลื่อนที่ที่ถูกต้องสำหรับหมากฮอส"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    row = data.get('row')
    col = data.get('col')
    
    # ดึงข้อมูลเกมจาก session
    game_data = session.get('checkers_game', {})
    board = game_data.get('board', [[0 for _ in range(8)] for _ in range(8)])
    is_player_turn = game_data.get('player_turn', True)
    
    # ใช้ฟังก์ชัน get_valid_moves ที่มีการตรวจสอบกฎการเดินที่ถูกต้อง
    valid_moves_list = get_valid_moves(board, row, col, is_player_turn)
    
    # แปลงรูปแบบข้อมูลให้ตรงกับที่ frontend ต้องการ
    valid_moves = {}
    for move_row, move_col in valid_moves_list:
        valid_moves[f"{move_row},{move_col}"] = {"row": move_row, "col": move_col}
    
    return jsonify({
        'valid_moves': valid_moves
    })

@app.route('/api/checkers/move', methods=['POST'])
def checkers_move():
    """ทำการเคลื่อนที่สำหรับเกมหมากฮอส"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # ดึงข้อมูลจาก request
    from_row = data.get('from_row')
    from_col = data.get('from_col')
    to_row = data.get('to_row')
    to_col = data.get('to_col')
    
    # ตรวจสอบว่ามีข้อมูลเกมในเซสชันหรือไม่
    if 'checkers_game' not in session:
        return jsonify({'error': 'No active game'}), 400
    
    # ดึงกระดานปัจจุบันจาก session
    game_data = session.get('checkers_game', {})
    board = game_data.get('board', [[0 for _ in range(8)] for _ in range(8)])
    
    # บันทึกค่าหมากเดิมก่อนเคลื่อนที่
    moved_piece = board[from_row][from_col]
    
    # อัปเดตกระดาน - ย้ายหมากจากตำแหน่งเดิมไปยังตำแหน่งใหม่
    board[to_row][to_col] = moved_piece
    board[from_row][from_col] = 0  # ตำแหน่งเดิมว่าง
    
    # ตรวจสอบการเลื่อนขั้นเป็นคิง
    if moved_piece == 1 and to_row == 0:  # หมากขาวถึงแถวบนสุด
        board[to_row][to_col] = 3  # เลื่อนขั้นเป็นคิงขาว
    elif moved_piece == 2 and to_row == 7:  # หมากดำถึงแถวล่างสุด
        board[to_row][to_col] = 4  # เลื่อนขั้นเป็นคิงดำ
    
    # ตรวจสอบว่ามีการกินหมากหรือไม่
    is_capture = False
    row_diff = abs(to_row - from_row)
    if row_diff > 1:
        middle_row = (from_row + to_row) // 2
        middle_col = (from_col + to_col) // 2
        if board[middle_row][middle_col] != 0:
            board[middle_row][middle_col] = 0
            is_capture = True
    
    # สลับเทิร์นผู้เล่น
    game_data['player_turn'] = not game_data['player_turn']
    
    # บันทึกกระดานและตรวจสอบสถานะเกม
    game_data['board'] = board
    game_over, winner = check_game_status(board, game_data['player_turn'])
    game_data['game_over'] = game_over
    game_data['winner'] = winner
    
    # บันทึกสถานะเกมลงในเซสชัน
    session['checkers_game'] = game_data
    
    # ส่งผลลัพธ์กลับ
    return jsonify({
        'board': board,
        'captured': is_capture,
        'game_over': game_over,
        'winner': winner,
        'player_turn': game_data['player_turn']
    })
@app.route('/api/checkers/new_game', methods=['POST'])
def checkers_new_game():
    """เริ่มเกมหมากฮอสใหม่"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    ai_mode = data.get('ai_mode', 1)  # ค่าเริ่มต้นระดับยาก = 1
    session_id = data.get('session_id', str(uuid.uuid4()))
    player_color = data.get('player_color', 'white')  # ค่าเริ่มต้นผู้เล่นเป็นขาว
    
    # สร้างกระดานเกม 8x8 (0 = ว่าง, 1 = ขาว, 2 = ดำ, 3 = ขาว(คิง), 4 = ดำ(คิง))
    board = [[0 for _ in range(8)] for _ in range(8)]
    
    # จัดวางหมากเริ่มต้นเพียง 2 แถวต่อฝั่ง (แทนที่จะเป็น 3 แถว)
    for row in range(8):
        for col in range(8):
            # เฉพาะช่องสีดำเท่านั้น (row+col เป็นเลขคี่)
            if (row + col) % 2 == 1:
                # หมากดำ (AI) อยู่ด้านบน 2 แถวแรก
                if row < 2:
                    board[row][col] = 2
                # หมากขาว (ผู้เล่น) อยู่ด้านล่าง 2 แถวสุดท้าย
                elif row > 5:
                    board[row][col] = 1
    
    # กำหนดว่าใครเริ่มก่อน
    player_turn = player_color == 'white'  # ถ้าผู้เล่นเป็นขาว ผู้เล่นเริ่มก่อน
    
    # บันทึกข้อมูลเกมลงใน session
    session['checkers_game'] = {
        'board': board,
        'ai_mode': ai_mode,
        'session_id': session_id,
        'player_color': player_color,
        'player_turn': player_turn,
        'game_over': False,
        'winner': None
    }
    
    return jsonify({
        'board': board,
        'player_turn': player_turn,
        'ai_mode': ai_mode,
        'session_id': session_id
    })

def get_valid_moves(board, row, col, is_player_turn):
    """
    Returns list of valid moves (row, col) for a piece at the given position
    """
    valid_moves = []
    
    # Determine which pieces belong to the current player
    player_color = session.get('checkers_game', {}).get('player_color', 'white')
    if is_player_turn:
        # Player's turn
        player_pieces = [1, 3] if player_color == 'white' else [2, 4]
    else:
        # AI's turn
        player_pieces = [2, 4] if player_color == 'white' else [1, 3]
    
    # Check if there's a piece at the position and if it belongs to the current player
    if board[row][col] == 0 or board[row][col] not in player_pieces:
        return []
    
    piece = board[row][col]
    is_king = piece in [3, 4]  # Kings can move in any direction
    
    # Determine movement direction
    directions = []
    if is_king or (piece in [1, 3] and player_color == 'white') or (piece in [2, 4] and player_color != 'white'):
        directions.append(-1)  # Can move up
    
    if is_king or (piece in [2, 4] and player_color == 'white') or (piece in [1, 3] and player_color != 'white'):
        directions.append(1)  # Can move down
    
    # Check for normal moves (1 step)
    for d_row in directions:
        for d_col in [-1, 1]:  # Can move diagonally left or right
            new_row = row + d_row
            new_col = col + d_col
            
            if 0 <= new_row < 8 and 0 <= new_col < 8 and board[new_row][new_col] == 0:
                valid_moves.append((new_row, new_col))
    
    # Check for capture moves (2 steps)
    for d_row in directions:
        for d_col in [-1, 1]:
            new_row = row + d_row * 2
            new_col = col + d_col * 2
            
            if 0 <= new_row < 8 and 0 <= new_col < 8 and board[new_row][new_col] == 0:
                middle_row = row + d_row
                middle_col = col + d_col
                
                if 0 <= middle_row < 8 and 0 <= middle_col < 8:
                    middle_piece = board[middle_row][middle_col]
                    if middle_piece != 0 and middle_piece not in player_pieces:
                        valid_moves.append((new_row, new_col))
    
    return valid_moves

def check_game_status(board, is_player_turn):
    """
    Check if the game is over and who the winner is
    Returns: (is_game_over, winner)
    """
    # Check if there are any pieces left for each player
    player_pieces = 0
    ai_pieces = 0
    
    player_color = session.get('checkers_game', {}).get('player_color', 'white')
    player_piece_values = [1, 3] if player_color == 'white' else [2, 4]
    ai_piece_values = [2, 4] if player_color == 'white' else [1, 3]
    
    for row in range(8):
        for col in range(8):
            if board[row][col] in player_piece_values:
                player_pieces += 1
            elif board[row][col] in ai_piece_values:
                ai_pieces += 1
    
    # If one player has no pieces, they lose the game
    if player_pieces == 0:
        return True, 'ai'  # Player has no pieces, so AI wins
    if ai_pieces == 0:
        return True, 'player'  # AI has no pieces, so Player wins
    
    # Check if the current player has any valid moves
    has_valid_moves = False
    
    for row in range(8):
        for col in range(8):
            piece_values = player_piece_values if is_player_turn else ai_piece_values
            if board[row][col] in piece_values:
                moves = get_valid_moves(board, row, col, is_player_turn)
                if moves:
                    has_valid_moves = True
                    break
        if has_valid_moves:
            break
    
    # If the current player has no valid moves, they lose
    if not has_valid_moves:
        return True, 'ai' if is_player_turn else 'player'
    
    # Game continues
    return False, None

@app.route('/api/checkers/ai_move', methods=['POST'])
def checkers_ai_move():
    """AI เลือกเดินหมากและตรวจสอบการแพ้ชนะ"""
    # ตรวจสอบว่ามีข้อมูลเกมในเซสชันหรือไม่
    if 'checkers_game' not in session:
        return jsonify({'error': 'No active game'}), 400
    
    # ดึงข้อมูลเกมจาก session
    game_data = session.get('checkers_game', {})
    board = game_data.get('board', [[0 for _ in range(8)] for _ in range(8)])
    player_turn = game_data.get('player_turn', True)
    
    # ตรวจสอบว่าเป็นตาของ AI หรือไม่
    if player_turn:
        return jsonify({'error': 'Not AI turn'}), 400
    
    # ตรวจสอบเงื่อนไขการจบเกม
    game_over, winner = check_game_status(board, False)  # False = AI turn
    if game_over:
        game_data['game_over'] = True
        game_data['winner'] = winner
        session['checkers_game'] = game_data
        return jsonify({
            'board': board,
            'game_over': True,
            'winner': winner,
            'player_turn': True  # กลับไปที่ผู้เล่นเพื่อให้เห็นผลการเล่น
        })
    
    # หาการเดินที่เป็นไปได้ทั้งหมดของ AI
    ai_moves = []  # เก็บ tuple ของ (from_pos, to_pos, is_capture)
    player_color = game_data.get('player_color', 'white')
    ai_pieces_values = [2, 4] if player_color == 'white' else [1, 3]
    
    # 1. หาหมากและการเดินที่เป็นไปได้ทั้งหมดของ AI
    for row in range(8):
        for col in range(8):
            if board[row][col] in ai_pieces_values:
                moves = get_valid_moves(board, row, col, False)  # False = AI turn
                for move in moves:
                    to_row, to_col = move
                    # ตรวจสอบว่าเป็นการกินหรือไม่
                    is_capture = abs(to_row - row) > 1
                    ai_moves.append(((row, col), (to_row, to_col), is_capture))
    
    # 2. ตรวจสอบว่ามีการเดินที่เป็นไปได้หรือไม่
    if not ai_moves:
        # ถ้าไม่มีการเดินที่เป็นไปได้ ผู้เล่นชนะ
        game_data['game_over'] = True
        game_data['winner'] = 'player'
        session['checkers_game'] = game_data
        return jsonify({
            'board': board,
            'game_over': True,
            'winner': 'player',
            'player_turn': True
        })

    # 3. เลือกการเดินที่ดีที่สุด (ให้ความสำคัญกับการกินก่อน)
    capture_moves = [move for move in ai_moves if move[2]]
    selected_move = None
    if capture_moves:  # ถ้ามีการเดินที่สามารถกินได้
        selected_move = random.choice(capture_moves)
    else:  # ถ้าไม่มีการเดินที่สามารถกินได้
        selected_move = random.choice(ai_moves)
    
    # 4. ทำการเคลื่อนที่
    (from_row, from_col), (to_row, to_col), is_capture = selected_move
    piece = board[from_row][from_col]
    
    # บันทึกการเคลื่อนที่
    board[to_row][to_col] = piece
    board[from_row][from_col] = 0
    
    # ถ้าเป็นการกิน ให้ลบหมากที่ถูกกิน
    if is_capture:
        middle_row = (from_row + to_row) // 2
        middle_col = (from_col + to_col) // 2
        board[middle_row][middle_col] = 0
    
    # ตรวจสอบการเลื่อนขั้นเป็นคิง
    if piece == 1 and to_row == 0:  # หมากขาวถึงแถวบนสุด
        board[to_row][to_col] = 3  # เลื่อนขั้นเป็นคิงขาว
    elif piece == 2 and to_row == 7:  # หมากดำถึงแถวล่างสุด
        board[to_row][to_col] = 4  # เลื่อนขั้นเป็นคิงดำ
    
    # 5. ตรวจสอบการแพ้ชนะหลังจากเดิน
    game_over, winner = check_game_status(board, False)  # False = after AI's turn
    
    # อัพเดตข้อมูลเกม
    game_data['board'] = board
    game_data['player_turn'] = True
    game_data['game_over'] = game_over
    game_data['winner'] = winner
    session['checkers_game'] = game_data
    
    return jsonify({
        'board': board,
        'move': True,
        'from_row': from_row,
        'from_col': from_col,
        'to_row': to_row,
        'to_col': to_col,
        'captured': is_capture,
        'game_over': game_over,
        'winner': winner,
        'player_turn': True
    })
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
