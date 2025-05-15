import random
from .math_challenge import MathChallenge
from .constants import GRID_WIDTH, GRID_HEIGHT
from .tetromino import Tetromino, SHAPES


class TetrisGame:
    def get_state_sync(self):
        # Return a dict representing the minimal state for remote sync
        return {
            'type': 'state_sync',
            'grid': self.grid,
            'score': self.score,
            'level': self.level,
            'lines_cleared': self.lines_cleared,
            'game_over': self.game_over,
            'player_name': self.player_name,
        }

    def apply_state_sync(self, state):
        # Update this game instance with remote state
        if not isinstance(state, dict):
            return
        if 'grid' in state:
            self.grid = [row[:] for row in state['grid']]
        if 'score' in state:
            self.score = state['score']
        if 'level' in state:
            self.level = state['level']
        if 'lines_cleared' in state:
            self.lines_cleared = state['lines_cleared']
        if 'game_over' in state:
            self.game_over = state['game_over']
        if 'player_name' in state:
            self.player_name = state['player_name']
    def __init__(self, player_name=None, difficulty_mode=None, multiplayer_mode=None):
        self.player_name = player_name
        self.difficulty_mode = difficulty_mode
        self.multiplayer_mode = multiplayer_mode
        self.network = None  # type: ignore  # Will be set by UI if multiplayer
        # Add missing attributes for test compatibility and correct initialization
        self.grid_width = GRID_WIDTH
        self.grid_height = GRID_HEIGHT
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.hold_piece = None
        self.hold_used = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5
        self.fall_time = 0
        self.piece_locked = False
        self.lock_delay = 0.5
        self.lock_timer = 0
        self.lock_pending = False
        self.move_left_pressed = False
        self.move_right_pressed = False
        self.move_down_pressed = False
        self.move_delay = 120
        self.move_interval = 50
        self.last_move_time = 0
        self.last_dir = 0
        self.pieces_since_question = 0
        self.soft_drop_interval = 0.07
        self.soft_drop_time = 0
        self.game_over = False
        self.state = "playing"
        self.math = MathChallenge(difficulty=1)
        self.correct_answers = 0
        self.math_feedback_time = 0
        self.feedback_message = ""
        self.feedback_color = (0, 255, 0)
        self.debug = False
    def handle_network_event(self, event):
        # Handle incoming network events
        if not isinstance(event, dict):
            return
        if event.get('type') == 'add_line':
            self.add_garbage_line()
        elif event.get('type') == 'state_sync':
            self.apply_state_sync(event)
        # Add more event types as needed
    def send_state_sync(self):
        # Send state to remote if networked
        if self.network:
            try:
                self.network.send_event(self.get_state_sync())
            except Exception as e:
                print(f"[TetrisGame] Failed to send state sync: {e}")

    def add_garbage_line(self):
        # Add a garbage line to the bottom, push everything up
        from .constants import GRAY
        empty_idx = random.randint(0, self.grid_width - 1)
        garbage = [GRAY if i != empty_idx else 0 for i in range(self.grid_width)]
        self.grid.pop(0)
        self.grid.append(garbage)

    def new_piece(self):
        shape = random.choice(SHAPES)
        return Tetromino(self.grid_width // 2 - len(shape[0]) // 2, 0, shape)

    def valid_move(self, piece, x, y, shape=None):
        if shape is None:
            shape = piece.shape
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    if (x + j < 0 or x + j >= self.grid_width or 
                        y + i >= self.grid_height or
                        (y + i >= 0 and self.grid[y + i][x + j])):
                        return False
        return True

    def add_to_grid(self, piece):
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    if piece.y + i >= 0:
                        self.grid[piece.y + i][piece.x + j] = piece.color

    def clear_lines(self):
        lines_to_clear = []
        for i, row in enumerate(self.grid):
            if all(cell != 0 for cell in row):
                lines_to_clear.append(i)
        for line in lines_to_clear:
            for y in range(line, 0, -1):
                self.grid[y] = self.grid[y-1][:]
            self.grid[0] = [0 for _ in range(self.grid_width)]
        num_lines = len(lines_to_clear)
        if num_lines > 0:
            self.lines_cleared += num_lines
            self.score += [100, 300, 500, 800][min(num_lines-1, 3)] * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
            self.update_difficulty()

    def update_difficulty(self):
        if self.level < 3:
            self.math.difficulty = 1
        elif self.level < 6:
            self.math.difficulty = 2
        elif self.level < 10:
            self.math.difficulty = 3
        else:
            self.math.difficulty = 4

    def reset_game(self):
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5
        self.correct_answers = 0
        self.math.reset()
        self.piece_locked = False
        self.hold_used = False
        self.pieces_since_question = 0
        self.state = "playing"
        self.math_feedback_time = 0
        self.feedback_message = ""
        self.feedback_color = (0, 255, 0)

    def trigger_math_challenge(self):
        self.math.reset()
        self.state = "math_challenge"
        self.piece_locked = True

    def move_piece(self, dx):
        if not self.piece_locked:
            new_x = self.current_piece.x + dx
            if self.valid_move(self.current_piece, new_x, self.current_piece.y):
                self.current_piece.x = new_x
                if self.lock_pending:
                    self.lock_timer = 0

    def soft_drop(self, dt=None):
        if self.piece_locked:
            return
        if dt is None:
            dt = self.soft_drop_interval
        self.soft_drop_time += dt
        if self.soft_drop_time >= self.soft_drop_interval:
            self.soft_drop_time = 0
            new_y = self.current_piece.y + 1
            if self.valid_move(self.current_piece, self.current_piece.x, new_y):
                self.current_piece.y = new_y
                self.lock_pending = False
                self.lock_timer = 0
            else:
                self.lock_pending = True

    def rotate_piece(self):
        # Prevent rotation if piece is locked (e.g., after hard drop)
        if self.piece_locked or self.current_piece.shape is None:
            return
        rotated_shape = self.current_piece.get_rotated_shape()
        kicks = [(0,0), (0,-1), (0,-2), (-1,0), (1,0)]
        for dx, dy in kicks:
            new_x = self.current_piece.x + dx
            new_y = self.current_piece.y + dy
            if self.valid_move(self.current_piece, new_x, new_y, rotated_shape):
                self.current_piece.shape = rotated_shape
                self.current_piece.rotation = (self.current_piece.rotation + 1) % 4
                self.current_piece.x = new_x
                self.current_piece.y = new_y
                if self.lock_pending:
                    self.lock_timer = 0
                break

    def hold_current_piece(self):
        if self.piece_locked or self.hold_used:
            return
        if self.hold_piece is None:
            self.hold_piece = self.current_piece
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
        else:
            self.hold_piece, self.current_piece = self.current_piece, self.hold_piece
            if self.current_piece.shape is not None:
                self.current_piece.x = self.grid_width // 2 - len(self.current_piece.shape[0]) // 2
                self.current_piece.y = 0
        self.hold_used = True
        self.lock_pending = False
        self.lock_timer = 0

    def lock_piece(self):
        self.hold_used = False
        self.update_difficulty()
        self.math.reset(self.math.difficulty)

    def set_state(self, new_state):
        if hasattr(self, 'state') and self.state == 'playing' and new_state != 'playing':
            self.move_left_pressed = False
            self.move_right_pressed = False
            self.move_down_pressed = False
        self.state = new_state

    def update(self, dt):
        if self.state == "game_over":
            return
        if self.state == "feedback":
            self.piece_locked = True
            self.math_feedback_time -= dt
            if self.math_feedback_time <= 0:
                self.set_state("playing")
                self.piece_locked = False
        elif self.state == "math_challenge":
            if self.difficulty_mode == 'master':
                self.piece_locked = False
                self.fall_time += dt
                if self.fall_time >= self.fall_speed:
                    self.fall_time = 0
                    if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y + 1):
                        self.current_piece.y += 1
                        self.lock_pending = False
                        self.lock_timer = 0
                    else:
                        self.lock_pending = True
                if self.lock_pending:
                    self.lock_timer += dt
                    if self.lock_timer >= self.lock_delay:
                        self.add_to_grid(self.current_piece)
                        self.clear_lines()
                        self.pieces_since_question += 1
                        self.current_piece = self.next_piece
                        self.next_piece = self.new_piece()
                        self.lock_pending = False
                        self.lock_timer = 0
                        if not self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y):
                            self.set_state("game_over")
                            self.game_over = True
            # else: in basic mode, piece is locked during math
        elif self.state == "playing":
            self.piece_locked = False
            self.fall_time += dt
            if self.fall_time >= self.fall_speed:
                self.fall_time = 0
                if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y + 1):
                    self.current_piece.y += 1
                    self.lock_pending = False
                    self.lock_timer = 0
                else:
                    self.lock_pending = True
            if self.move_down_pressed:
                self.soft_drop(dt)
            if self.lock_pending:
                self.lock_timer += dt
                if self.lock_timer >= self.lock_delay:
                    self.add_to_grid(self.current_piece)
                    self.clear_lines()
                    self.pieces_since_question += 1
                    self.current_piece = self.next_piece
                    self.next_piece = self.new_piece()
                    self.lock_pending = False
                    self.lock_timer = 0
                    if self.pieces_since_question >= 5:
                        self.trigger_math_challenge()
                        self.pieces_since_question = 0
            if not self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y):
                self.set_state("game_over")
                self.game_over = True

    def get_ghost_piece_position(self):
        piece = self.current_piece
        if not piece or not piece.shape:
            return piece.x, piece.y
        x, y = piece.x, piece.y
        while self.valid_move(piece, x, y + 1):
            y += 1
        return x, y

    def run_ui(self, ui):
        # This method is called by the UI loop for each frame
        dt = ui.clock.get_time() / 1000.0
        # Handle input events (UI should pass relevant events to TetrisGame)
        # Update game state
        self.update(dt)
        # Draw game (UI will handle actual drawing)
        # UI should call its own draw_game method, passing self as needed
        pass
