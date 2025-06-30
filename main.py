import pygame
import random
import sys
import time
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 800
BOARD_SIZE = 600
CELL_SIZE = BOARD_SIZE // 15
DICE_SIZE = 60
PLAYER_SIZE = 20
FPS = 60
BOARD_OFFSET_X = (WINDOW_SIZE - BOARD_SIZE ) // 2
BOARD_OFFSET_Y = (WINDOW_SIZE - BOARD_SIZE) // 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)        # Darker red
GREEN = (40, 180, 40)      # Darker green
BLUE = (30, 100, 200)      # Darker blue
YELLOW = (240, 200, 0)     # Darker yellow
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
WOOD_COLOR = (222, 184, 135)  # Wooden background color
WOOD_DARK = (160, 120, 80)    # Darker wood color for lines

# Path colors (lighter versions for better visibility on white)
PATH_COLORS = {
    0: (255, 200, 200),  # Light red
    1: (200, 255, 200),  # Light green
    2: (200, 200, 255),  # Light blue
    3: (255, 255, 200)   # Light yellow
}

# Board colors
HOME_COLORS = {
    0: {"border": RED, "fill": (255, 200, 200)},      # Red
    1: {"border": GREEN, "fill": (200, 255, 200)},    # Green
    2: {"border": BLUE, "fill": (200, 200, 255)},     # Blue
    3: {"border": YELLOW, "fill": (255, 255, 200)}    # Yellow
}

# Dice positions for each player
DICE_POSITIONS = {
    0: (0 + 20, 0 + 100),  # Red (right)
    1: (WINDOW_SIZE - DICE_SIZE - 20, 0 + 100),   # Green (top)
    2: (WINDOW_SIZE - DICE_SIZE - 20, WINDOW_SIZE - DICE_SIZE - 150),   # Blue (bottom left)
    3: (0 +20, WINDOW_SIZE - DICE_SIZE - 150),
}

# Game Statestar
WAITING_FOR_ROLL = "WAITING_FOR_ROLL"
WAITING_FOR_PIECE = "WAITING_FOR_PIECE"
PIECE_MOVING = "PIECE_MOVING"

# Set up display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Ludo Game")

# Board sections (in cells)
BOARD_CELLS = 15  # 15x15 grid
HOME_SIZE = 6     # 6x6 cells for each home
PATH_WIDTH = 3    # 3 cells wide for the main path

# Define the board layout
BOARD_LAYOUT = {
    'homes': {
        'red': (0, 0),                          # Top-left
        'green': (BOARD_CELLS - HOME_SIZE, 0),  # Top-right
        'blue': (BOARD_CELLS - HOME_SIZE, BOARD_CELLS - HOME_SIZE),  # Bottom-right
        'yellow': (0, BOARD_CELLS - HOME_SIZE)  # Bottom-left
    },
    'start_positions': {
        'red': (1, 6),      # Red starting position
        'green': (8, 1),    # Green starting position
        'blue': (13, 8),    # Blue starting position
        'yellow': (6, 13)   # Yellow starting position
    },
    'colors': {
        'red': {'main': RED, 'light': (255, 200, 200), 'path': (255, 220, 220)},
        'green': {'main': GREEN, 'light': (200, 255, 200), 'path': (220, 255, 220)},
        'blue': {'main': BLUE, 'light': (200, 200, 255), 'path': (220, 220, 255)},
        'yellow': {'main': YELLOW, 'light': (255, 255, 200), 'path': (255, 255, 220)}
    }
}

class Token:
    def __init__(self, x, y, color, index):
        self.start_pos = (x, y)
        self.pos = (x, y)
        self.color = color
        self.index = index
        self.is_home = False
        self.is_in_play = False
        self.steps_taken = 0
        self.selected = False

    def reset(self):
        self.pos = self.start_pos
        self.is_home = False
        self.is_in_play = False
        self.steps_taken = 0
        self.selected = False

    def move_to(self, x, y):
        self.pos = (x, y)

class DiceAnimation:
    def __init__(self):
        self.is_rolling = False
        self.start_time = 0
        self.duration = 1.0  # Animation duration in seconds
        self.frames = []
        self.current_frame = 0
        self.final_value = 1
        
        # Create dice face patterns
        self.dice_patterns = {
            1: [(DICE_SIZE//2, DICE_SIZE//2)],
            2: [(DICE_SIZE//4, DICE_SIZE//4), (3*DICE_SIZE//4, 3*DICE_SIZE//4)],
            3: [(DICE_SIZE//4, DICE_SIZE//4), (DICE_SIZE//2, DICE_SIZE//2), (3*DICE_SIZE//4, 3*DICE_SIZE//4)],
            4: [(DICE_SIZE//4, DICE_SIZE//4), (3*DICE_SIZE//4, DICE_SIZE//4),
                (DICE_SIZE//4, 3*DICE_SIZE//4), (3*DICE_SIZE//4, 3*DICE_SIZE//4)],
            5: [(DICE_SIZE//4, DICE_SIZE//4), (3*DICE_SIZE//4, DICE_SIZE//4),
                (DICE_SIZE//2, DICE_SIZE//2),
                (DICE_SIZE//4, 3*DICE_SIZE//4), (3*DICE_SIZE//4, 3*DICE_SIZE//4)],
            6: [(DICE_SIZE//4, DICE_SIZE//4), (3*DICE_SIZE//4, DICE_SIZE//4),
                (DICE_SIZE//4, DICE_SIZE//2), (3*DICE_SIZE//4, DICE_SIZE//2),
                (DICE_SIZE//4, 3*DICE_SIZE//4), (3*DICE_SIZE//4, 3*DICE_SIZE//4)]
        }

    def start_roll(self, final_value):
        self.is_rolling = True
        self.start_time = time.time()
        self.final_value = final_value
        self.current_frame = 0

    def draw(self, screen, x, y):
        if self.is_rolling:
            current_time = time.time() - self.start_time
            if current_time > self.duration:
                self.is_rolling = False
                value = self.final_value
            else:
                value = random.randint(1, 6)
                self.current_frame = (self.current_frame + 1) % 6
        else:
            value = self.final_value

        # Draw dice background
        pygame.draw.rect(screen, WHITE, (x, y, DICE_SIZE, DICE_SIZE))
        pygame.draw.rect(screen, BLACK, (x, y, DICE_SIZE, DICE_SIZE), 2)

        # Draw dots
        for dot_pos in self.dice_patterns[value]:
            pygame.draw.circle(screen, BLACK,
                             (x + dot_pos[0], y + dot_pos[1]),
                             DICE_SIZE//10)

class LudoGame:
    def __init__(self):
        self.current_player = 0
        self.state = WAITING_FOR_ROLL
        self.consecutive_sixes = 0
        self.game_message = ""
        self.dice_roll_time = 0
        self.testing_mode = False
        self.path_checking_test = False 
        self.test_move_delay = 0.5  # Delay between automatic moves (seconds)
        self.last_test_move_time = 0
        
        # Initialize tokens for each player in their home positions
        self.tokens = {
            0: [Token(1, 1, RED, i) for i in range(4)],      # Red player (left)
            1: [Token(10, 1, GREEN, i) for i in range(4)],   # Green player (top)
            2: [Token(10, 10, BLUE, i) for i in range(4)],   # Blue player (right)
            3: [Token(1, 10, YELLOW, i) for i in range(4)]   # Yellow player (bottom)
        }
        
        # Position each token in a 2x2 grid within their home area
        for player, tokens in self.tokens.items():
            base_x = 1 if player in [0, 3] else 10  # Left side for Red/Yellow, Right side for Green/Blue
            base_y = 1 if player in [0, 1] else 10  # Top for Red/Green, Bottom for Blue/Yellow
            
            for i, token in enumerate(tokens):
                x = base_x + (i % 2) * 3  # Alternate between base_x and base_x + 3
                y = base_y + (i // 2) * 3  # First two tokens on first row, next two on second row
                token.pos = (x, y)
                token.start_pos = (x, y)
        
        self.dice_value = 1
        self.dice_rolled = False
        self.dice_animation = DiceAnimation()
        
        # Define safe squares (stars and starting positions)
        self.safe_squares = [
            (1, 6),   # Red starting position (left)
            (8, 1),   # Green starting position (top)
            (13, 8),  # Blue starting position (right)
            (6, 13)   # Yellow starting position (bottom)
        ]
        
        # Define paths for each player
        self.main_path = self._create_main_path()
        self.home_paths = self._create_home_paths()

        # For testing: Put tokens at specific positions for each player
        if self.testing_mode:
            # Test positions for each player
            test_positions = {
                0: [],  # Red player positions
                1: [],  # Green player positions
                2: [],  # Blue player positions
                3: []   # Yellow player positions
            }
            
            # Place tokens at test positions
            for player, positions in test_positions.items():
                for i, pos in enumerate(positions):
                    token = self.tokens[player][i]
                    token.move_to(pos[0], pos[1])
                    token.is_in_play = True
                    token.steps_taken = i  # Set steps taken based on position

    def _create_main_path(self):
        # Define the complete path for each player
        paths = {
            0: [  # Red path (from left)
                (1, 6), (2, 6), (3, 6), (4, 6), (5, 6),   # Start to center
                (6, 5), (6, 4), (6, 3), (6, 2), (6, 1), (6, 0), (7, 0), (8, 0),  # Up to green start
                (8, 1), (8, 2), (8, 3), (8, 4), (8, 5),  # Down to center
                (9, 6), (10, 6), (11, 6), (12, 6), (13, 6), (14, 6), (14, 7), (14, 8),  # Right to blue start
                (13, 8), (12, 8), (11, 8), (10, 8), (9, 8),  # Left to center
                (8, 9), (8, 10), (8, 11), (8, 12), (8, 13), (8, 14),  # Down to yellow start
                (7, 14), (6, 14),  # Left to center
                (6, 13), (6, 12), (6, 11), (6, 10), (6, 9),  # Up to center
                (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8),  # Left to home
                (0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7)  # Right into home
            ],
            1: [  # Green path (from top)
                (8, 1), (8, 2), (8, 3), (8, 4), (8, 5),  # Start to center
                (9, 6), (10, 6), (11, 6), (12, 6), (13, 6), (14, 6), (14, 7), (14, 8),  # Right to blue start
                (13, 8), (12, 8), (11, 8), (10, 8), (9, 8),  # Left to center
                (8, 9), (8, 10), (8, 11), (8, 12), (8, 13), (8, 14),  # Down to yellow start
                (7, 14), (6, 14),  # Left to center
                (6, 13), (6, 12), (6, 11), (6, 10), (6, 9),  # Up to center
                (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8), (0, 7),(0,6),(1, 6),  # Left to red start
                (2, 6), (3, 6), (4, 6), (5, 6),  # Right to center
                (6, 5), (6, 4), (6, 3), (6, 2), (6, 1), (6, 0),  # Up to home
                (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6)  # Down into home
            ],
            2: [  # Blue path (from right)
                (13, 8), (12, 8), (11, 8), (10, 8), (9, 8),  # Start to center
                (8, 9), (8, 10), (8, 11), (8, 12), (8, 13), (8, 14),  # Down to yellow start
                (7, 14), (6, 14),  # Left to center
                (6, 13), (6, 12), (6, 11), (6, 10), (6, 9),  # Up to center
                (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8), (0, 7),(0,6),(1, 6),  # Left to red start
                (2, 6), (3, 6), (4, 6), (5, 6),  # Right to center
                (6, 5), (6, 4), (6, 3), (6, 2), (6, 1), (6, 0), (7, 0), (8, 0),  # Up to green start
                (8, 1), (8, 2), (8, 3), (8, 4), (8, 5),  # Down to center
                (9, 6), (10, 6), (11, 6), (12, 6), (13, 6), (14, 6),  # Right to home
                (14, 7), (13, 7), (12, 7), (11, 7), (10, 7), (9, 7), (8, 7)  # Left into home
            ],
            3: [  # Yellow path (from bottom)
                (6, 13), (6, 12), (6, 11), (6, 10), (6, 9),  # Start to center
                (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8), (0, 7),(0, 6),(1, 6),  # Left to red start
                (2, 6), (3, 6), (4, 6), (5, 6),  # Right to center
                (6, 5), (6, 4), (6, 3), (6, 2), (6, 1), (6, 0), (7, 0), (8, 0),  # Up to green start
                (8, 1), (8, 2), (8, 3), (8, 4), (8, 5),  # Down to center
                (9, 6), (10, 6), (11, 6), (12, 6), (13, 6), (14, 6), (14, 7), (14, 8),  # Right to blue start
                (13, 8), (12, 8), (11, 8), (10, 8), (9, 8),  # Left to center
                (8, 9), (8, 10), (8, 11), (8, 12), (8, 13), (8, 14),  # Down to home
                (7, 14), (7, 13), (7, 12), (7, 11), (7, 10), (7, 9), (7, 8)  # Up into home
            ]
        }
        return paths

    def _create_home_paths(self):
        # Final paths to reach home
        return {
            0: [(1, 6)],  # Red final home (bottom-right of center)
            1: [(8, 1)],  # Green final home (top-right of center)
            2: [(13, 8)],  # Blue final home (bottom-left of center)
            3: [(6, 13)]   # Yellow final home (top-left of center)
        }

    def is_safe_square(self, pos):
        return pos in self.safe_squares

    def can_move_token(self, token, steps):
        # If token is already home, it can't move
        if token.is_home:
            return False
            
        # If token is not in play and roll is 6, it can move
        if not token.is_in_play and steps == 6:
            return True
            
        # If token is in play, check if move would be valid
        if token.is_in_play:
            current_path = self.main_path[self.current_player]
            current_index = 0
            
            # Find current position in path
            for i, pos in enumerate(current_path):
                if pos == token.pos:
                    current_index = i
                    break
            
            new_index = current_index + steps
            
            # Check if move would go beyond home path
            if new_index >= len(current_path):
                home_path = self.home_paths[self.current_player]
                steps_into_home = new_index - len(current_path)
                return steps_into_home < len(home_path)
            
            return True
            
        return False

    def get_token_at_position(self, pos):
        for player in self.tokens.values():
            for token in player:
                if token.pos == pos:
                    return token
        return None

    def move_token(self, token, steps):
        # If token is not in play and roll is 6, move to starting position
        if not token.is_in_play and steps == 6:
            start_pos = self.main_path[self.current_player][0]
            token.move_to(start_pos[0], start_pos[1])
            token.is_in_play = True
            token.steps_taken = 0
            # Update game state
            self.dice_rolled = False
            self.dice_animation.is_rolling = False
            self.check_capture(token)
            return True

        # If token is already in play, move it along the path
        if token.is_in_play:
            current_path = self.main_path[self.current_player]
            current_index = 0
            
            # Find current position in path
            for i, pos in enumerate(current_path):
                if pos == token.pos:
                    current_index = i
                    break
            
            # Calculate new position
            new_index = current_index + steps
            
            # Check if token can enter home path
            if new_index >= len(current_path):
                home_path = self.home_paths[self.current_player]
                steps_into_home = new_index - len(current_path)
                
                if steps_into_home < len(home_path):
                    new_pos = home_path[steps_into_home]
                    token.move_to(new_pos[0], new_pos[1])
                    token.steps_taken = len(current_path) + steps_into_home
                    # Update game state
                    self.dice_rolled = False
                    self.dice_animation.is_rolling = False
                    if steps_into_home == len(home_path) - 1:
                        token.is_home = True
                    self.check_capture(token)
                    return True
            else:
                new_pos = current_path[new_index]
                token.move_to(new_pos[0], new_pos[1])
                token.steps_taken = new_index
                # Update game state
                self.dice_rolled = False
                self.dice_animation.is_rolling = False
                self.check_capture(token)
                return True
                
        return False

    def check_capture(self, token):
        # Check if there are any opponent tokens at the new position
        if token.pos in self.safe_squares:  # No capture on safe squares
            return
            
        for player, tokens in self.tokens.items():
            if player != self.current_player:  # Only check opponent tokens
                for other_token in tokens:
                    if other_token.pos == token.pos and other_token.is_in_play:
                        # Send opponent token back home
                        other_token.reset()
                        return True
        return False

    def get_player_name(self, player_index):
        colors = ["Red", "Green", "Blue", "Yellow"]
        return colors[player_index]

    def check_winner(self):
        for player_idx, tokens in self.tokens.items():
            if all(token.is_home for token in tokens):
                return player_idx
        return None

    def draw_corner_split_cell(self, screen, x, y, position):
        # Convert grid coordinates to pixel coordinates
        pixel_x = BOARD_OFFSET_X + x * CELL_SIZE
        pixel_y = BOARD_OFFSET_Y + y * CELL_SIZE
        
        if position == "top_left":  # (0,0) - split between red and green
            points1 = [(pixel_x, pixel_y),
                      (pixel_x + CELL_SIZE, pixel_y),
                      (pixel_x, pixel_y + CELL_SIZE)]
            points2 = [(pixel_x + CELL_SIZE, pixel_y),
                      (pixel_x + CELL_SIZE, pixel_y + CELL_SIZE),
                      (pixel_x, pixel_y + CELL_SIZE)]
            color1 = HOME_COLORS[1]["fill"]  # Green (top)
            color2 = HOME_COLORS[2]["fill"]  # blue (left)
        elif position == "top_right":  # (2,0) - split between green and blue
            points1 = [(pixel_x, pixel_y),
                      (pixel_x + CELL_SIZE, pixel_y),
                      (pixel_x + CELL_SIZE, pixel_y + CELL_SIZE)]
            points2 = [(pixel_x, pixel_y),
                      (pixel_x, pixel_y + CELL_SIZE),
                      (pixel_x + CELL_SIZE, pixel_y + CELL_SIZE)]
            color1 = HOME_COLORS[1]["fill"]  # Green (top)
            color2 = HOME_COLORS[0]["fill"]  # red (right)
        elif position == "bottom_left":  # (0,2) - split between red and yellow
            points1 = [(pixel_x, pixel_y),
                      (pixel_x + CELL_SIZE, pixel_y),
                      (pixel_x + CELL_SIZE, pixel_y + CELL_SIZE)]
            points2 = [(pixel_x, pixel_y),
                      (pixel_x, pixel_y + CELL_SIZE),
                      (pixel_x + CELL_SIZE, pixel_y + CELL_SIZE)]
            color1 = HOME_COLORS[2]["fill"]  # Red (left)
            color2 = HOME_COLORS[3]["fill"]  # Yellow (bottom)
        else:  # "bottom_right" (2,2) - split between blue and yellow
            points1 = [(pixel_x + CELL_SIZE, pixel_y),
                      (pixel_x + CELL_SIZE, pixel_y + CELL_SIZE),
                      (pixel_x, pixel_y + CELL_SIZE)]
            points2 = [(pixel_x + CELL_SIZE, pixel_y),
                      (pixel_x, pixel_y),
                      (pixel_x, pixel_y + CELL_SIZE)]
            color1 = HOME_COLORS[3]["fill"]  # Blue (right)
            color2 = HOME_COLORS[0]["fill"]  # Yellow (bottom)
        
        # Draw the two triangles
        pygame.draw.polygon(screen, color1, points1)
        pygame.draw.polygon(screen, color2, points2)
        
        # Draw the cell border
        pygame.draw.rect(screen, BLACK, (pixel_x, pixel_y, CELL_SIZE, CELL_SIZE), 1)

    def draw_four_way_split_cell(self, screen, x, y):
        # Convert grid coordinates to pixel coordinates
        pixel_x = BOARD_OFFSET_X + x * CELL_SIZE
        pixel_y = BOARD_OFFSET_Y + y * CELL_SIZE
        center_x = pixel_x + CELL_SIZE // 2
        center_y = pixel_y + CELL_SIZE // 2
        
        # Define the four triangles (top, right, bottom, left)
        top_triangle = [(center_x, center_y),
                       (pixel_x, pixel_y),
                       (pixel_x + CELL_SIZE, pixel_y)]
        
        right_triangle = [(center_x, center_y),
                         (pixel_x + CELL_SIZE, pixel_y),
                         (pixel_x + CELL_SIZE, pixel_y + CELL_SIZE)]
        
        bottom_triangle = [(center_x, center_y),
                          (pixel_x + CELL_SIZE, pixel_y + CELL_SIZE),
                          (pixel_x, pixel_y + CELL_SIZE)]
        
        left_triangle = [(center_x, center_y),
                        (pixel_x, pixel_y + CELL_SIZE),
                        (pixel_x, pixel_y)]
        
        # Draw the four triangles with corresponding home colors
        pygame.draw.polygon(screen, HOME_COLORS[1]["fill"], top_triangle)     # Top (Green)
        pygame.draw.polygon(screen, HOME_COLORS[2]["fill"], right_triangle)   # Right (Blue)
        pygame.draw.polygon(screen, HOME_COLORS[3]["fill"], bottom_triangle)  # Bottom (Yellow)
        pygame.draw.polygon(screen, HOME_COLORS[0]["fill"], left_triangle)    # Left (Red)
        
        # Draw the cell border
        pygame.draw.rect(screen, BLACK, (pixel_x, pixel_y, CELL_SIZE, CELL_SIZE), 1)

    def draw_board(self):
        # Fill background
        screen.fill(WOOD_COLOR)
        
        # Draw the main board area with border
        pygame.draw.rect(screen, WHITE,
                        (BOARD_OFFSET_X - 5, BOARD_OFFSET_Y - 5,
                         BOARD_SIZE + 10, BOARD_SIZE + 10))
        pygame.draw.rect(screen, BLACK,
                        (BOARD_OFFSET_X - 5, BOARD_OFFSET_Y - 5,
                         BOARD_SIZE + 10, BOARD_SIZE + 10), 2)

        # Draw colored home areas (squares)
        home_positions = {
            0: (0, 0, RED),                    # Red (top-left)
            1: (9, 0, GREEN),                  # Green (top-right)
            2: (9, 9, BLUE),                   # Blue (bottom-right)
            3: (0, 9, YELLOW)                  # Yellow (bottom-left)
        }

        # Draw home areas
        for player, (x, y, color) in home_positions.items():
            # Draw 6x6 colored square for home
            rect = (BOARD_OFFSET_X + x * CELL_SIZE,
                   BOARD_OFFSET_Y + y * CELL_SIZE,
                   CELL_SIZE * 6, CELL_SIZE * 6)
            pygame.draw.rect(screen, HOME_COLORS[player]["fill"], rect)
            pygame.draw.rect(screen, HOME_COLORS[player]["border"], rect, 2)

            # Draw 2x2 grid for token positions
            for i in range(2):
                for j in range(2):
                    # Calculate exact center of each cell in the 2x2 grid
                    circle_x = BOARD_OFFSET_X + (x + 1 + i * 3) * CELL_SIZE + (CELL_SIZE // 2)
                    circle_y = BOARD_OFFSET_Y + (y + 1 + j * 3) * CELL_SIZE + (CELL_SIZE // 2)
                    
                    # Draw white background circle
                    pygame.draw.circle(screen, WHITE, (circle_x, circle_y), CELL_SIZE // 3)
                    # Draw colored border
                    pygame.draw.circle(screen, color, (circle_x, circle_y), CELL_SIZE // 3, 2)
                    # Draw inner colored circle
                    pygame.draw.circle(screen, color, (circle_x, circle_y), CELL_SIZE // 6)

        # Draw center paths (white cross)
        center_paths = [
            (6, 0, 3, 15),  # Vertical path
            (0, 6, 15, 3)   # Horizontal path
        ]
        
        for x, y, w, h in center_paths:
            rect = (BOARD_OFFSET_X + x * CELL_SIZE,
                   BOARD_OFFSET_Y + y * CELL_SIZE,
                   w * CELL_SIZE, h * CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, WOOD_DARK, rect, 1)

        # Draw colored paths leading to center
        colored_center_paths = {
            0: [(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (1, 6)],  # Red path (left)
            1: [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (8, 1)],  # Green path (top)
            2: [(13, 7), (12, 7), (11, 7), (10, 7), (9, 7), (13, 8)],  # Blue path (right)
            3: [(7, 13), (7, 12), (7, 11), (7, 10), (7, 9), (6, 13)]   # Yellow path (bottom)
        }

        # Draw the colored paths to center
        for player, path in colored_center_paths.items():
            for x, y in path:
                rect = (BOARD_OFFSET_X + x * CELL_SIZE,
                       BOARD_OFFSET_Y + y * CELL_SIZE,
                       CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, HOME_COLORS[player]["fill"], rect)
                pygame.draw.rect(screen, HOME_COLORS[player]["border"], rect, 1)

        # Draw center home squares with diagonal split pattern
        # First draw white background for center area
        center_rect = (BOARD_OFFSET_X + 6 * CELL_SIZE,
                      BOARD_OFFSET_Y + 6 * CELL_SIZE,
                      CELL_SIZE * 3, CELL_SIZE * 3)
        pygame.draw.rect(screen, WHITE, center_rect)

        # Draw the center 3x3 grid
        for i in range(3):
            for j in range(3):
                x = 6 + i  # Center starts at x=6
                y = 6 + j  # Center starts at y=6
                pixel_x = BOARD_OFFSET_X + x * CELL_SIZE
                pixel_y = BOARD_OFFSET_Y + y * CELL_SIZE
                
                # Single cells with different patterns
                if (i, j) == (0, 1):  # Left middle cell
                    pygame.draw.rect(screen, HOME_COLORS[0]["fill"], 
                                   (pixel_x, pixel_y, CELL_SIZE, CELL_SIZE))
                elif (i, j) == (1, 0):  # Top middle cell
                    pygame.draw.rect(screen, HOME_COLORS[1]["fill"], 
                                   (pixel_x, pixel_y, CELL_SIZE, CELL_SIZE))
                elif (i, j) == (2, 1):  # Right middle cell
                    pygame.draw.rect(screen, HOME_COLORS[2]["fill"], 
                                   (pixel_x, pixel_y, CELL_SIZE, CELL_SIZE))
                elif (i, j) == (1, 2):  # Bottom middle cell
                    pygame.draw.rect(screen, HOME_COLORS[3]["fill"], 
                                   (pixel_x, pixel_y, CELL_SIZE, CELL_SIZE))
                elif (i, j) == (1, 1):  # Center cell - four-way split
                    self.draw_four_way_split_cell(screen, x, y)
                elif (i, j) == (0, 0):  # Top-left corner
                    self.draw_corner_split_cell(screen, x, y, "top_right")
                elif (i, j) == (2, 0):  # Top-right corner
                    self.draw_corner_split_cell(screen, x, y, "top_left")
                elif (i, j) == (0, 2):  # Bottom-left corner
                    self.draw_corner_split_cell(screen, x, y, "bottom_right")
                elif (i, j) == (2, 2):  # Bottom-right corner
                    self.draw_corner_split_cell(screen, x, y, "bottom_left")
                
                # Draw cell border
                pygame.draw.rect(screen, BLACK, 
                               (pixel_x, pixel_y, CELL_SIZE, CELL_SIZE), 1)

        # Draw grid lines
        for i in range(16):
            # Vertical lines
            pygame.draw.line(screen, WOOD_DARK,
                           (BOARD_OFFSET_X + i * CELL_SIZE, BOARD_OFFSET_Y),
                           (BOARD_OFFSET_X + i * CELL_SIZE, BOARD_OFFSET_Y + BOARD_SIZE))
            # Horizontal lines
            pygame.draw.line(screen, WOOD_DARK,
                           (BOARD_OFFSET_X, BOARD_OFFSET_Y + i * CELL_SIZE),
                           (BOARD_OFFSET_X + BOARD_SIZE, BOARD_OFFSET_Y + i * CELL_SIZE))

        # Draw player icons in corners
        icon_size = CELL_SIZE * 2
        icon_positions = [
            (BOARD_OFFSET_X + CELL_SIZE * 2, BOARD_OFFSET_Y + CELL_SIZE * 2),  # Red
            (BOARD_OFFSET_X + BOARD_SIZE - CELL_SIZE * 4, BOARD_OFFSET_Y + CELL_SIZE * 2),  # Green
            (BOARD_OFFSET_X + BOARD_SIZE - CELL_SIZE * 4, BOARD_OFFSET_Y + BOARD_SIZE - CELL_SIZE * 4),  # Blue
            (BOARD_OFFSET_X + CELL_SIZE * 2, BOARD_OFFSET_Y + BOARD_SIZE - CELL_SIZE * 4)  # Yellow
        ]

    def draw_tokens(self):
        for player, tokens in self.tokens.items():
            for token in tokens:
                # Calculate exact center position of the cell
                screen_x = BOARD_OFFSET_X + (token.pos[0] * CELL_SIZE) + (CELL_SIZE // 2)
                screen_y = BOARD_OFFSET_Y + (token.pos[1] * CELL_SIZE) + (CELL_SIZE // 2)
                
                if token.is_home:
                    # Draw home token with different appearance (grayed out)
                    pygame.draw.circle(screen, LIGHT_GRAY, (screen_x, screen_y), CELL_SIZE // 3)
                    pygame.draw.circle(screen, GRAY, (screen_x, screen_y), CELL_SIZE // 3, 2)
                    pygame.draw.circle(screen, GRAY, (screen_x, screen_y), CELL_SIZE // 6)
                else:
                    border_color = HOME_COLORS[player]["border"]
                    if not token.is_in_play:
                        # Draw token not in play with a cross pattern
                        pygame.draw.circle(screen, WHITE, (screen_x, screen_y), CELL_SIZE // 3)
                        pygame.draw.circle(screen, border_color, (screen_x, screen_y), CELL_SIZE // 3, 2)
                        # Draw an X pattern inside
                        size = CELL_SIZE // 4
                        pygame.draw.line(screen, border_color, 
                                       (screen_x - size, screen_y - size),
                                       (screen_x + size, screen_y + size), 2)
                        pygame.draw.line(screen, border_color,
                                       (screen_x + size, screen_y - size),
                                       (screen_x - size, screen_y + size), 2)
                    else:
                        # Draw normal token in play
                        pygame.draw.circle(screen, WHITE, (screen_x, screen_y), CELL_SIZE // 3)
                        pygame.draw.circle(screen, border_color, (screen_x, screen_y), CELL_SIZE // 3, 2)
                        pygame.draw.circle(screen, border_color, (screen_x, screen_y), CELL_SIZE // 6)
                    
                    # If token is selected, draw highlight
                    if token.selected:
                        pygame.draw.circle(screen, LIGHT_GRAY, (screen_x, screen_y), CELL_SIZE // 2.5, 3)

    def draw_dice(self):
        try:
            # Get dice position based on current player
            dice_x, dice_y = DICE_POSITIONS[self.current_player]
            
            # Draw player indicator around dice
            padding = 10
            pygame.draw.rect(screen, self.tokens[self.current_player][0].color,
                           (dice_x - padding, dice_y - padding,
                            DICE_SIZE + 2*padding, DICE_SIZE + 2*padding))
            pygame.draw.rect(screen, BLACK,
                           (dice_x - padding, dice_y - padding,
                            DICE_SIZE + 2*padding, DICE_SIZE + 2*padding), 2)
            
            self.dice_animation.draw(screen, dice_x, dice_y)

            # Draw "Roll" text below dice when waiting for roll
            if self.state == WAITING_FOR_ROLL and not self.dice_animation.is_rolling:
                font = pygame.font.Font(None, 24)
                text1 = font.render("Click to", True, BLACK)
                text2 = font.render("Roll!", True, BLACK)
                text_rect1 = text1.get_rect(center=(dice_x + DICE_SIZE//2, dice_y + DICE_SIZE + 35))
                text_rect2 = text2.get_rect(center=(dice_x + DICE_SIZE//2, dice_y + DICE_SIZE + 55))
                screen.blit(text1, text_rect1)
                screen.blit(text2, text_rect2)

        except Exception as e:
            print(f"Error drawing dice: {e}")
            pygame.quit()
            sys.exit(1)

    def roll_dice(self):
        if not self.dice_animation.is_rolling:
            if self.testing_mode:
                if self.path_checking_test:
                    # In path checking test, always succeed
                    self.dice_value = 6 if not any(t.is_in_play for t in self.tokens[self.current_player]) else 1
                else:
                    # Regular test mode
                    self.dice_value = 1
            else:
                self.dice_value = random.randint(1, 6)
            
            self.dice_animation.start_roll(self.dice_value)
            self.dice_rolled = True
            self.dice_roll_time = time.time()
            
            if self.dice_value == 6:
                self.consecutive_sixes += 1
                if self.consecutive_sixes == 3:
                    self.game_message = "Three sixes in a row! Turn forfeited!"
                    self.next_turn()
                else:
                    self.game_message = "Rolled a 6! You get another turn after moving."
                self.state = WAITING_FOR_PIECE
            else:
                self.consecutive_sixes = 0
                self.state = "SHOWING_ROLL"

    def update_game_state(self):
        current_time = time.time()
        
        # Path checking test mode: automatically move tokens along their paths
        if self.testing_mode and self.path_checking_test:
            if current_time - self.last_test_move_time >= self.test_move_delay:
                self.last_test_move_time = current_time
                self.auto_test_move()
                return

        # Regular game state updates
        if self.state == "SHOWING_ROLL" and current_time - self.dice_roll_time >= 2:
            can_move = False
            for token in self.tokens[self.current_player]:
                if self.can_move_token(token, self.dice_value):
                    can_move = True
                    break
            
            if not can_move:
                self.game_message = "No valid moves available!"
                self.next_turn()
            else:
                self.state = WAITING_FOR_PIECE

    def next_turn(self):
        self.current_player = (self.current_player + 1) % 4
        self.dice_rolled = False
        self.consecutive_sixes = 0
        self.state = WAITING_FOR_ROLL
        
        # Deselect all tokens
        for tokens in self.tokens.values():
            for token in tokens:
                token.selected = False

    def handle_click(self, pos):
        if self.state == WAITING_FOR_ROLL:
            # Check if dice was clicked
            dice_rect = pygame.Rect(
                DICE_POSITIONS[self.current_player][0],
                DICE_POSITIONS[self.current_player][1],
                DICE_SIZE,
                DICE_SIZE
            )
            if dice_rect.collidepoint(pos):
                return self.roll_dice()
            return False

        elif self.state == WAITING_FOR_PIECE:
            # Convert mouse position to board coordinates
            board_x = (pos[0] - BOARD_OFFSET_X) // CELL_SIZE
            board_y = (pos[1] - BOARD_OFFSET_Y) // CELL_SIZE
            click_pos = (board_x, board_y)

            # Check if any token was clicked
            for token in self.tokens[self.current_player]:
                if token.is_home:
                    continue  # Skip tokens that have reached home
                
                token_screen_x = BOARD_OFFSET_X + (token.pos[0] * CELL_SIZE) + (CELL_SIZE // 2)
                token_screen_y = BOARD_OFFSET_Y + (token.pos[1] * CELL_SIZE) + (CELL_SIZE // 2)
                
                # Check if click is within token radius
                click_distance = math.sqrt(
                    (pos[0] - token_screen_x) ** 2 +
                    (pos[1] - token_screen_y) ** 2
                )
                
                if click_distance <= PLAYER_SIZE:
                    if self.can_move_token(token, self.dice_value):
                        # Deselect all other tokens
                        for other_token in self.tokens[self.current_player]:
                            other_token.selected = False
                        # Select this token
                        token.selected = True
                        # Move the token
                        if self.move_token(token, self.dice_value):
                            # If moved successfully, check for game end
                            if all(t.is_home for t in self.tokens[self.current_player]):
                                self.game_message = f"Player {self.current_player} wins!"
                                return True
                            # If rolled 6, player gets another turn
                            if self.dice_value == 6:
                                self.state = WAITING_FOR_ROLL
                            else:
                                self.next_turn()
                            return True
            return False

        return False

    def auto_test_move(self):
        """Automatically move tokens to test paths"""
        # Get the current player's first token
        token = self.tokens[self.current_player][0]
        
        if not token.is_in_play:
            # If token is not in play, put it at the starting position
            start_pos = self.main_path[self.current_player][0]
            token.move_to(start_pos[0], start_pos[1])
            token.is_in_play = True
            token.steps_taken = 0
            self.game_message = f"Player {self.current_player} token placed at start: {start_pos}"
        else:
            # Move token one step along the path
            current_path = self.main_path[self.current_player]
            current_index = 0
            
            # Find current position in path
            for i, pos in enumerate(current_path):
                if pos == token.pos:
                    current_index = i
                    break
            
            # Move to next position
            next_index = current_index + 1
            
            if next_index >= len(current_path):
                # Move into home path
                home_path = self.home_paths[self.current_player]
                steps_into_home = next_index - len(current_path)
                
                if steps_into_home < len(home_path):
                    new_pos = home_path[steps_into_home]
                    token.move_to(new_pos[0], new_pos[1])
                    token.steps_taken = len(current_path) + steps_into_home
                    self.game_message = f"Player {self.current_player} token at home path: {new_pos}"
                    if steps_into_home == len(home_path) - 1:
                        token.is_home = True
                        self.game_message = f"Player {self.current_player} token reached home!"
                        self.next_turn()  # Move to next player when token reaches home
                else:
                    # Token completed its path, move to next player
                    self.next_turn()
            else:
                # Move along main path
                new_pos = current_path[next_index]
                token.move_to(new_pos[0], new_pos[1])
                token.steps_taken = next_index
                self.game_message = f"Player {self.current_player} token at: {new_pos}"

def main():
    try:
        game = LudoGame()
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    game.handle_click(event.pos)

            # Update game state
            game.update_game_state()

            # Draw game state
            game.draw_board()
            game.draw_tokens()
            game.draw_dice()

            # Display current player and game message
            font = pygame.font.Font(None, 36)
            player_text = f"{game.get_player_name(game.current_player)}'s turn"
            text = font.render(player_text, True, game.tokens[game.current_player][0].color)
            screen.blit(text, (10, 10))
            
            if game.game_message:
                msg_text = font.render(game.game_message, True, BLACK)
                screen.blit(msg_text, (10, 50))

            pygame.display.flip()
            clock.tick(FPS)

    except Exception as e:
        print(f"Game error: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main() 