import pygame
import sys
import random
import time
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 15
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# Colors
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tic Tac Toe with AI')
screen.fill(BG_COLOR)

# Board
board = [[None for x in range(BOARD_COLS)] for y in range(BOARD_ROWS)]
game_over = False
player_turn = True  # True for player, False for AI
winner = None

def draw_lines():
    # Horizontal lines
    pygame.draw.line(screen, LINE_COLOR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH)
    
    # Vertical lines
    pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, HEIGHT), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

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

def draw_winning_line(player):
    # Function to draw a line through winning combination
    # This will be implemented based on the winning combination
    pass

def reset_game():
    global board, game_over, player_turn, winner
    screen.fill(BG_COLOR)
    draw_lines()
    board = [[None for x in range(BOARD_COLS)] for y in range(BOARD_ROWS)]
    game_over = False
    player_turn = True
    winner = None

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

def best_move():
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

def ai_move():
    global player_turn, game_over, winner
    
    if not game_over and not player_turn:
        row, col = best_move()
        mark_square(row, col, 'X')
        winner = check_win()
        if winner or is_board_full():
            game_over = True
        player_turn = True

# Main game loop
draw_lines()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over and player_turn:
            mouseX = event.pos[0]
            mouseY = event.pos[1]
            
            clicked_row = mouseY // SQUARE_SIZE
            clicked_col = mouseX // SQUARE_SIZE
            
            if mark_square(clicked_row, clicked_col, 'O'):
                winner = check_win()
                if winner or is_board_full():
                    game_over = True
                player_turn = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
    
    # AI's turn
    if not game_over and not player_turn:
        # Add a small delay to make AI move visible
        pygame.display.update()
        time.sleep(0.5)
        ai_move()
    
    draw_figures()
    
    # Display game over or winner message
    if game_over:
        font = pygame.font.Font(None, 40)
        if winner:
            text = font.render(f"Player {winner} wins!", True, (0, 0, 0))
        else:
            text = font.render("It's a draw!", True, (0, 0, 0))
        
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        restart_text = font.render("Press 'r' to restart", True, (0, 0, 0))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        
        screen.blit(text, text_rect)
        screen.blit(restart_text, restart_rect)
    
    pygame.display.update()
