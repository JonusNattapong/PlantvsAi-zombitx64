import pygame
import sys
import random
import time
import json
import os
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Constants
BASE_WIDTH, BASE_HEIGHT = 800, 700  # Base dimensions
WIDTH, HEIGHT = BASE_WIDTH, BASE_HEIGHT  # Actual dimensions (will be adjusted for responsive design)
LINE_WIDTH = 15
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = 200  # Base size (will be adjusted)
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# Colors
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (50, 50, 50)
BUTTON_HOVER_COLOR = (70, 70, 70)
BUTTON_TEXT_COLOR = (255, 255, 255)
STATS_BG_COLOR = (40, 40, 40)
WELCOME_BG_COLOR = (20, 130, 120)

# Get screen info for responsive design
screen_info = pygame.display.Info()
screen_width, screen_height = screen_info.current_w, screen_info.current_h

# Calculate scale factor based on screen size
scale_w = min(1.0, screen_width / BASE_WIDTH * 0.9)
scale_h = min(1.0, screen_height / BASE_HEIGHT * 0.9)
scale = min(scale_w, scale_h)

# Adjust dimensions
WIDTH = int(BASE_WIDTH * scale)
HEIGHT = int(BASE_HEIGHT * scale)
SQUARE_SIZE = int(200 * scale)
LINE_WIDTH = max(1, int(15 * scale))
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = max(1, int(15 * scale))
CROSS_WIDTH = max(1, int(25 * scale))
SPACE = SQUARE_SIZE // 4

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tic Tac Toe with AI')
screen.fill(BG_COLOR)

# Font sizes based on scale
font_size_small = max(10, int(18 * scale))
font_size_medium = max(12, int(24 * scale))
font_size_large = max(18, int(40 * scale))

# Load fonts
pygame.font.init()
FONT = pygame.font.SysFont('Arial', font_size_medium)
LARGE_FONT = pygame.font.SysFont('Arial', font_size_large)
SMALL_FONT = pygame.font.SysFont('Arial', font_size_small)

# Game state
in_welcome_screen = True
in_game = False
board = [[None for x in range(BOARD_COLS)] for y in range(BOARD_ROWS)]
game_over = False
player_turn = True  # True for player, False for AI
winner = None

# AI setup
ai_modes = ["Minimax", "Pattern Recognition"]
current_ai_mode = 0  # Default to Minimax

# Pattern recognition data structure
player_patterns = {}
player_id = "default_player"
current_game_moves = []

# Game statistics
game_stats = {
    "total_games": 0,
    "player_wins": 0,
    "ai_wins": 0,
    "draws": 0,
    "ai_mode_stats": {mode: {"wins": 0, "losses": 0, "draws": 0} for mode in ai_modes}
}

# Load game stats if exists
if os.path.exists('game_stats.json'):
    try:
        with open('game_stats.json', 'r') as f:
            game_stats = json.load(f)
    except:
        print("Error loading game stats, starting fresh")

# Load pattern data if exists
if os.path.exists('player_patterns.json'):
    try:
        with open('player_patterns.json', 'r') as f:
            player_patterns = json.load(f)
    except:
        print("Error loading pattern data, starting fresh")

def save_game_stats():
    """Save game statistics to file"""
    with open('game_stats.json', 'w') as f:
        json.dump(game_stats, f, indent=2)

def save_pattern_data():
    """Save pattern data to file"""
    with open('player_patterns.json', 'w') as f:
        json.dump(player_patterns, f, indent=2)

def draw_welcome_screen():
    """Draw the welcome screen with start button"""
    screen.fill(WELCOME_BG_COLOR)
    
    # Draw title
    title = LARGE_FONT.render("TIC TAC TOE", True, TEXT_COLOR)
    subtitle = FONT.render("with Advanced AI", True, TEXT_COLOR)
    
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 4 + title.get_height() + 10))
    
    # Draw start button
    button_width = WIDTH // 2
    button_height = int(50 * scale)
    button_x = WIDTH // 2 - button_width // 2
    button_y = HEIGHT // 2
    
    pygame.draw.rect(screen, BUTTON_COLOR, (button_x, button_y, button_width, button_height))
    pygame.draw.rect(screen, LINE_COLOR, (button_x, button_y, button_width, button_height), 2)
    
    start_text = FONT.render("START GAME", True, BUTTON_TEXT_COLOR)
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 
                            button_y + button_height // 2 - start_text.get_height() // 2))
    
    # Draw AI mode selector
    draw_welcome_ai_selector()
    
    # Draw instructions
    instructions = [
        "How to Play:",
        "- Click on a square to place your 'O'",
        "- Beat the AI by getting three in a row",
        "- Select AI mode below",
        "- Press 'R' to restart at any time"
    ]
    
    y_pos = HEIGHT * 2 // 3
    for instruction in instructions:
        text = SMALL_FONT.render(instruction, True, TEXT_COLOR)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_pos))
        y_pos += text.get_height() + 5

def draw_welcome_ai_selector():
    """Draw buttons to select AI mode on welcome screen"""
    text = FONT.render("Select AI Mode:", True, TEXT_COLOR)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + int(70 * scale)))
    
    button_width = WIDTH // len(ai_modes) - int(30 * scale)
    button_height = int(40 * scale)
    y_pos = HEIGHT // 2 + int(110 * scale)
    
    for i, mode in enumerate(ai_modes):
        x_pos = i * (button_width + int(30 * scale)) + WIDTH // 2 - (button_width * len(ai_modes) + int(30 * scale) * (len(ai_modes) - 1)) // 2
        
        # Draw button
        color = BUTTON_HOVER_COLOR if i == current_ai_mode else BUTTON_COLOR
        pygame.draw.rect(screen, color, (x_pos, y_pos, button_width, button_height))
        pygame.draw.rect(screen, LINE_COLOR, (x_pos, y_pos, button_width, button_height), 1)
        
        # Draw button text
        text = SMALL_FONT.render(mode, True, BUTTON_TEXT_COLOR)
        screen.blit(text, (x_pos + button_width // 2 - text.get_width() // 2, 
                          y_pos + button_height // 2 - text.get_height() // 2))

def handle_welcome_click(pos):
    """Handle clicks on welcome screen"""
    global in_welcome_screen, in_game, current_ai_mode
    
    # Check if clicked on start button
    button_width = WIDTH // 2
    button_height = int(50 * scale)
    button_x = WIDTH // 2 - button_width // 2
    button_y = HEIGHT // 2
    
    if (button_x <= pos[0] <= button_x + button_width and
        button_y <= pos[1] <= button_y + button_height):
        in_welcome_screen = False
        in_game = True
        start_game()
        return True
    
    # Check if clicked on AI mode selector
    button_width = WIDTH // len(ai_modes) - int(30 * scale)
    button_height = int(40 * scale)
    y_pos = HEIGHT // 2 + int(110 * scale)
    
    if y_pos <= pos[1] <= y_pos + button_height:
        for i in range(len(ai_modes)):
            x_pos = i * (button_width + int(30 * scale)) + WIDTH // 2 - (button_width * len(ai_modes) + int(30 * scale) * (len(ai_modes) - 1)) // 2
            if x_pos <= pos[0] <= x_pos + button_width:
                current_ai_mode = i
                # Redraw the welcome screen to show selection
                draw_welcome_screen()
                return True
    
    return False

def start_game():
    """Initialize and start a new game"""
    global board, game_over, player_turn, winner, current_game_moves
    screen.fill(BG_COLOR)
    draw_lines()
    draw_stats_panel()
    draw_ai_selector()
    board = [[None for x in range(BOARD_COLS)] for y in range(BOARD_ROWS)]
    game_over = False
    player_turn = True
    winner = None
    current_game_moves = []

def draw_lines():
    # Horizontal lines
    pygame.draw.line(screen, LINE_COLOR, (0, SQUARE_SIZE), (SQUARE_SIZE * 3, SQUARE_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (SQUARE_SIZE * 3, 2 * SQUARE_SIZE), LINE_WIDTH)
    
    # Vertical lines
    pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, SQUARE_SIZE * 3), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, SQUARE_SIZE * 3), LINE_WIDTH)

def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 'O':
                pygame.draw.circle(
                    screen, 
                    CIRCLE_COLOR, 
                    (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 
                    CIRCLE_RADIUS, 
                    CIRCLE_WIDTH
                )
            elif board[row][col] == 'X':
                # Drawing X
                pygame.draw.line(
                    screen, 
                    CROSS_COLOR, 
                    (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                    (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE),
                    CROSS_WIDTH
                )
                pygame.draw.line(
                    screen, 
                    CROSS_COLOR, 
                    (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE),
                    (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                    CROSS_WIDTH
                )

def mark_square(row, col, player):
    if board[row][col] is None:
        board[row][col] = player
        return True
    return False

def is_board_full():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] is None:
                return False
    return True

def check_win():
    # Check rows
    for row in range(BOARD_ROWS):
        if board[row][0] == board[row][1] == board[row][2] and board[row][0] is not None:
            return board[row][0]
    
    # Check columns
    for col in range(BOARD_COLS):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] is not None:
            return board[0][col]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    
    if board[2][0] == board[1][1] == board[0][2] and board[2][0] is not None:
        return board[2][0]
    
    return None

def reset_game():
    global board, game_over, player_turn, winner, current_game_moves
    screen.fill(BG_COLOR)
    draw_lines()
    draw_stats_panel()
    draw_ai_selector()
    board = [[None for x in range(BOARD_COLS)] for y in range(BOARD_ROWS)]
    game_over = False
    player_turn = True
    winner = None
    current_game_moves = []

def minimax(board, depth, is_maximizing):
    # Check terminal states
    result = check_win()
    if result == 'X':  # AI
        return 10 - depth
    if result == 'O':  # Player
        return depth - 10
    if is_board_full():
        return 0
    
    if is_maximizing:
        best_score = -float('inf')
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

def best_move_minimax():
    best_score = -float('inf')
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

def board_to_string(board):
    """Convert board to string representation"""
    result = ""
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] is None:
                result += "_"
            else:
                result += board[row][col]
    return result

def record_player_move(row, col):
    """Record player move for pattern recognition"""
    global current_game_moves
    board_str = board_to_string(board)
    current_game_moves.append({
        "board": board_str,
        "move": f"{row},{col}",
        "player": player_id,
        "mark": "O"
    })

def record_ai_move(row, col):
    """Record AI move for pattern recognition"""
    global current_game_moves
    board_str = board_to_string(board)
    current_game_moves.append({
        "board": board_str,
        "move": f"{row},{col}",
        "player": "AI",
        "mark": "X"
    })

def analyze_game_patterns():
    """Analyze player patterns after game is over"""
    global player_patterns
    
    if player_id not in player_patterns:
        player_patterns[player_id] = {
            "games_played": 0,
            "win_rate": 0,
            "draw_rate": 0,
            "loss_rate": 0,
            "board_patterns": {},
            "first_moves": {},
            "favorite_moves": {}
        }
    
    # Update games played
    player_patterns[player_id]["games_played"] += 1
    
    # Update win/loss/draw rates
    games_played = player_patterns[player_id]["games_played"]
    
    if winner == 'O':  # Player won
        player_patterns[player_id]["win_rate"] = (
            (player_patterns[player_id]["win_rate"] * (games_played - 1) + 1) / games_played
        )
    elif winner == 'X':  # AI won
        player_patterns[player_id]["loss_rate"] = (
            (player_patterns[player_id]["loss_rate"] * (games_played - 1) + 1) / games_played
        )
    else:  # Draw
        player_patterns[player_id]["draw_rate"] = (
            (player_patterns[player_id]["draw_rate"] * (games_played - 1) + 1) / games_played
        )
    
    # Record board patterns and moves
    for move_data in current_game_moves:
        if move_data["player"] == player_id:
            board_pattern = move_data["board"]
            move_str = move_data["move"]
            
            # Record board pattern
            if board_pattern not in player_patterns[player_id]["board_patterns"]:
                player_patterns[player_id]["board_patterns"][board_pattern] = {}
            
            if move_str not in player_patterns[player_id]["board_patterns"][board_pattern]:
                player_patterns[player_id]["board_patterns"][board_pattern][move_str] = 0
            
            player_patterns[player_id]["board_patterns"][board_pattern][move_str] += 1
            
            # Record favorite moves
            if move_str not in player_patterns[player_id]["favorite_moves"]:
                player_patterns[player_id]["favorite_moves"][move_str] = 0
            
            player_patterns[player_id]["favorite_moves"][move_str] += 1
            
            # Record first move if this is the first move of the game
            if len(current_game_moves) <= 2:  # First move by each player
                if move_data["mark"] == 'O':  # Player goes first
                    if move_str not in player_patterns[player_id]["first_moves"]:
                        player_patterns[player_id]["first_moves"][move_str] = 0
                    
                    player_patterns[player_id]["first_moves"][move_str] += 1
    
    # Save patterns to file
    save_pattern_data()

def predict_player_move():
    """Predict player's next move based on current board"""
    if player_id not in player_patterns:
        return None
    
    current_board = board_to_string(board)
    
    # Check if we've seen this board pattern before
    if current_board in player_patterns[player_id]["board_patterns"]:
        patterns = player_patterns[player_id]["board_patterns"][current_board]
        
        if patterns:
            # Find most common move for this pattern
            best_move = max(patterns.items(), key=lambda x: x[1])[0]
            row, col = map(int, best_move.split(','))
            return (row, col)
    
    # If no pattern match, check favorite moves
    if player_patterns[player_id]["favorite_moves"]:
        favorite_moves = player_patterns[player_id]["favorite_moves"]
        valid_moves = []
        
        for move_str, count in favorite_moves.items():
            row, col = map(int, move_str.split(','))
            if row < 3 and col < 3 and board[row][col] is None:
                valid_moves.append((move_str, count))
        
        if valid_moves:
            # Return the most common valid favorite move
            best_move = max(valid_moves, key=lambda x: x[1])[0]
            row, col = map(int, best_move.split(','))
            return (row, col)
    
    # If no patterns or favorites, return None for fallback strategy
    return None

def pattern_recognition_move():
    """Choose move based on pattern recognition"""
    # Try to predict player's next move
    predicted_move = predict_player_move()
    
    if predicted_move:
        row, col = predicted_move
        
        # Check if this would be a winning move for player
        temp_board = [row[:] for row in board]
        temp_board[row][col] = 'O'
        
        if check_win_for_board(temp_board) == 'O':
            # Block this winning move
            return row, col
    
    # Check for AI winning move
    for r in range(BOARD_ROWS):
        for c in range(BOARD_COLS):
            if board[r][c] is None:
                # Try this move
                temp_board = [row[:] for row in board]
                temp_board[r][c] = 'X'
                
                if check_win_for_board(temp_board) == 'X':
                    # This is a winning move
                    return r, c
    
    # Take center if available
    if board[1][1] is None:
        return 1, 1
    
    # Take corner if available
    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    available_corners = [corner for corner in corners if board[corner[0]][corner[1]] is None]
    if available_corners:
        return random.choice(available_corners)
    
    # Take any available edge
    edges = [(0, 1), (1, 0), (1, 2), (2, 1)]
    available_edges = [edge for edge in edges if board[edge[0]][edge[1]] is None]
    if available_edges:
        return random.choice(available_edges)
    
    # Fallback to minimax
    return best_move_minimax()

def check_win_for_board(board):
    """Check win condition for a given board"""
    # Check rows
    for row in range(BOARD_ROWS):
        if board[row][0] == board[row][1] == board[row][2] and board[row][0] is not None:
            return board[row][0]
    
    # Check columns
    for col in range(BOARD_COLS):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] is not None:
            return board[0][col]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    
    if board[2][0] == board[1][1] == board[0][2] and board[2][0] is not None:
        return board[2][0]
    
    return None

def ai_move():
    global player_turn, game_over, winner, game_stats
    
    if not game_over and not player_turn:
        # Choose move based on current AI mode
        if current_ai_mode == 0:  # Minimax
            row, col = best_move_minimax()
        else:  # Pattern Recognition
            row, col = pattern_recognition_move()
        
        # Record AI move
        record_ai_move(row, col)
        
        # Make the move
        if mark_square(row, col, 'X'):
            winner = check_win()
            if winner or is_board_full():
                game_over = True
                update_game_stats()
                analyze_game_patterns()
            player_turn = True

def update_game_stats():
    """Update game statistics based on game outcome"""
    global game_stats
    
    game_stats["total_games"] += 1
    current_mode = ai_modes[current_ai_mode]
    
    if winner == 'O':  # Player wins
        game_stats["player_wins"] += 1
        game_stats["ai_mode_stats"][current_mode]["losses"] += 1
    elif winner == 'X':  # AI wins
        game_stats["ai_wins"] += 1
        game_stats["ai_mode_stats"][current_mode]["wins"] += 1
    else:  # Draw
        game_stats["draws"] += 1
        game_stats["ai_mode_stats"][current_mode]["draws"] += 1
    
    save_game_stats()

def draw_stats_panel():
    """Draw the statistics panel at the bottom of the screen"""
    # Background for stats panel
    pygame.draw.rect(screen, STATS_BG_COLOR, (0, 3 * SQUARE_SIZE, WIDTH, HEIGHT - 3 * SQUARE_SIZE))
    
    # Title
    title = LARGE_FONT.render("Game Statistics", True, TEXT_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 3 * SQUARE_SIZE + 10))
    
    # Game stats
    y_pos = 3 * SQUARE_SIZE + 60
    stats_texts = [
        f"Total Games: {game_stats['total_games']}",
        f"Player Wins: {game_stats['player_wins']} ({game_stats['player_wins'] / max(1, game_stats['total_games']) * 100:.1f}%)",
        f"AI Wins: {game_stats['ai_wins']} ({game_stats['ai_wins'] / max(1, game_stats['total_games']) * 100:.1f}%)",
        f"Draws: {game_stats['draws']} ({game_stats['draws'] / max(1, game_stats['total_games']) * 100:.1f}%)",
        f"Current AI: {ai_modes[current_ai_mode]}"
    ]
    
    for text in stats_texts:
        rendered_text = FONT.render(text, True, TEXT_COLOR)
        screen.blit(rendered_text, (WIDTH // 4 - rendered_text.get_width() // 2, y_pos))
        y_pos += 30
    
    # AI-specific stats
    y_pos = 3 * SQUARE_SIZE + 60
    current_mode = ai_modes[current_ai_mode]
    
    if current_ai_mode == 1:  # Pattern Recognition
        # Make sure the current AI mode stats exist in the dictionary
        if current_mode not in game_stats["ai_mode_stats"]:
            game_stats["ai_mode_stats"][current_mode] = {"wins": 0, "losses": 0, "draws": 0}
            
        mode_stats = game_stats["ai_mode_stats"][current_mode]
        total_mode_games = mode_stats["wins"] + mode_stats["losses"] + mode_stats["draws"]
        
        if player_id in player_patterns:
            pattern_stats = player_patterns[player_id]
            ai_stats_texts = [
                f"Mode Games: {total_mode_games}",
                f"Player Wins: {mode_stats['losses']}",
                f"AI Wins: {mode_stats['wins']}",
                f"Patterns: {len(pattern_stats['board_patterns'])}"
            ]
        else:
            ai_stats_texts = [
                f"Mode Games: {total_mode_games}",
                f"Player Wins: {mode_stats['losses']}",
                f"AI Wins: {mode_stats['wins']}",
                f"No pattern data yet"
            ]
    else:  # Minimax
        # Make sure the current AI mode stats exist in the dictionary
        if current_mode not in game_stats["ai_mode_stats"]:
            game_stats["ai_mode_stats"][current_mode] = {"wins": 0, "losses": 0, "draws": 0}
            
        mode_stats = game_stats["ai_mode_stats"][current_mode]
        total = mode_stats["wins"] + mode_stats["losses"] + mode_stats["draws"]
        
        ai_stats_texts = [
            f"Mode Games: {total}",
            f"Player Wins: {mode_stats['losses']}",
            f"AI Wins: {mode_stats['wins']}",
            f"Draws: {mode_stats['draws']}"
        ]
    
    for text in ai_stats_texts:
        rendered_text = FONT.render(text, True, TEXT_COLOR)
        screen.blit(rendered_text, (WIDTH * 3 // 4 - rendered_text.get_width() // 2, y_pos))
        y_pos += 30

def draw_ai_selector():
    """Draw buttons to select AI mode"""
    button_width = WIDTH // len(ai_modes) - 10
    button_height = 40
    y_pos = HEIGHT - 50
    
    for i, mode in enumerate(ai_modes):
        x_pos = i * (button_width + 10) + 5
        
        # Draw button
        color = BUTTON_HOVER_COLOR if i == current_ai_mode else BUTTON_COLOR
        pygame.draw.rect(screen, color, (x_pos, y_pos, button_width, button_height))
        
        # Draw button text
        text = SMALL_FONT.render(mode, True, BUTTON_TEXT_COLOR)
        screen.blit(text, (x_pos + button_width // 2 - text.get_width() // 2, 
                          y_pos + button_height // 2 - text.get_height() // 2))

def handle_button_click(pos):
    """Handle clicks on AI selector buttons"""
    global current_ai_mode
    
    button_width = WIDTH // len(ai_modes) - 10
    button_height = 40
    y_pos = HEIGHT - 50
    
    if y_pos <= pos[1] <= y_pos + button_height:
        for i in range(len(ai_modes)):
            x_pos = i * (button_width + 10) + 5
            if x_pos <= pos[0] <= x_pos + button_width:
                current_ai_mode = i
                # Redraw the buttons to show selection
                draw_stats_panel()
                draw_ai_selector()
                return True
    
    return False

# Main game loop
draw_welcome_screen()  # Start with welcome screen

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Save game stats before quitting
            save_game_stats()
            save_pattern_data()
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseX, mouseY = event.pos
            
            if in_welcome_screen:
                handle_welcome_click((mouseX, mouseY))
            elif in_game:
                # Check if clicked on AI selector buttons
                if handle_button_click((mouseX, mouseY)):
                    continue
                
                # Handle game board clicks
                if not game_over and player_turn and mouseY < 3 * SQUARE_SIZE:
                    clicked_row = mouseY // SQUARE_SIZE
                    clicked_col = mouseX // SQUARE_SIZE
                    
                    if clicked_row < 3 and clicked_col < 3:  # Ensure click is within board
                        if mark_square(clicked_row, clicked_col, 'O'):
                            # Record player move
                            record_player_move(clicked_row, clicked_col)
                            
                            winner = check_win()
                            if winner or is_board_full():
                                game_over = True
                                update_game_stats()
                                analyze_game_patterns()
                            player_turn = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                if in_game:
                    reset_game()
                else:
                    in_welcome_screen = True
                    in_game = False
                    draw_welcome_screen()
            
            # Return to welcome screen with ESCAPE key
            if event.key == pygame.K_ESCAPE:
                in_welcome_screen = True
                in_game = False
                draw_welcome_screen()
    
    # AI's turn
    if in_game and not game_over and not player_turn:
        # Add a small delay to make AI move visible
        pygame.display.update()
        time.sleep(0.5)
        ai_move()
    
    if in_game:
        draw_figures()
        
        # Display game over or winner message
        if game_over:
            # Semi-transparent overlay
            s = pygame.Surface((WIDTH, 3 * SQUARE_SIZE), pygame.SRCALPHA)
            s.fill((0, 0, 0, 128))
            screen.blit(s, (0, 0))
            
            if winner:
                text = LARGE_FONT.render(f"Player {winner} wins!", True, (255, 255, 255))
            else:
                text = LARGE_FONT.render("It's a draw!", True, (255, 255, 255))
            
            text_rect = text.get_rect(center=(WIDTH // 2, 3 * SQUARE_SIZE // 2 - 30))
            restart_text = FONT.render("Press 'r' to restart", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, 3 * SQUARE_SIZE // 2 + 30))
            
            screen.blit(text, text_rect)
            screen.blit(restart_text, restart_rect)
    
    pygame.display.update()
