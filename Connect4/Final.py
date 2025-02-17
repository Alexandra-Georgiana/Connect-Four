import numpy as np
import math
import random
import copy
import pygame
import os

from config import *

pygame.init()
pygame.mixer.init()

menu_sound = pygame.mixer.Sound("Elements/Sound/Menu_sound.mp3")
game_sound = pygame.mixer.Sound("Elements/Sound/Game_sound.mp3")
select = pygame.mixer.Sound("Elements/Sound/Select.wav")
drop = pygame.mixer.Sound("Elements/Sound/Drop.mp3")
win = pygame.mixer.Sound("Elements/Sound/Win.mp3")

pygame.mixer.set_num_channels(4)

def Board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    if board[0][col] == 0:
        return True
    return False

def get_next_open_row(board, col):
    for r in range(ROW_COUNT-1, -1, -1):
        if board[r][col] == 0:
            return r

def is_winning_move(board, piece):
    # vertically
    for col in range (COLUMN_COUNT):
        for row in range(ROW_COUNT-3):
            if board[row][col] == piece and board[row+1][col] == piece and board[row+2][col] == piece and board[row+3][col] == piece:
                return True

    # horizontally
    for col in range(COLUMN_COUNT-3):
        for row in range(ROW_COUNT):
            if board[row][col] == piece and board[row][col+1] == piece and board[row][col+2] == piece and board[row][col+3] == piece:
                return True

    # diagonal 1
    for col in range (COLUMN_COUNT-3):
        for row in range(ROW_COUNT-3):
            if board[row][col] == piece and board[row+1][col+1] == piece and board[row+2][col+2] == piece and board[row+3][col+3] == piece:
                return True

    # diagonal 2
    for col in range (COLUMN_COUNT-3):
        for row in range(3, ROW_COUNT):
            if board[row][col] == piece and board[row-1][col+1] == piece and board[row-2][col+2] == piece and board[row-3][col+3] == piece:
                return True

def is_terminal(board):
    return is_winning_move(board, 1) or is_winning_move(board, 2) or len(get_valid_locations(board)) == 0

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0

    ## Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    ## Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score posiive sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return is_winning_move(board, PLAYER_PIECE) or is_winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if is_winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif is_winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def pick_best_move(board, piece):

    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col

def run_p_vs_p():
    game_over = False
    board = Board()
    turn = 0

    while not game_over:
        if turn == 0:
            col = int(input("Player 1 make your selection (0-6): "))

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 1)
                if is_winning_move(board, 1):
                    print("Player 1 wins!")
                    game_over = True
        else:
            col = int(input("Player 2 make your selection (0-6): "))

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)
                if is_winning_move(board, 2):
                    print("Player 2 wins!")
                    game_over = True

        print(board)

        turn += 1
        turn = turn % 2

def run_p_vs_ai():
    game_over = False
    board = Board()
    turn = 0

    while not game_over:
        if turn == 0:
            col = int(input("Player make your selection (0-6): "))

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, PLAYER_PIECE)
                if is_winning_move(board, PLAYER_PIECE):
                    print("Player wins!")
                    game_over = True
        else:
            col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)
                if is_winning_move(board, AI_PIECE):
                    print("AI wins!")
                    game_over = True

        print(board)

        turn += 1
        turn = turn % 2


# Game variables
board = np.zeros((ROWS, COLS), dtype=int)
turn = 1
game_mode = None  # None, "PvP", or "PvAI"
game_over = False

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Connect 4 - Animated Menu")
font = pygame.font.Font(None, 30)

# Buttons
BUTTON_WIDTH, BUTTON_HEIGHT = 220, 70
button_pvp = pygame.Rect((WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 - 90), (BUTTON_WIDTH, BUTTON_HEIGHT))
button_ai = pygame.Rect((WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 + 20), (BUTTON_WIDTH, BUTTON_HEIGHT))

def run_animation():
    global game_mode

    channel = pygame.mixer.Channel(1)
    channel.play(menu_sound)
    channel.set_volume(0.1)

    # Load images
    layer_names = ["Background", "Sky", "Soil", "Weed", "Trunks", "Dark crowns", "Light crowns", "Normal petals", "Light petals", "Inversed petals"]
    layers = {name: pygame.image.load(os.path.join("Elements/C4", f"{name}.PNG")) for name in layer_names}

    # Resize images to fit screen
    for name in layers:
        layers[name] = pygame.transform.scale(layers[name], (WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    running = True

    # Animation variables
    wind_offset = 0.0
    wind_target = 3.0  # Maximum sway
    wind_speed = 0.02  # Controls smoothness

    # Petal positions (moving rightward)
    petal_positions = {
        "Normal petals": [(-100, 10)],
        "Light petals": [(-60, 20)],
        "Inversed petals": [(-10, 30)]
    }

    last_petal_time = pygame.time.get_ticks()

    def animate_petal(petal_list):
        """Moves petals rightward and resets when out of bounds."""
        for i in range(len(petal_list)):
            x, y = petal_list[i]
            x += 1
            y += int(1.3 * math.sin(x / 50.0))
            if x > WIDTH:
                x = random.randint(-200, -60)
            petal_list[i] = (x, y)

    def draw_button(rect, text, is_pressed):
        color = PASTEL_PINK if not is_pressed else PASTEL_PURPLE
        if rect.collidepoint(pygame.mouse.get_pos()) and not is_pressed:
            color = DARK_PINK

        pygame.draw.rect(screen, (230, 150, 160), (rect.x, rect.y + 5, rect.width, rect.height), border_radius=12)
        pygame.draw.rect(screen, color, rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, rect, 3, border_radius=12)

        text_surface = font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(rect.centerx, rect.centery))
        screen.blit(text_surface, text_rect)

    while running:
        screen.fill(WHITE)

        # Smooth wind effect
        wind_offset += (wind_target - wind_offset) * wind_speed
        if abs(wind_offset - wind_target) < 0.5:
            wind_target *= -1

        # Draw animated layers
        screen.blit(layers["Background"], (0, 0))
        screen.blit(layers["Sky"], (0, 0))
        screen.blit(layers["Soil"], (0, 0))
        screen.blit(layers["Weed"], (0, 0))
        screen.blit(layers["Trunks"], (0, 0))
        screen.blit(layers["Dark crowns"], (-wind_offset, 0))
        screen.blit(layers["Light crowns"], (wind_offset, 0))

        # Generate new petals every 2 seconds
        current_time = pygame.time.get_ticks()
        if current_time - last_petal_time > random.randint(8000, 15000):
            for petal_layer in petal_positions:
                petal_positions[petal_layer].append((random.randint(-200, -60), random.randint(-100, 100)))
            last_petal_time = current_time

        for petal_layer, positions in petal_positions.items():
            animate_petal(positions)
            for pos in positions:
                screen.blit(layers[petal_layer], pos)

        # Draw buttons
        mouse_pressed = pygame.mouse.get_pressed()
        draw_button(button_pvp, "Player vs Player", mouse_pressed[0] and button_pvp.collidepoint(pygame.mouse.get_pos()))
        draw_button(button_ai, "Player vs AI", mouse_pressed[0] and button_ai.collidepoint(pygame.mouse.get_pos()))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                channel = pygame.mixer.Channel(2)
                channel.play(select)
                channel.set_volume(1.0)
                if button_pvp.collidepoint(event.pos):
                    game_mode = "PvP"
                    print("Starting Player vs Player mode")
                    running = False
                elif button_ai.collidepoint(event.pos):
                    game_mode = "PvAI"
                    print("Starting Player vs AI mode")
                    running = False

        pygame.display.flip()
        clock.tick(120)

    return game_mode

def draw_board(board):
    # menu_sound.stop()
    # game_sound.play()
    # game_sound.set_volume(0.1)
    screen.fill(WHITE)
    pygame.draw.rect(screen, PASTEL_PURPLE, (0, TOP_SPACE, WIDTH, HEIGHT - TOP_SPACE))
    for row in range(ROWS):
        for col in range(COLS):
            pygame.draw.circle(screen, PASTEL_PINK,
                               (col * SQUARE_SIZE + 15 + SQUARE_SIZE//2, row * SQUARE_SIZE + 100 + SQUARE_SIZE//2),
                               RADIUS)

            if board[row][col] == 1:
                pygame.draw.circle(screen, PLAYER1_COLOR,
                                   (col * SQUARE_SIZE + 15 + SQUARE_SIZE//2, row * SQUARE_SIZE + 100 + SQUARE_SIZE//2),
                                   RADIUS)
            elif board[row][col] == 2:
                pygame.draw.circle(screen, PLAYER2_COLOR,
                                   (col * SQUARE_SIZE + 15 + SQUARE_SIZE//2, row * SQUARE_SIZE + 100 + SQUARE_SIZE//2),
                                   RADIUS)

    pygame.display.update()

def play_pygame():
    """Runs the game after mode selection, supporting both PvP and PvAI modes."""
    global game_mode, turn, game_over

    game_mode = run_animation()  # Show animated menu first
    game_board = Board()

    running = True
    while running:
        screen.fill(WHITE)  # Clear the entire screen
        channel = pygame.mixer.Channel(3)

        # Event handling
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                channel = pygame.mixer.Channel(0)
                col = (event.pos[0] - 15) // SQUARE_SIZE
                if 0 <= col < COLS:
                    row = get_next_open_row(game_board, col)
                    if row is not None:
                        drop_piece(game_board, row, col, turn)
                        channel.play(drop)
                        channel.set_volume(1.0)
                        draw_board(game_board)  # Redraw board after piece drop

                        if is_winning_move(game_board, turn):
                            channel.play(win)
                            channel.set_volume(1.0)
                            text = font.render(f"Player {turn} wins!", True, PLAYER1_COLOR if turn == 1 else PLAYER2_COLOR)
                            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 10))
                            pygame.display.update()
                            pygame.time.delay(2000)  # Show win message for 2 seconds
                            game_over = True

                        turn = 3 - turn  # Switch turn


        if game_mode == "PvAI" and turn == AI_PIECE and not game_over:
            pygame.time.delay(500)
            col, minimax_score = minimax(game_board, 5, -math.inf, math.inf, True)
            if col is not None:
                row = get_next_open_row(game_board, col)
                if row is not None:
                    drop_piece(game_board, row, col, AI_PIECE)
                    channel.play(drop)
                    channel.set_volume(1.0)
                    draw_board(game_board)

                    if is_winning_move(game_board, AI_PIECE):
                        channel.play(win)
                        channel.set_volume(1.0)
                        text = font.render("AI wins!", True, WIN_TEXT_COLOR)
                        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 10))
                        pygame.display.update()
                        pygame.time.delay(2000)
                        game_over = True

                    turn = 1

        draw_board(game_board)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    play_pygame()