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
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = 200  # Base size (will be adjusted)

# Modern Color Scheme
THEME = {
    "bg_primary": (25, 26, 30),            # Dark background
    "bg_secondary": (35, 37, 42),          # Slightly lighter background
    "accent_primary": (88, 101, 242),      # Discord-like blue
    "accent_secondary": (114, 137, 218),   # Lighter blue
    "text_primary": (255, 255, 255),       # White text
    "text_secondary": (185, 187, 190),     # Light gray text
    "success": (59, 165, 93),              # Green
    "danger": (237, 66, 69),               # Red
    "warning": (250, 168, 26),             # Yellow/Orange
    "grid_lines": (57, 60, 67),            # Dark gray for grid
    "o_marker": (114, 137, 218),           # Blue for O (Player)
    "x_marker": (237, 66, 69),             # Red for X (AI)
}

# Set up the display - make it resizable
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Tic Tac Toe with AI')
icon = pygame.Surface((32, 32))
icon.fill(THEME["bg_primary"])
pygame.draw.line(icon, THEME["x_marker"], (8, 8), (24, 24), 4)
pygame.draw.line(icon, THEME["x_marker"], (24, 8), (8, 24), 4)
pygame.draw.circle(icon, THEME["o_marker"], (16, 16), 12, 2)
pygame.display.set_icon(icon)
screen.fill(THEME["bg_primary"])

# Font sizes based on scale
font_size_small = max(10, int(18))
font_size_medium = max(12, int(24)) 
font_size_large = max(18, int(36))
font_size_xlarge = max(24, int(48))

# Load fonts
pygame.font.init()
try:
    # Try to use a nice font if available (or fall back to Arial)
    FONT = pygame.font.SysFont('Segoe UI, Arial', font_size_medium)
    LARGE_FONT = pygame.font.SysFont('Segoe UI, Arial', font_size_large)
    XLARGE_FONT = pygame.font.SysFont('Segoe UI, Arial', font_size_xlarge, bold=True)
    SMALL_FONT = pygame.font.SysFont('Segoe UI, Arial', font_size_small)
    FONT_BOLD = pygame.font.SysFont('Segoe UI, Arial', font_size_medium, bold=True)
except:
    # Fallback
    FONT = pygame.font.SysFont('Arial', font_size_medium)
    LARGE_FONT = pygame.font.SysFont('Arial', font_size_large)
    XLARGE_FONT = pygame.font.SysFont('Arial', font_size_xlarge, bold=True)
    SMALL_FONT = pygame.font.SysFont('Arial', font_size_small)
    FONT_BOLD = pygame.font.SysFont('Arial', font_size_medium, bold=True)

# Game state
in_welcome_screen = True
in_game = False
game_over = False
show_results_overlay = False
winner = None
player_turn = True  # True for player, False for AI
board = [[None for x in range(BOARD_COLS)] for y in range(BOARD_ROWS)]

# AI setup
ai_modes = ["Minimax", "Pattern Recognition"]
current_ai_mode = 0  # Default to Minimax

# Pattern recognition data structure
player_patterns = {}
player_id = "default_player"
current_game_moves = []

# Game settings
game_settings = GameSettings()
settings = game_settings.get_settings()

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

def calculate_dimensions(window_width, window_height):
    """Calculate responsive dimensions based on window size"""
    global WIDTH, HEIGHT, SQUARE_SIZE, FONT, LARGE_FONT, XLARGE_FONT, SMALL_FONT, FONT_BOLD
    
    # Calculate scale factor
    scale_w = window_width / BASE_WIDTH
    scale_h = window_height / BASE_HEIGHT
    scale = min(scale_w, scale_h)
    
    # Update dimensions
    WIDTH = window_width
    HEIGHT = window_height
    SQUARE_SIZE = max(50, int(200 * scale))
    
    # Update fonts
    font_size_small = max(10, int(18 * scale))
    font_size_medium = max(12, int(24 * scale))
    font_size_large = max(18, int(36 * scale))
    font_size_xlarge = max(24, int(48 * scale))
    
    try:
        FONT = pygame.font.SysFont('Segoe UI, Arial', font_size_medium)
        LARGE_FONT = pygame.font.SysFont('Segoe UI, Arial', font_size_large)
        XLARGE_FONT = pygame.font.SysFont('Segoe UI, Arial', font_size_xlarge, bold=True)
        SMALL_FONT = pygame.font.SysFont('Segoe UI, Arial', font_size_small)
        FONT_BOLD = pygame.font.SysFont('Segoe UI, Arial', font_size_medium, bold=True)
    except:
        FONT = pygame.font.SysFont('Arial', font_size_medium)
        LARGE_FONT = pygame.font.SysFont('Arial', font_size_large)
        XLARGE_FONT = pygame.font.SysFont('Arial', font_size_xlarge, bold=True)
        SMALL_FONT = pygame.font.SysFont('Arial', font_size_small)
        FONT_BOLD = pygame.font.SysFont('Arial', font_size_medium, bold=True)

def handle_resize(width, height):
    """Handle window resize event"""
    # Calculate new dimensions
    calculate_dimensions(width, height)
    
    # Redraw everything
    if in_welcome_screen:
        draw_welcome_screen()
    elif in_game:
        # Redraw game screen
        screen.fill(THEME["bg_primary"])
        draw_board()
        draw_figures()
        draw_stats_panel()
        draw_ai_selector()
        
        # Redraw game over overlay if needed
        if game_over and show_results_overlay:
            draw_game_over_overlay()

def create_rounded_rect(width, height, radius=10):
    """Create a surface with a rounded rectangle"""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    rect = pygame.Rect(0, 0, width, height)
    pygame.draw.rect(surface, (255, 255, 255), rect, border_radius=radius)
    return surface

def draw_button(text, rect, bg_color, text_color=THEME["text_primary"], border_radius=10, border_color=None, hover=False):
    """Draw a button with optional hover effect"""
    x, y, width, height = rect
    
    # Create hover effect
    if hover:
        # Lighten the color for hover
        bg_color = tuple(min(c + 20, 255) for c in bg_color)
    
    # Draw the button background
    pygame.draw.rect(screen, bg_color, (x, y, width, height), border_radius=border_radius)
    
    # Draw border if specified
    if border_color:
        pygame.draw.rect(screen, border_color, (x, y, width, height), 1, border_radius=border_radius)
    
    # Render text
    text_surface = FONT.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
    screen.blit(text_surface, text_rect)

def draw_welcome_screen():
    """Draw the welcome screen with modern UI design"""
    # Create a gradient background
    for y in range(HEIGHT):
        # Calculate gradient color (dark at top to slightly lighter at bottom)
        factor = y / HEIGHT
        color = [THEME["bg_primary"][i] + int((THEME["bg_secondary"][i] - THEME["bg_primary"][i]) * factor) for i in range(3)]
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))
    
    # Draw decorative header bar
    header_height = HEIGHT // 6
    pygame.draw.rect(screen, THEME["accent_primary"], (0, 0, WIDTH, header_height))
    
    # Draw logo/title
    title_y = header_height + 40
    
    # Draw a stylized tic-tac-toe grid as logo
    logo_size = min(WIDTH // 3, HEIGHT // 3)
    logo_x = WIDTH // 2 - logo_size // 2
    logo_y = header_height + 20
    
    # Draw grid lines for the logo
    cell_size = logo_size // 3
    line_width = max(3, logo_size // 30)
    
    # Draw vertical lines
    pygame.draw.line(screen, THEME["text_primary"], 
                    (logo_x + cell_size, logo_y), 
                    (logo_x + cell_size, logo_y + logo_size), line_width)
    pygame.draw.line(screen, THEME["text_primary"], 
                    (logo_x + 2*cell_size, logo_y), 
                    (logo_x + 2*cell_size, logo_y + logo_size), line_width)
    
    # Draw horizontal lines
    pygame.draw.line(screen, THEME["text_primary"], 
                    (logo_x, logo_y + cell_size), 
                    (logo_x + logo_size, logo_y + cell_size), line_width)
    pygame.draw.line(screen, THEME["text_primary"], 
                    (logo_x, logo_y + 2*cell_size), 
                    (logo_x + logo_size, logo_y + 2*cell_size), line_width)
    
    # Draw X and O in the logo
    x_pos = [(0, 0), (1, 1), (2, 2)]
    o_pos = [(0, 2), (1, 0), (2, 1)]
    
    # Draw Xs
    for row, col in x_pos:
        x_center_x = logo_x + col * cell_size + cell_size // 2
        x_center_y = logo_y + row * cell_size + cell_size // 2
        x_size = cell_size // 3
        
        pygame.draw.line(screen, THEME["x_marker"], 
                        (x_center_x - x_size, x_center_y - x_size),
                        (x_center_x + x_size, x_center_y + x_size), line_width)
        pygame.draw.line(screen, THEME["x_marker"], 
                        (x_center_x - x_size, x_center_y + x_size),
                        (x_center_x + x_size, x_center_y - x_size), line_width)
    
    # Draw Os
    for row, col in o_pos:
        o_center_x = logo_x + col * cell_size + cell_size // 2
        o_center_y = logo_y + row * cell_size + cell_size // 2
        o_radius = cell_size // 3
        
        pygame.draw.circle(screen, THEME["o_marker"], 
                          (o_center_x, o_center_y), o_radius, line_width - 1)
    
    # Draw title text
    title_y = logo_y + logo_size + 30
    title = XLARGE_FONT.render("TIC TAC TOE", True, THEME["text_primary"])
    subtitle = LARGE_FONT.render("with Advanced AI", True, THEME["text_secondary"])
    
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, title_y))
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, title_y + title.get_height()))
    
    # Draw start button with shadow
    button_width = min(WIDTH - 80, 300)
    button_height = int(60)
    button_x = WIDTH // 2 - button_width // 2
    button_y = title_y + title.get_height() + subtitle.get_height() + 40
    
    # Draw button shadow
    shadow_offset = 4
    pygame.draw.rect(screen, (0, 0, 0, 128), 
                    (button_x + shadow_offset, button_y + shadow_offset, button_width, button_height), 
                    border_radius=10)
    
    # Draw main button
    draw_button("START GAME", (button_x, button_y, button_width, button_height), 
               THEME["accent_primary"], THEME["text_primary"], border_radius=10)
    
    # Draw AI mode selector
    draw_welcome_ai_selector()
    
    # Draw difficulty selector
    draw_welcome_difficulty_selector()
    
    # Draw statistics section if games have been played
    if game_stats["total_games"] > 0:
        draw_welcome_stats()
    
    # Draw instructions
    instructions_y = HEIGHT - 140
    instruction_title = FONT_BOLD.render("How to Play:", True, THEME["text_primary"])
    screen.blit(instruction_title, (WIDTH // 2 - instruction_title.get_width() // 2, instructions_y))
    
    instructions = [
        "• Click on a square to place your 'O'",
        "• Beat the AI by getting three in a row",
        "• Press 'R' to restart anytime | 'ESC' for menu | 'F11' for fullscreen"
    ]
    
    y_pos = instructions_y + instruction_title.get_height() + 10
    for instruction in instructions:
        text = SMALL_FONT.render(instruction, True, THEME["text_secondary"])
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_pos))
        y_pos += text.get_height() + 5

def draw_welcome_stats():
    """Draw game statistics on welcome screen"""
    stats_y = HEIGHT - 260
    stats_title = FONT_BOLD.render("Your Statistics", True, THEME["text_primary"])
    screen.blit(stats_title, (WIDTH // 2 - stats_title.get_width() // 2, stats_y))
    
    # Create stat boxes
    box_width = min(WIDTH - 80, 500) // 3 - 10
    box_height = 80
    box_y = stats_y + stats_title.get_height() + 10
    
    # Draw stats boxes
    stats = [
        {"label": "Games", "value": game_stats["total_games"], "color": THEME["accent_secondary"]},
        {"label": "Wins", "value": game_stats["player_wins"], "color": THEME["success"]},
        {"label": "Win Rate", "value": f"{int(game_stats['player_wins']/max(1, game_stats['total_games'])*100)}%", "color": THEME["warning"]}
    ]
    
    for i, stat in enumerate(stats):
        box_x = WIDTH//2 - (box_width*3 + 20)//2 + i*(box_width + 10)
        
        # Draw box with shadow
        pygame.draw.rect(screen, (0, 0, 0, 100), 
                       (box_x + 2, box_y + 2, box_width, box_height), 
                       border_radius=10)
        
        pygame.draw.rect(screen, stat["color"], 
                       (box_x, box_y, box_width, box_height), 
                       border_radius=10)
        
        # Draw stat value (large)
        value_text = LARGE_FONT.render(str(stat["value"]), True, THEME["text_primary"])
        screen.blit(value_text, (box_x + box_width//2 - value_text.get_width()//2, box_y + 15))
        
        # Draw stat label (small)
        label_text = SMALL_FONT.render(stat["label"], True, THEME["text_primary"])
        screen.blit(label_text, (box_x + box_width//2 - label_text.get_width()//2, 
                              box_y + box_height - label_text.get_height() - 10))

def draw_welcome_ai_selector():
    """Draw buttons to select AI mode on welcome screen with modern design"""
    title_y = HEIGHT // 2 + 140
    text = FONT_BOLD.render("Select AI Mode", True, THEME["text_primary"])
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, title_y))
    
    button_width = min(180, WIDTH // 3)
    button_height = 50
    button_spacing = 20
    buttons_total_width = len(ai_modes) * button_width + (len(ai_modes) - 1) * button_spacing
    starting_x = WIDTH // 2 - buttons_total_width // 2
    y_pos = title_y + text.get_height() + 15
    
    for i, mode in enumerate(ai_modes):
        x_pos = starting_x + i * (button_width + button_spacing)
        
        # Draw button
        color = THEME["accent_primary"] if i == current_ai_mode else THEME["bg_secondary"]
        border_color = THEME["accent_secondary"] if i == current_ai_mode else THEME["grid_lines"]
        
        # Draw shadow
        if i == current_ai_mode:
            shadow_offset = 3
            pygame.draw.rect(screen, (0, 0, 0, 100), 
                           (x_pos + shadow_offset, y_pos + shadow_offset, button_width, button_height), 
                           border_radius=10)
        
        # Draw button
        draw_button(mode, (x_pos, y_pos, button_width, button_height), 
                  color, border_color=border_color, border_radius=10)

def draw_welcome_difficulty_selector():
    """Draw buttons to select difficulty on welcome screen with modern design"""
    title_y = HEIGHT // 2 + 220
    text = FONT_BOLD.render("Select Difficulty", True, THEME["text_primary"])
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, title_y))
    
    difficulties = ["Easy", "Medium", "Hard"]
    button_width = min(180, WIDTH // 3)
    button_height = 50
    button_spacing = 20
    buttons_total_width = len(difficulties) * button_width + (len(difficulties) - 1) * button_spacing
    starting_x = WIDTH // 2 - buttons_total_width // 2
    y_pos = title_y + text.get_height() + 15
    
    for i, difficulty in enumerate(difficulties):
        x_pos = starting_x + i * (button_width + button_spacing)
        
        # Draw button
        color = THEME["accent_primary"] if i == game_settings.difficulty else THEME["bg_secondary"]
        border_color = THEME["accent_secondary"] if i == game_settings.difficulty else THEME["grid_lines"]
        
        # Draw shadow
        if i == game_settings.difficulty:
            shadow_offset = 3
            pygame.draw.rect(screen, (0, 0, 0, 100), 
                           (x_pos + shadow_offset, y_pos + shadow_offset, button_width, button_height), 
                           border_radius=10)
        
        # Draw button
        draw_button(difficulty, (x_pos, y_pos, button_width, button_height), 
                  color, border_color=border_color, border_radius=10)

def handle_welcome_click(pos):
    """Handle clicks on welcome screen"""
    global in_welcome_screen, in_game, current_ai_mode, game_settings
    
    # Check if clicked on start button
    button_width = min(WIDTH - 80, 300)
    button_height = 60
    
    # Calculate position of elements
    logo_size = min(WIDTH // 3, HEIGHT // 3)
    header_height = HEIGHT // 6
    logo_y = header_height + 20
    title_y = logo_y + logo_size + 30
    
    # Get title dimensions for calculation
    title = XLARGE_FONT.render("TIC TAC TOE", True, THEME["text_primary"])
    subtitle = LARGE_FONT.render("with Advanced AI", True, THEME["text_secondary"])
    
    button_x = WIDTH // 2 - button_width // 2
    button_y = title_y + title.get_height() + subtitle.get_height() + 40
    
    if (button_x <= pos[0] <= button_x + button_width and
        button_y <= pos[1] <= button_y + button_height):
        in_welcome_screen = False
        in_game = True
        start_game()
        return True
    
    # Check if clicked on AI mode selector
    title_y = HEIGHT // 2 + 140
    text = FONT_BOLD.render("Select AI Mode", True, THEME["text_primary"])
    
    button_width = min(180, WIDTH // 3)
    button_height = 50
    button_spacing = 20
    buttons_total_width = len(ai_modes) * button_width + (len(ai_modes) - 1) * button_spacing
    starting_x = WIDTH // 2 - buttons_total_width // 2
    y_pos = title_y + text.get_height() + 15
    
    if y_pos <= pos[1] <= y_pos + button_height:
        for i in range(len(ai_modes)):
            x_pos = starting_x + i * (button_width + button_spacing)
            if x_pos <= pos[0] <= x_pos + button_width:
                current_ai_mode = i
                # Redraw the welcome screen to show selection
                draw_welcome_screen()
                return True
    
    # Check if clicked on difficulty selector
    title_y = HEIGHT // 2 + 220
    text = FONT_BOLD.render("Select Difficulty", True, THEME["text_primary"])
    
    difficulties = ["Easy", "Medium", "Hard"]
    button_width = min(180, WIDTH // 3)
    button_height = 50
    button_spacing = 20
    buttons_total_width = len(difficulties) * button_width + (len(difficulties) - 1) * button_spacing
    starting_x = WIDTH // 2 - buttons_total_width // 2
    y_pos = title_y + text.get_height() + 15
    
    if y_pos <= pos[1] <= y_pos + button_height:
        for i in range(len(difficulties)):
            x_pos = starting_x + i * (button_width + button_spacing)
            if x_pos <= pos[0] <= x_pos + button_width:
                game_settings.difficulty = i
                # Redraw the welcome screen to show selection
                draw_welcome_screen()
                return True
    
    return False

def start_game():
    """Initialize and start a new game"""
    global board, game_over, player_turn, winner, current_game_moves, show_results_overlay
    
    screen.fill(THEME["bg_primary"])
    draw_board()
    draw_stats_panel()
    draw_ai_selector()
    board = [[None for x in range(BOARD_COLS)] for y in range(BOARD_ROWS)]
    game_over = False
    player_turn = True
    winner = None
    current_game_moves = []
    show_results_overlay = False
    
    pygame.display.update()

def draw_board():
    """Draw the game board with modern styling"""
    # Calculate board position to center it
    board_width = 3 * SQUARE_SIZE
    board_height = 3 * SQUARE_SIZE
    board_x = WIDTH // 2 - board_width // 2
    
    # Draw board background with slight gradient
    for y in range(board_height):
        # Calculate gradient color
        factor = y / board_height
        color = [THEME["bg_secondary"][i] + int((THEME["bg_primary"][i] - THEME["bg_secondary"][i]) * factor) for i in range(3)]
        pygame.draw.line(screen, color, (board_x, y), (board_x + board_width, y))
    
    # Draw grid lines
    line_width = max(2, int(SQUARE_SIZE * 0.05))
    
    # Horizontal lines
    for i in range(1, BOARD_ROWS):
        pygame.draw.line(
            screen, THEME["grid_lines"], 
            (board_x, i * SQUARE_SIZE), 
            (board_x + board_width, i * SQUARE_SIZE), 
            line_width
        )
    
    # Vertical lines
    for i in range(1, BOARD_COLS):
        pygame.draw.line(
            screen, THEME["grid_lines"], 
            (board_x + i * SQUARE_SIZE, 0), 
            (board_x + i * SQUARE_SIZE, board_height), 
            line_width
        )
    
    # Draw board border
    pygame.draw.rect(screen, THEME["grid_lines"], 
                   (board_x, 0, board_width, board_height), 
                   max(1, line_width // 3), border_radius=5)

def draw_figures():
    """Draw X and O on the board with improved styling"""
    # Calculate board position to center it
    board_width = 3 * SQUARE_SIZE
    board_x = WIDTH // 2 - board_width // 2
    
    # Calculate sizing based on square size
    circle_radius = int(SQUARE_SIZE * 0.35)
    circle_width = max(3, int(SQUARE_SIZE * 0.05))
    cross_width = max(3, int(SQUARE_SIZE * 0.08))
    cross_size = int(SQUARE_SIZE * 0.3)
    
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            center_x = board_x + col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            
            if board[row][col] == 'X':
                # Draw X with shadow effect
                # Shadow
                shadow_offset = max(1, circle_width // 2)
                pygame.draw.line(
                    screen, (0, 0, 0, 128),
                    (center_x - cross_size + shadow_offset, center_y - cross_size + shadow_offset),
                    (center_x + cross_size + shadow_offset, center_y + cross_size + shadow_offset),
                    cross_width
                )
                pygame.draw.line(
                    screen, (0, 0, 0, 128),
                    (center_x + cross_size + shadow_offset, center_y - cross_size + shadow_offset),
                    (center_x - cross_size + shadow_offset, center_y + cross_size + shadow_offset),
                    cross_width
                )
                
                # X
                pygame.draw.line(
                    screen, THEME["x_marker"],
                    (center_x - cross_size, center_y - cross_size),
                    (center_x + cross_size, center_y + cross_size),
                    cross_width
                )
                pygame.draw.line(
                    screen, THEME["x_marker"],
                    (center_x + cross_size, center_y - cross_size),
                    (center_x - cross_size, center_y + cross_size),
                    cross_width
                )
                
            elif board[row][col] == 'O':
                # Draw O with shadow effect
                # Shadow
                shadow_offset = max(1, circle_width // 2)
                pygame.draw.circle(
                    screen, (0, 0, 0, 128),
                    (center_x + shadow_offset, center_y + shadow_offset),
                    circle_radius, circle_width
                )
                
                # O
                pygame.draw.circle(
                    screen, THEME["o_marker"],
                    (center_x, center_y),
                    circle_radius, circle_width
                )

def mark_square(row, col, player):
    if board[row][col] is None:
        board[row][col] = player
        
        # Add visual effect when marking a square
        draw_mark_animation(row, col, player)
        return True
    return False

def draw_mark_animation(row, col, player):
    """Draw animation when marking a square"""
    # Calculate board position to center it
    board_width = 3 * SQUARE_SIZE
    board_x = WIDTH // 2 - board_width // 2
    
    # Center of the square
    center_x = board_x + col * SQUARE_SIZE + SQUARE_SIZE // 2
    center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
    
    # Draw appropriate animation based on player marker
    if player == 'O':
        # Animate O drawing (growing circle)
        circle_radius = int(SQUARE_SIZE * 0.35)
        circle_width = max(3, int(SQUARE_SIZE * 0.05))
        
        for i in range(10):
            # Clear previous animation frame
            pygame.draw.rect(screen, THEME["bg_secondary"], 
                           (board_x + col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
            # Draw growing circle
            current_radius = circle_radius * (i + 1) / 10
            pygame.draw.circle(
                screen, THEME["o_marker"],
                (center_x, center_y),
                current_radius, circle_width
            )
            pygame.display.update()
            pygame.time.delay(15)
    else:
        # Animate X drawing (drawing each line)
        cross_width = max(3, int(SQUARE_SIZE * 0.08))
        cross_size = int(SQUARE_SIZE * 0.3)
        
        # First line of X
        for i in range(10):
            # Clear previous animation frame
            pygame.draw.rect(screen, THEME["bg_secondary"], 
                           (board_x + col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
            # Draw growing line
            ratio = (i + 1) / 10
            end_x = center_x - cross_size + (cross_size * 2) * ratio
            end_y = center_y - cross_size + (cross_size * 2) * ratio
            
            pygame.draw.line(
                screen, THEME["x_marker"],
                (center_x - cross_size, center_y - cross_size),
                (end_x, end_y),
                cross_width
            )
            pygame.display.update()
            pygame.time.delay(15)
        
        # Second line of X
        for i in range(10):
            ratio = (i + 1) / 10
            end_x = center_x + cross_size - (cross_size * 2) * ratio
            end_y = center_y - cross_size + (cross_size * 2) * ratio
            
            pygame.draw.line(
                screen, THEME["x_marker"],
                (center_x + cross_size, center_y - cross_size),
                (end_x, end_y),
                cross_width
            )
            pygame.display.update()
            pygame.time.delay(15)

def is_board_full():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] is None:
                return False
    return True

def check_horizontal_win():
    for row in range(BOARD_ROWS):
        if board[row][0] == board[row][1] == board[row][2] and board[row][0] is not None:
            # Draw winning line
            draw_winning_line('h', row)
            return board[row][0]
    return None

def check_vertical_win():
    for col in range(BOARD_COLS):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] is not None:
            # Draw winning line
            draw_winning_line('v', col)
            return board[0][col]
    return None

def check_diagonal_win():
    # Check diagonal from top-left to bottom-right
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        draw_winning_line('d1', None)
        return board[0][0]
    
    # Check diagonal from top-right to bottom-left
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        draw_winning_line('d2', None)
        return board[0][2]
    
    return None

def draw_winning_line(line_type, index):
    """Draw animated winning line"""
    # Calculate board position to center it
    board_width = 3 * SQUARE_SIZE
    board_x = WIDTH // 2 - board_width // 2
    
    line_width = max(4, int(SQUARE_SIZE * 0.06))
    win_color = THEME["success"]
    
    # Define start and end points based on line type
    if line_type == 'h':  # Horizontal
        start_x = board_x + SQUARE_SIZE * 0.1
        end_x = board_x + SQUARE_SIZE * 2.9
        y = index * SQUARE_SIZE + SQUARE_SIZE // 2
        start_point = (start_x, y)
        end_point = (end_x, y)
    
    elif line_type == 'v':  # Vertical
        x = board_x + index * SQUARE_SIZE + SQUARE_SIZE // 2
        start_y = SQUARE_SIZE * 0.1
        end_y = SQUARE_SIZE * 2.9
        start_point = (x, start_y)
        end_point = (x, end_y)
    
    elif line_type == 'd1':  # Diagonal top-left to bottom-right
        start_x = board_x + SQUARE_SIZE * 0.1
        start_y = SQUARE_SIZE * 0.1
        end_x = board_x + SQUARE_SIZE * 2.9
        end_y = SQUARE_SIZE * 2.9
        start_point = (start_x, start_y)
        end_point = (end_x, end_y)
    
    else:  # Diagonal top-right to bottom-left
        start_x = board_x + SQUARE_SIZE * 2.9
        start_y = SQUARE_SIZE * 0.1
        end_x = board_x + SQUARE_SIZE * 0.1
        end_y = SQUARE_SIZE * 2.9
        start_point = (start_x, start_y)
        end_point = (end_x, end_y)
    
    # Animated line drawing with glow effect
    for i in range(21):
        current_end_x = start_point[0] + (end_point[0] - start_point[0]) * (i / 20)
        current_end_y = start_point[1] + (end_point[1] - start_point[1]) * (i / 20)
        current_end = (current_end_x, current_end_y)
        
        # Draw glow effect (multiple lines with decreasing opacity)
        for glow in range(3):
            glow_width = line_width + (3-glow)*2
            glow_alpha = 100 - glow * 30
            glow_color = (*win_color, glow_alpha)
            
            pygame.draw.line(
                screen,
                glow_color,
                start_point,
                current_end,
                glow_width
            )
        
        # Draw main line
        pygame.draw.line(
            screen,
            win_color,
            start_point,
            current_end,
            line_width
        )
        
        pygame.display.update()
        pygame.time.delay(20)

def check_win():
    winner = check_horizontal_win()
    if winner is None:
        winner = check_vertical_win()
    if winner is None:
        winner = check_diagonal_win()
    return winner

def draw_game_over_overlay():
    """Draw game over overlay with modern design"""
    # Create a semi-transparent overlay over the board area
    overlay_height = 3 * SQUARE_SIZE
    overlay = pygame.Surface((WIDTH, overlay_height), pygame.SRCALPHA)
    
    # Gradient overlay
    for y in range(overlay_height):
        alpha = 180 - int(60 * y / overlay_height)  # Fade effect
        color = (*THEME["bg_primary"], alpha)
        pygame.draw.line(overlay, color, (0, y), (WIDTH, y))
    
    screen.blit(overlay, (0, 0))
    
    # Create a rounded card for the result
    card_width = min(WIDTH - 60, 400)
    card_height = 200
    card_x = WIDTH // 2 - card_width // 2
    card_y = overlay_height // 2 - card_height // 2
    
    # Draw card shadow
    shadow_offset = 8
    pygame.draw.rect(screen, (0, 0, 0, 100), 
                   (card_x + shadow_offset, card_y + shadow_offset, card_width, card_height), 
                   border_radius=15)
    
    # Draw card background
    pygame.draw.rect(screen, THEME["bg_secondary"], 
                   (card_x, card_y, card_width, card_height), 
                   border_radius=15)
    pygame.draw.rect(screen, THEME["grid_lines"], 
                   (card_x, card_y, card_width, card_height), 
                   2, border_radius=15)
    
    # Draw result text
    if winner == 'O':
        result_color = THEME["success"]
        result_text = "You Win!"
    elif winner == 'X':
        result_color = THEME["danger"] 
        result_text = "AI Wins!"
    else:
        result_color = THEME["warning"]
        result_text = "It's a Draw!"
    
    # Add colored accent bar at top of card
    pygame.draw.rect(screen, result_color, 
                   (card_x, card_y, card_width, 6), 
                   border_top_left_radius=15, border_top_right_radius=15)
    
    # Draw title
    text = LARGE_FONT.render(result_text, True, result_color)
    screen.blit(text, (card_x + card_width//2 - text.get_width()//2, card_y + 30))
    
    # Draw instruction
    restart_text = FONT.render("Press 'R' to play again", True, THEME["text_secondary"])
    screen.blit(restart_text, (card_x + card_width//2 - restart_text.get_width()//2, card_y + 90))
    
    menu_text = FONT.render("Press 'ESC' for menu", True, THEME["text_secondary"])
    screen.blit(menu_text, (card_x + card_width//2 - menu_text.get_width()//2, card_y + 130))

def reset_game():
    """Reset the game to start a new round"""
    global board, game_over, player_turn, winner, current_game_moves, show_results_overlay
    
    board = [[None for x in range(BOARD_COLS)] for y in range(BOARD_ROWS)]
    game_over = False
    winner = None
    player_turn = True
    current_game_moves = []
    show_results_overlay = False
    
    # Redraw game screen
    screen.fill(THEME["bg_primary"])
    draw_board()
    draw_stats_panel()
    draw_ai_selector()

def minimax(board, depth, is_maximizing):
    # Check terminal states
    result = check_win_for_board(board)
    if result == 'X':  # AI
        return 10 - depth
    if result == 'O':  # Player
        return depth - 10
    
    # Check for draw
    is_full = True
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] is None:
                is_full = False
                break
        if not is_full:
            break
    
    if is_full:
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

def best_move_minimax(depth):
    """Find best move using minimax algorithm with optimization for first moves"""
    settings = game_settings.adjust_settings('tictactoe')
    
    # ทำให้ AI ช้าลงในโหมดง่ายเพื่อให้ผู้เล่นมีเวลาคิด
    if settings['ai_delay'] > 0:
        time.sleep(settings['ai_delay'])
    
    # ปรับความลึกของการค้นหาตามระดับความยาก
    depth = min(depth, settings['search_depth'])
    
    return minimax(board, depth, False)[1]

def pattern_recognition_move():
    """Choose move based on pattern recognition with improved strategy"""
    settings = game_settings.adjust_settings('tictactoe')
    
    # ทำนายการเคลื่อนที่ของผู้เล่น
    predicted_move = predict_player_move()
    
    # หาการเคลื่อนที่ที่ดีที่สุดตามรูปแบบที่พบ
    patterns = analyze_game_patterns()
    
    # ปรับความสุ่มตามระดับความยาก
    if settings['randomness'] > random.random():
        empty_cells = [(r, c) for r in range(BOARD_ROWS) for c in range(BOARD_COLS) if board[r][c] is None]
        if empty_cells:
            return random.choice(empty_cells)
    
    # หาการเคลื่อนที่ที่ดีที่สุด
    best_move = None
    best_score = float('-inf')
    
    for r in range(BOARD_ROWS):
        for c in range(BOARD_COLS):
            if board[r][c] is None:
                # คำนวณคะแนนตามรูปแบบที่พบ
                score = 0
                if predicted_move == (r, c):
                    score += 100
                if patterns and (r, c) in patterns:
                    score += patterns[(r, c)] * settings['pattern_weight']
                
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
    
    return best_move if best_move else (random.randint(0, 2), random.randint(0, 2))

def calculate_board_complexity(board):
    """คำนวณความซับซ้อนของกระดาน"""
    # นับจำนวนช่องว่าง
    empty_cells = sum(1 for row in board for cell in row if cell is None)
    
    # นับจำนวนการจัดเรียงที่เป็นไปได้
    possible_lines = 0
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] is None:
                # ตรวจสอบแนวนอน
                if col < 2 and (board[row][col+1] is None or board[row][col+1] == board[row][col]):
                    possible_lines += 1
                # ตรวจสอบแนวตั้ง
                if row < 2 and (board[row+1][col] is None or board[row+1][col] == board[row][col]):
                    possible_lines += 1
                # ตรวจสอบแนวทแยง
                if row < 2 and col < 2 and (board[row+1][col+1] is None or board[row+1][col+1] == board[row][col]):
                    possible_lines += 1
                if row < 2 and col > 0 and (board[row+1][col-1] is None or board[row+1][col-1] == board[row][col]):
                    possible_lines += 1
    
    # คำนวณความซับซ้อนโดยรวม
    complexity = (empty_cells + possible_lines) / 10.0
    return complexity

def ai_move():
    """AI makes its move based on current settings"""
    settings = game_settings.adjust_settings('tictactoe')
    
    # คำนวณเวลาคิดตามความซับซ้อนของกระดาน
    move_count = sum(1 for row in board for cell in row if cell is not None)
    complexity = calculate_board_complexity(board)
    thinking_time = game_settings.calculate_thinking_time('tictactoe', move_count, complexity)
    
    # ปรับความลึกของการค้นหาตามเวลาคิด
    search_depth = min(settings['search_depth'], int(thinking_time * 2))
    
    if settings['randomness'] > random.random():
        # ทำให้การเคลื่อนที่ของ AI มีความสุ่มบ้าง
        empty_cells = [(r, c) for r in range(BOARD_ROWS) for c in range(BOARD_COLS) if board[r][c] is None]
        if empty_cells:
            row, col = random.choice(empty_cells)
            return row, col
    
    if current_ai_mode == 0:  # Minimax
        return best_move_minimax(search_depth)
    else:  # Pattern Recognition
        return pattern_recognition_move()

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
    """Draw the game statistics panel with modern design"""
    panel_height = HEIGHT - 3 * SQUARE_SIZE
    panel_y = 3 * SQUARE_SIZE
    
    # Draw panel background with gradient
    for i in range(panel_height):
        alpha = 255 - int(i / panel_height * 30)  # Subtle gradient
        color = (THEME["bg_secondary"][0], THEME["bg_secondary"][1], THEME["bg_secondary"][2], alpha)
        pygame.draw.line(screen, color, (0, panel_y + i), (WIDTH, panel_y + i))
    
    # Draw divider line
    pygame.draw.line(screen, THEME["grid_lines"], (0, panel_y), (WIDTH, panel_y), 2)
    
    # Draw stats title
    title = FONT_BOLD.render("Game Statistics", True, THEME["text_primary"])
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, panel_y + 15))
    
    # Get stats for the current AI mode
    mode = ai_modes[current_ai_mode]
    mode_stats = game_stats.get("ai_mode_stats", {}).get(mode, {"wins": 0, "losses": 0, "draws": 0})
    
    # Draw AI mode info with icon
    mode_label = FONT_BOLD.render(f"AI Mode:", True, THEME["text_secondary"])
    mode_text = FONT.render(f"{mode}", True, THEME["accent_primary"])
    
    # Calculate positions
    mode_x = WIDTH // 2 - (mode_label.get_width() + 10 + mode_text.get_width()) // 2
    mode_y = panel_y + 50
    
    screen.blit(mode_label, (mode_x, mode_y))
    screen.blit(mode_text, (mode_x + mode_label.get_width() + 10, mode_y))
    
    # Calculate stats values
    total_mode_games = mode_stats.get("wins", 0) + mode_stats.get("losses", 0) + mode_stats.get("draws", 0)
    
    # Draw stats boxes in a row
    stats = [
        {"label": "Games", "value": str(total_mode_games), "color": THEME["accent_secondary"]},
        {"label": "Player Wins", "value": str(mode_stats.get("losses", 0)), "color": THEME["success"]},
        {"label": "AI Wins", "value": str(mode_stats.get("wins", 0)), "color": THEME["danger"]},
        {"label": "Draws", "value": str(mode_stats.get("draws", 0)), "color": THEME["warning"]}
    ]
    
    box_height = 80
    box_width = min((WIDTH - 80) // len(stats), 150)
    box_spacing = (WIDTH - (box_width * len(stats))) // (len(stats) + 1)
    box_y = panel_y + 90
    
    for i, stat in enumerate(stats):
        box_x = box_spacing * (i + 1) + box_width * i
        
        # Draw box shadow
        shadow_offset = 4
        pygame.draw.rect(screen, (0, 0, 0, 100), 
                       (box_x + shadow_offset, box_y + shadow_offset, box_width, box_height), 
                       border_radius=10)
        
        # Draw box
        pygame.draw.rect(screen, THEME["bg_primary"], 
                       (box_x, box_y, box_width, box_height), 
                       border_radius=10)
        
        # Draw colored accent on top
        pygame.draw.rect(screen, stat["color"], 
                       (box_x, box_y, box_width, 5), 
                       border_top_left_radius=10, border_top_right_radius=10)
        
        # Draw stat value
        value_text = LARGE_FONT.render(stat["value"], True, THEME["text_primary"])
        screen.blit(value_text, (box_x + box_width//2 - value_text.get_width()//2, 
                              box_y + 25))
        
        # Draw stat label
        label_text = SMALL_FONT.render(stat["label"], True, THEME["text_secondary"])
        screen.blit(label_text, (box_x + box_width//2 - label_text.get_width()//2, 
                              box_y + box_height - label_text.get_height() - 15))
    
    # Draw "Show Results" button
    button_width = 180
    button_height = 40
    button_x = WIDTH // 2 - button_width // 2
    button_y = box_y + box_height + 20
    
    # Check if game is over to determine button color
    if game_over:
        button_color = THEME["accent_primary"]
        hover = False
        
        # Check if mouse is hovering over button
        mouse_pos = pygame.mouse.get_pos()
        if (button_x <= mouse_pos[0] <= button_x + button_width and 
            button_y <= mouse_pos[1] <= button_y + button_height):
            hover = True
            
        # Draw the button with hover effect
        draw_button("Show Results", (button_x, button_y, button_width, button_height), 
                   button_color, hover=hover)

def draw_ai_selector():
    """Draw the AI selector buttons during game with modern design"""
    # Position at the bottom of the screen
    y_pos = HEIGHT - 60
    
    # Draw label
    label = FONT_BOLD.render("AI Mode:", True, THEME["text_secondary"])
    label_x = 20
    screen.blit(label, (label_x, y_pos + 10))
    
        # Draw buttons
    button_width = 150
    button_height = 40
    button_spacing = 10
    
    # Center buttons in remaining space
    total_width = button_width * len(ai_modes) + button_spacing * (len(ai_modes) - 1)
    start_x = WIDTH - total_width - 20
    
    for i, mode in enumerate(ai_modes):
        x_pos = start_x + i * (button_width + button_spacing)
        
        # Draw button
        if i == current_ai_mode:
            # Active button - draw with glow effect
            for j in range(3):
                glow_color = (*THEME["accent_secondary"], 100 - j*30)
                pygame.draw.rect(
                    screen, 
                    glow_color, 
                    (x_pos - j, y_pos - j, button_width + j*2, button_height + j*2), 
                    border_radius=10
                )
            button_color = THEME["accent_primary"]
        else:
            button_color = THEME["bg_secondary"]
        
        # Draw button background
        pygame.draw.rect(screen, button_color, (x_pos, y_pos, button_width, button_height), border_radius=10)
        pygame.draw.rect(screen, THEME["grid_lines"], (x_pos, y_pos, button_width, button_height), 1, border_radius=10)
        
        # Draw button text
        text = FONT.render(mode, True, THEME["text_primary"])
        screen.blit(text, (x_pos + button_width // 2 - text.get_width() // 2, 
                          y_pos + button_height // 2 - text.get_height() // 2))

def handle_button_click(pos):
    """Handle button clicks and return True if a button was clicked"""
    global current_ai_mode, show_results_overlay
    mouseX, mouseY = pos
    
    # Check if "Show Results" button was clicked (only if game is over)
    if game_over:
        button_width = 180
        button_height = 40
        panel_y = 3 * SQUARE_SIZE
        box_height = 80
        
        # Calculate stats boxes position to position the button below them
        box_y = panel_y + 90
        button_x = WIDTH // 2 - button_width // 2
        button_y = box_y + box_height + 20
        
        if (button_x <= mouseX <= button_x + button_width and 
            button_y <= mouseY <= button_y + button_height):
            # Toggle results overlay
            show_results_overlay = not show_results_overlay
            
            # Redraw the screen
            screen.fill(THEME["bg_primary"])
            draw_board()
            draw_figures()
            draw_stats_panel()
            draw_ai_selector()
            
            if show_results_overlay:
                draw_game_over_overlay()
                
            pygame.display.update()
            return True
    
    # Check if AI selector buttons were clicked
    y_pos = HEIGHT - 60
    button_height = 40
    
    if y_pos <= mouseY <= y_pos + button_height:
        button_width = 150
        button_spacing = 10
        total_width = button_width * len(ai_modes) + button_spacing * (len(ai_modes) - 1)
        start_x = WIDTH - total_width - 20
        
        for i, mode in enumerate(ai_modes):
            x_pos = start_x + i * (button_width + button_spacing)
            
            if x_pos <= mouseX <= x_pos + button_width:
                if current_ai_mode != i:
                    # Change AI mode with animation
                    # Flash effect when changing modes
                    flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    flash_surface.fill((255, 255, 255, 30))  # Very light flash
                    screen.blit(flash_surface, (0, 0))
                    pygame.display.update()
                    pygame.time.delay(50)
                    
                    # Change mode
                    current_ai_mode = i
                    
                    # Redraw the screen
                    screen.fill(THEME["bg_primary"])
                    draw_board()
                    draw_figures() 
                    draw_stats_panel()
                    draw_ai_selector()
                    
                    # Keep overlay visible if it was showing
                    if show_results_overlay and game_over:
                        draw_game_over_overlay()
                    
                    pygame.display.update()
                return True
    
    return False

def save_game_stats():
    """Save game statistics to file"""
    try:
        with open('game_stats.json', 'w') as f:
            json.dump(game_stats, f, indent=2)
    except Exception as e:
        print(f"Error saving game stats: {e}")

def save_pattern_data():
    """Save pattern data to file"""
    try:
        with open('player_patterns.json', 'w') as f:
            json.dump(player_patterns, f, indent=2)
    except Exception as e:
        print(f"Error saving pattern data: {e}")

def handle_game_click(pos):
    """Handle clicks during the game on the board"""
    global player_turn, game_over, winner
    
    # Calculate board position
    board_width = 3 * SQUARE_SIZE
    board_x = WIDTH // 2 - board_width // 2
    
    # Only process clicks within the board area and when it's player's turn
    if (not game_over and player_turn and 
        0 <= pos[1] < 3 * SQUARE_SIZE and 
        board_x <= pos[0] < board_x + board_width):
        
        # Adjust mouse coordinates relative to board position
        board_mouseX = pos[0] - board_x
        
        # Calculate clicked cell
        clicked_row = pos[1] // SQUARE_SIZE
        clicked_col = board_mouseX // SQUARE_SIZE
        
        if clicked_row < 3 and clicked_col < 3:  # Ensure click is within board
            if mark_square(clicked_row, clicked_col, 'O'):
                # Record player move
                record_player_move(clicked_row, clicked_col)
                
                # Check for win or draw
                winner = check_win()
                if winner or is_board_full():
                    game_over = True
                    update_game_stats()
                    analyze_game_patterns()
                    draw_game_over_overlay()
                
                # Switch turn
                player_turn = False
                return True
    
    return False

class GameSettings:
    def __init__(self):
        self.difficulty = 1
        self.search_depth = 5
        self.randomness = 0.1
        self.ai_delay = 0.5
        self.pattern_weight = 1.0

    def adjust_settings(self, game):
        if game == 'tictactoe':
            if self.difficulty == 0:  # Easy
                self.search_depth = 3
                self.randomness = 0.2
                self.ai_delay = 0.8
                self.pattern_weight = 0.8
            elif self.difficulty == 1:  # Medium
                self.search_depth = 5
                self.randomness = 0.1
                self.ai_delay = 0.5
                self.pattern_weight = 1.0
            elif self.difficulty == 2:  # Hard
                self.search_depth = 7
                self.randomness = 0.05
                self.ai_delay = 0.2
                self.pattern_weight = 1.2

        return {
            'search_depth': self.search_depth,
            'randomness': self.randomness,
            'ai_delay': self.ai_delay,
            'pattern_weight': self.pattern_weight
        }

    def calculate_thinking_time(self, game, move_count, complexity):
        if game == 'tictactoe':
            thinking_time = 0.5 + (move_count * 0.1) + (complexity * 0.2)
            return thinking_time

# Main game loop
calculate_dimensions(WIDTH, HEIGHT)  # Initialize dimensions
draw_welcome_screen()  # Start with welcome screen

# FPS control
clock = pygame.time.Clock()
FPS = 60

while True:
    clock.tick(FPS)  # Control frame rate
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Save game stats before quitting
            save_game_stats()
            save_pattern_data()
            pygame.quit()
            sys.exit()
            
        elif event.type == pygame.VIDEORESIZE:
            # Handle window resize
            handle_resize(event.w, event.h)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            if in_welcome_screen:
                handle_welcome_click(pos)
            elif in_game:
                # First check if clicked on buttons in the control panel
                if handle_button_click(pos):
                    continue
                
                # Then check for game board clicks
                handle_game_click(pos)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Restart game
                if in_game:
                    reset_game()
            
            elif event.key == pygame.K_ESCAPE:
                # Return to welcome screen
                in_welcome_screen = True
                in_game = False
                draw_welcome_screen()
            
            elif event.key == pygame.K_F11:
                # Toggle fullscreen
                pygame.display.toggle_fullscreen()
                # Update dimensions after toggling fullscreen
                WIDTH, HEIGHT = pygame.display.get_surface().get_size()
                calculate_dimensions(WIDTH, HEIGHT)
                
                # Redraw appropriate screen
                if in_welcome_screen:
                    draw_welcome_screen()
                else:
                    screen.fill(THEME["bg_primary"])
                    draw_board()
                    draw_figures()
                    draw_stats_panel()
                    draw_ai_selector()
                    
                    if game_over and show_results_overlay:
                        draw_game_over_overlay()
    
    # AI's turn
    if in_game and not game_over and not player_turn:
        # Add a small delay to make AI move visible
        pygame.display.update()
        pygame.time.delay(300)  # Slight delay before AI moves
        ai_move()
    
    pygame.display.update()