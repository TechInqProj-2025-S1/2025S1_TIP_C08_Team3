import pygame
from .constants import (
    BG_COLOR, PRIMARY_COLOR, ACCENT_COLOR, WHITE, BLACK, TEXT_COLOR, get_fonts
)
from .tetris import TetrisGame

class Button:
    def __init__(self, rect, text, color, hover_color, font, text_color=BLACK):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = font
        self.text_color = text_color
        self.hovered = False
    def draw(self, surface):
        pygame.draw.rect(surface, self.hover_color if self.hovered else self.color, self.rect, border_radius=10)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

class TetrisMathUI:
    def __init__(self, screen_width=None, screen_height=None, fullscreen=True, borderless=False):
        import os
        import json
        pygame.init()
        info = pygame.display.Info()
        # Try to read launcher config for display settings
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
        launcher_display = None
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                launcher_display = config.get("launcher", {}).get("display", None)
            except Exception:
                launcher_display = None
        if launcher_display:
            screen_width = launcher_display.get("width", info.current_w)
            screen_height = launcher_display.get("height", info.current_h)
            borderless = launcher_display.get("borderless", True)
        if screen_width is None:
            screen_width = info.current_w
        if screen_height is None:
            screen_height = info.current_h
        self.screen_width, self.screen_height = screen_width, screen_height
        if borderless:
            flags = pygame.NOFRAME
        else:
            flags = pygame.FULLSCREEN if fullscreen else 0
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), flags)
        pygame.display.set_caption("Tetris Math")
        self.clock = pygame.time.Clock()
        self.state = 'menu'  # menu, playing, game_over
        self.name = ''
        self.difficulty = None
        self.menu_buttons = []
        self.init_menu_buttons()
        self.tetris_game = None
        self.running = True
    def init_menu_buttons(self):
        fonts = get_fonts()
        font = fonts['BODY_FONT']
        sw, sh = self.screen_width, self.screen_height
        self.basic_btn = Button((sw//2-180, sh//2-60, 150, 60), "Basic", (144, 213, 101), (110, 180, 80), font, text_color=WHITE)  # #90d565
        self.master_btn = Button((sw//2+30, sh//2-60, 150, 60), "Master", (185, 84, 225), (140, 50, 180), font, text_color=WHITE)  # #b954e1
        self.multi_btn = Button((sw//2-75, sh//2+20, 150, 60), "Multiplayer", (52, 152, 219), (41, 128, 185), font, text_color=WHITE)
        self.back_btn = Button((sw//2-90, sh//2+100, 180, 44), "Back to Menu", (52, 152, 219), (41, 128, 185), font, text_color=WHITE)
        self.menu_buttons = [self.basic_btn, self.master_btn, self.multi_btn, self.back_btn]
    def run(self):
        from .constants import ACCENT_COLOR, WARNING_COLOR
        import random
        while self.running:
            self.clock.tick(60)
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_click = True
                # Handle custom event for network connection
                if event.type == pygame.USEREVENT and hasattr(event, 'custom_type') and event.custom_type == 'start_multiplayer_game':
                    self._start_multiplayer_game()
                if self.state == 'menu':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            self.name = self.name[:-1]
                        elif len(self.name) < 12 and event.unicode.isprintable():
                            self.name += event.unicode
                        elif event.key == pygame.K_RETURN and self.name and self.difficulty:
                            self.start_game()
                elif self.state == 'waiting':
                    # Host: show waiting overlay, no input
                    pass
                elif self.state == 'connecting':
                    # Client: show connecting overlay, no input
                    pass
                elif self.state == 'playing':
                    if self.tetris_game:
                        if event.type == pygame.KEYDOWN:
                            if self.tetris_game.state == 'math_challenge':
                                if event.unicode.isdigit():
                                    self.tetris_game.math.add_digit(event.unicode)
                                elif event.key == pygame.K_BACKSPACE:
                                    self.tetris_game.math.remove_digit()
                                elif event.key == pygame.K_RETURN:
                                    if self.tetris_game.math.user_answer:
                                        correct = self.tetris_game.math.check_answer(self.tetris_game.math.user_answer)
                                        if correct:
                                            self.tetris_game.correct_answers += 1
                                            object.__setattr__(self.tetris_game, 'feedback_message', "Correct!")
                                            object.__setattr__(self.tetris_game, 'feedback_color', ACCENT_COLOR)
                                            self.tetris_game.state = "feedback"
                                            self.tetris_game.math_feedback_time = 1.2
                                            # Multiplayer: send add_line to opponent
                                            if self.multiplayer_mode and self.network:
                                                try:
                                                    self.network.send_event({"type": "add_line"})
                                                except Exception as e:
                                                    print(f"[TetrisMathUI] Failed to send add_line: {e}")
                                        else:
                                            object.__setattr__(self.tetris_game, 'feedback_message', f"Wrong! Answer: {self.tetris_game.math.answer}")
                                            object.__setattr__(self.tetris_game, 'feedback_color', WARNING_COLOR)
                                            self.tetris_game.state = "feedback"
                                            self.tetris_game.math_feedback_time = 1.2
                                            # Multiplayer: add line to self
                                            if self.multiplayer_mode and self.network:
                                                try:
                                                    self.tetris_game.add_garbage_line()
                                                except Exception as e:
                                                    print(f"[TetrisMathUI] Failed to add garbage line: {e}")
                                            # Drop the piece randomly
                                            piece = self.tetris_game.current_piece
                                            grid_w = self.tetris_game.grid_width
                                            if piece.shape is not None:
                                                piece_width = len(piece.shape[0])
                                                valid_xs = []
                                                for x in range(grid_w - piece_width + 1):
                                                    if self.tetris_game.valid_move(piece, x, 0):
                                                        valid_xs.append(x)
                                                if valid_xs:
                                                    piece.x = random.choice(valid_xs)
                                                    piece.y = 0
                                                    while self.tetris_game.valid_move(piece, piece.x, piece.y + 1):
                                                        piece.y += 1
                                                    self.tetris_game.add_to_grid(piece)
                                                    self.tetris_game.clear_lines()
                                                    self.tetris_game.current_piece = self.tetris_game.next_piece
                                                    self.tetris_game.next_piece = self.tetris_game.new_piece()
                                                    self.tetris_game.pieces_since_question += 1
                                                    self.tetris_game.lock_pending = False
                                                    self.tetris_game.lock_timer = 0
                                                    if not self.tetris_game.valid_move(self.tetris_game.current_piece, self.tetris_game.current_piece.x, self.tetris_game.current_piece.y):
                                                        self.tetris_game.set_state("game_over")
                                                        self.tetris_game.game_over = True
                            elif self.tetris_game.state == 'playing':
                                if event.key in (pygame.K_LEFT, pygame.K_a):
                                    self.tetris_game.move_left_pressed = True
                                    self.tetris_game.last_move_time = pygame.time.get_ticks()
                                    self.tetris_game.last_dir = -1
                                    self.tetris_game.move_piece(-1)
                                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                                    self.tetris_game.move_right_pressed = True
                                    self.tetris_game.last_move_time = pygame.time.get_ticks()
                                    self.tetris_game.last_dir = 1
                                    self.tetris_game.move_piece(1)
                                elif event.key in (pygame.K_DOWN, pygame.K_s):
                                    self.tetris_game.move_down_pressed = True
                                    self.tetris_game.soft_drop()
                                elif event.key in (pygame.K_UP, pygame.K_w):
                                    self.tetris_game.rotate_piece()
                                    self.tetris_game.last_move_time = pygame.time.get_ticks()
                                elif event.key == pygame.K_SPACE:
                                    # Hard drop: move piece to bottom, then lock it and prevent further rotation
                                    while self.tetris_game.valid_move(self.tetris_game.current_piece, self.tetris_game.current_piece.x, self.tetris_game.current_piece.y + 1):
                                        self.tetris_game.current_piece.y += 1
                                        self.tetris_game.score += 1
                                    # After hard drop, lock the piece and prevent further movement/rotation
                                    self.tetris_game.piece_locked = True
                                    self.tetris_game.lock_pending = True
                                    self.tetris_game.lock_timer = self.tetris_game.lock_delay
                                elif event.key in (pygame.K_c, pygame.K_LSHIFT, pygame.K_RSHIFT):
                                    self.tetris_game.hold_current_piece()
                                elif event.key == pygame.K_ESCAPE:
                                    self.state = 'menu'
                                    self.tetris_game = None
                                elif event.key == pygame.K_r and self.tetris_game.game_over:
                                    self.start_game()
                        elif event.type == pygame.KEYUP:
                            if self.tetris_game.state == 'playing':
                                if event.key in (pygame.K_LEFT, pygame.K_a):
                                    self.tetris_game.move_left_pressed = False
                                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                                    self.tetris_game.move_right_pressed = False
                                elif event.key in (pygame.K_DOWN, pygame.K_s):
                                    self.tetris_game.move_down_pressed = False
                elif self.state == 'game_over':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.start_game()
            if self.state == 'menu':
                self.draw_menu(mouse_pos, mouse_click)
            elif self.state == 'waiting':
                self.draw_waiting_overlay(mouse_pos, mouse_click)
            elif self.state == 'connecting':
                self.draw_connecting_overlay(mouse_pos, mouse_click)
            elif self.state == 'playing':
                if self.tetris_game:
                    self.tetris_game.run_ui(self)
                    # Send state sync after update
                    if self.multiplayer_mode and self.network:
                        self.tetris_game.send_state_sync()
                    self.draw_game()
                    if self.tetris_game.game_over:
                        self.state = 'game_over'
            elif self.state == 'game_over':
                self.draw_game_over(mouse_pos, mouse_click)
            pygame.display.flip()

    def draw_waiting_overlay(self, mouse_pos, mouse_click):
        sw, sh = self.screen_width, self.screen_height
        fonts = get_fonts()
        self.screen.fill(BG_COLOR)
        msg = fonts['TITLE_FONT'].render("Waiting for player to join...", True, PRIMARY_COLOR)
        self.screen.blit(msg, (sw//2 - msg.get_width()//2, sh//2 - 60))
        instr = fonts['BODY_FONT'].render("Share your IP/port and wait for a connection.", True, TEXT_COLOR)
        self.screen.blit(instr, (sw//2 - instr.get_width()//2, sh//2 + 10))
        # Cancel button for host
        cancel_btn_rect = (sw//2 - 100, sh//2 + 80, 200, 50)
        if not hasattr(self, 'cancel_wait_btn') or self.cancel_wait_btn is None:
            font = fonts['BODY_FONT']
            self.cancel_wait_btn = Button(cancel_btn_rect, "Cancel", ACCENT_COLOR, PRIMARY_COLOR, font, text_color=BLACK)
        self.cancel_wait_btn.rect.topleft = (sw//2 - 100, sh//2 + 80)
        self.cancel_wait_btn.update(mouse_pos)
        self.cancel_wait_btn.draw(self.screen)
        if self.cancel_wait_btn.is_clicked(mouse_pos, mouse_click):
            # Clean up network if needed
            if hasattr(self, 'network') and self.network:
                try:
                    self.network.close()
                except Exception:
                    pass
                self.network = None
            self.state = 'menu'
            self.multiplayer_mode = None
            self.tetris_game = None
            self.remote_tetris_game = None

    def draw_connecting_overlay(self, mouse_pos, mouse_click):
        sw, sh = self.screen_width, self.screen_height
        fonts = get_fonts()
        self.screen.fill(BG_COLOR)
        msg = fonts['TITLE_FONT'].render("Connecting to host...", True, ACCENT_COLOR)
        self.screen.blit(msg, (sw//2 - msg.get_width()//2, sh//2 - 60))
        instr = fonts['BODY_FONT'].render("Waiting for host to accept connection.", True, TEXT_COLOR)
        self.screen.blit(instr, (sw//2 - instr.get_width()//2, sh//2 + 10))
        # Cancel button
        cancel_btn_rect = (sw//2 - 100, sh//2 + 80, 200, 50)
        if not hasattr(self, 'cancel_connect_btn') or self.cancel_connect_btn is None:
            font = fonts['BODY_FONT']
            self.cancel_connect_btn = Button(cancel_btn_rect, "Cancel", ACCENT_COLOR, PRIMARY_COLOR, font, text_color=BLACK)
        self.cancel_connect_btn.rect.topleft = (sw//2 - 100, sh//2 + 80)
        self.cancel_connect_btn.update(mouse_pos)
        self.cancel_connect_btn.draw(self.screen)
        if self.cancel_connect_btn.is_clicked(mouse_pos, mouse_click):
            # Clean up network if needed
            if hasattr(self, 'network') and self.network:
                try:
                    self.network.close()
                except Exception:
                    pass
                self.network = None
            self.state = 'menu'
            self.multiplayer_mode = None
            self.tetris_game = None
            self.remote_tetris_game = None
    def draw_menu(self, mouse_pos, mouse_click):
        self.screen.fill(BG_COLOR)
        sw, sh = self.screen_width, self.screen_height
        fonts = get_fonts()
        # Layout parameters
        center_x = sw // 2
        y = int(sh * 0.13)
        spacing = 48
        # Title
        title = fonts['TITLE_FONT'].render("Tetris Math", True, PRIMARY_COLOR)
        self.screen.blit(title, (center_x - title.get_width() // 2, y))
        y += title.get_height() + spacing
        # Name prompt
        prompt = fonts['BODY_FONT'].render("Enter your name:", True, TEXT_COLOR)
        self.screen.blit(prompt, (center_x - prompt.get_width() // 2, y))
        y += prompt.get_height() + 10
        # Name input box
        input_box_width, input_box_height = 320, 50
        input_box = pygame.Rect(center_x - input_box_width // 2, y, input_box_width, input_box_height)
        pygame.draw.rect(self.screen, WHITE, input_box, 2, border_radius=8)
        name_surface = fonts['BODY_FONT'].render(self.name, True, BLACK)
        name_rect = name_surface.get_rect(center=input_box.center)
        self.screen.blit(name_surface, name_rect)
        y += input_box_height + 18
        # Difficulty prompt
        diff_text = fonts['SCORE_FONT'].render("Choose difficulty:", True, TEXT_COLOR)
        self.screen.blit(diff_text, (center_x - diff_text.get_width() // 2, y))
        y += diff_text.get_height() + 10
        # Difficulty buttons (side by side, centered)
        btn_w, btn_h = 140, 50
        btn_gap = 32
        bx = center_x - btn_w - btn_gap // 2
        by = y
        self.basic_btn.rect.topleft = (bx, by)
        self.master_btn.rect.topleft = (center_x + btn_gap // 2, by)
        self.basic_btn.rect.size = (btn_w, btn_h)
        self.master_btn.rect.size = (btn_w, btn_h)
        self.basic_btn.update(mouse_pos)
        self.master_btn.update(mouse_pos)
        self.basic_btn.draw(self.screen)
        self.master_btn.draw(self.screen)
        # Highlight selected
        if self.difficulty == 'basic':
            pygame.draw.rect(self.screen, (0,255,0), self.basic_btn.rect, 4, border_radius=10)
        elif self.difficulty == 'master':
            pygame.draw.rect(self.screen, (155,89,182), self.master_btn.rect, 4, border_radius=10)
        y += btn_h + 18
        # Multiplayer button (centered)
        self.multi_btn.rect.topleft = (center_x - btn_w // 2, y)
        self.multi_btn.rect.size = (btn_w, btn_h)
        self.multi_btn.update(mouse_pos)
        self.multi_btn.draw(self.screen)
        y += btn_h + 18
        # Back button (centered)
        # Make back button a bit longer to cover the text
        back_btn_w = 180
        self.back_btn.rect.topleft = (center_x - back_btn_w // 2, y)
        self.back_btn.rect.size = (back_btn_w, btn_h)
        self.back_btn.update(mouse_pos)
        self.back_btn.draw(self.screen)
        # Handle clicks
        if self.basic_btn.is_clicked(mouse_pos, mouse_click):
            self.difficulty = 'basic'
        if self.master_btn.is_clicked(mouse_pos, mouse_click):
            self.difficulty = 'master'
        if self.multi_btn.is_clicked(mouse_pos, mouse_click):
            self.show_multiplayer_mode_prompt()
        if self.back_btn.is_clicked(mouse_pos, mouse_click):
            self.running = False
        # Instruction
        y += btn_h + 10
        instr = fonts['SCORE_FONT'].render("Press Enter to start", True, TEXT_COLOR)
        self.screen.blit(instr, (center_x - instr.get_width() // 2, y))

    def show_multiplayer_mode_prompt(self):
        # Modal for Host/Join selection, then show waiting/connecting overlay
        running = True
        sw, sh = self.screen_width, self.screen_height
        fonts = get_fonts()
        font = fonts['BODY_FONT']
        host_btn = Button((sw//2-180, sh//2, 150, 60), "Host", (52, 152, 219), (41, 128, 185), font, text_color=WHITE)
        join_btn = Button((sw//2+30, sh//2, 150, 60), "Join", (52, 152, 219), (41, 128, 185), font, text_color=WHITE)
        while running:
            self.screen.fill(BG_COLOR)
            modal_rect = pygame.Rect(sw//2-220, sh//2-100, 440, 220)
            pygame.draw.rect(self.screen, WHITE, modal_rect, border_radius=16)
            pygame.draw.rect(self.screen, PRIMARY_COLOR, modal_rect, 4, border_radius=16)
            title = fonts['TITLE_FONT'].render("Multiplayer Mode", True, PRIMARY_COLOR)
            self.screen.blit(title, (sw//2-title.get_width()//2, sh//2-80))
            host_btn.update(pygame.mouse.get_pos())
            join_btn.update(pygame.mouse.get_pos())
            host_btn.draw(self.screen)
            join_btn.draw(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if host_btn.is_clicked(pygame.mouse.get_pos(), True):
                        self.multiplayer_mode = 'host'
                        self.state = 'waiting'
                        self._start_multiplayer_connection('host')
                        return
                    if join_btn.is_clicked(pygame.mouse.get_pos(), True):
                        self.multiplayer_mode = 'join'
                        self.state = 'connecting'
                        self._start_multiplayer_connection('join')
                        return
            pygame.display.flip()

    def _start_multiplayer_connection(self, mode):
        import os
        import json
        config_path = os.path.join(os.getcwd(), "config.json")
        with open(config_path, "r") as f:
            config = json.load(f)
        tetris_cfg = config.get("games", {}).get("tetris_math_multiplayer", {})
        host_ip = tetris_cfg.get("host_ip", "127.0.0.1")
        host_port = int(tetris_cfg.get("host_port", 5000))
        from .network import TetrisNetwork
        def on_connect():
            self._on_multiplayer_connected()
        self.network = TetrisNetwork(mode, host_ip, host_port, on_event=self.on_network_event, on_connect=on_connect)
        try:
            self.network.start()
        except Exception as e:
            print(f"[TetrisMathUI] Network error: {e}")
            self.network = None
            self.state = 'menu'

    def _on_multiplayer_connected(self):
        # Called from network thread when connection is established
        # Switch to main thread for UI/game start
        import threading
        if threading.current_thread() is not threading.main_thread():
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'custom_type': 'start_multiplayer_game'}))
        else:
            self._start_multiplayer_game()

    def _start_multiplayer_game(self):
        self.tetris_game = TetrisGame(player_name=self.name, difficulty_mode=self.difficulty, multiplayer_mode=self.multiplayer_mode)
        if self.network:
            self.tetris_game.network = self.network  # type: ignore
        # Prepare for 2P: create a second TetrisGame for the remote player (stub for now)
        self.remote_tetris_game = TetrisGame(player_name="Player 2", difficulty_mode=self.difficulty, multiplayer_mode=self.multiplayer_mode)
        self.state = 'playing'
    def start_game(self, multiplayer_mode=None):
        self.multiplayer_mode = multiplayer_mode
        self.network = None
        # Load multiplayer config if needed
        if multiplayer_mode in ('host', 'join'):
            import os
            import json
            config_path = os.path.join(os.getcwd(), "config.json")
            with open(config_path, "r") as f:
                config = json.load(f)
            tetris_cfg = config.get("games", {}).get("tetris_math_multiplayer", {})
            host_ip = tetris_cfg.get("host_ip", "127.0.0.1")
            host_port = int(tetris_cfg.get("host_port", 5000))
            from .network import TetrisNetwork
            self.network = TetrisNetwork(multiplayer_mode, host_ip, host_port, on_event=self.on_network_event)
            try:
                self.network.start()
            except Exception as e:
                print(f"[TetrisMathUI] Network error: {e}")
                self.network = None
                # TODO: Show error overlay/UI
        self.tetris_game = TetrisGame(player_name=self.name, difficulty_mode=self.difficulty, multiplayer_mode=multiplayer_mode)
        self.remote_tetris_game = None
        if self.network:
            self.tetris_game.network = self.network  # type: ignore
        self.state = 'playing'

    def on_network_event(self, event):
        # Called from network thread when an event is received
        # If it's a state_sync, update remote_tetris_game; else, pass to local game
        if isinstance(event, dict) and event.get('type') == 'state_sync':
            if self.remote_tetris_game:
                self.remote_tetris_game.apply_state_sync(event)
        elif self.tetris_game:
            self.tetris_game.handle_network_event(event)
    def draw_game(self):
        if not self.tetris_game:
            return
        from .constants import GRAY
        sw, sh = self.screen_width, self.screen_height
        grid_height = self.tetris_game.grid_height
        grid_width = self.tetris_game.grid_width
        # 2P: side by side grids
        n_players = 2 if self.remote_tetris_game else 1
        grid_gap = 80
        grid_size = min(int(sh * 0.8) // grid_height, (sw - grid_gap) // (n_players * grid_width))
        grid_total_w = grid_width * grid_size
        grid_total_h = grid_height * grid_size
        base_left = (sw - (n_players * grid_total_w + (n_players - 1) * grid_gap)) // 2
        grid_tops = [max(60, (sh - grid_total_h) // 2)] * n_players
        grid_lefts = [base_left + i * (grid_total_w + grid_gap) for i in range(n_players)]
        self.screen.fill(BG_COLOR)
        fonts = get_fonts()
        # Draw both grids
        for pidx, game in enumerate([self.tetris_game, self.remote_tetris_game] if self.remote_tetris_game else [self.tetris_game]):
            if not game:
                continue
            grid_left = grid_lefts[pidx]
            grid_top = grid_tops[pidx]
            # Label
            label = fonts['SCORE_FONT'].render(f"{'1P' if pidx == 0 else '2P'}: {game.player_name or ('You' if pidx == 0 else 'Remote')}", True, PRIMARY_COLOR if pidx == 0 else ACCENT_COLOR)
            self.screen.blit(label, (grid_left + (grid_total_w - label.get_width()) // 2, grid_top - 40))
            # Grid
            for y in range(grid_height):
                for x in range(grid_width):
                    pygame.draw.rect(self.screen, GRAY,
                                     (grid_left + x * grid_size,
                                      grid_top + y * grid_size,
                                      grid_size, grid_size), 1)
                    if game.grid[y][x]:
                        pygame.draw.rect(self.screen, game.grid[y][x],
                                         (grid_left + x * grid_size + 1,
                                          grid_top + y * grid_size + 1,
                                          grid_size - 2, grid_size - 2))
            # Only draw local player's piece/ghost
            if pidx == 0:
                piece = game.current_piece
                if piece and piece.shape:
                    ghost_x, ghost_y = game.get_ghost_piece_position()
                    ghost_color = piece.color
                    ghost_surface = pygame.Surface((grid_size, grid_size), pygame.SRCALPHA)
                    ghost_surface.fill((*ghost_color[:3], 70))
                    for i, row in enumerate(piece.shape):
                        for j, cell in enumerate(row):
                            if cell:
                                gx = grid_left + (ghost_x + j) * grid_size + 1
                                gy = grid_top + (ghost_y + i) * grid_size + 1
                                self.screen.blit(ghost_surface, (gx, gy))
                # Draw current piece (on top of ghost)
                if piece and piece.shape:
                    for i, row in enumerate(piece.shape):
                        for j, cell in enumerate(row):
                            if cell:
                                pygame.draw.rect(self.screen, piece.color,
                                                 (grid_left + (piece.x + j) * grid_size + 1,
                                                  grid_top + (piece.y + i) * grid_size + 1,
                                                  grid_size - 2, grid_size - 2))
            # Sidebar (only for local player)
            if pidx == 0:
                sidebar_left = grid_left + grid_total_w + 40
                sidebar_top = grid_top
                sidebar_w = min(320, sw - sidebar_left - 40)
                sidebar_h = grid_total_h
                sidebar_rect = pygame.Rect(sidebar_left, sidebar_top, sidebar_w, sidebar_h)
                pygame.draw.rect(self.screen, WHITE, sidebar_rect, border_radius=18)
                pygame.draw.rect(self.screen, PRIMARY_COLOR, sidebar_rect, 3, border_radius=18)
                y_offset = sidebar_top + 30
                spacing = 50
                score_text = fonts['SCORE_FONT'].render(f"Score: {game.score}", True, TEXT_COLOR)
                self.screen.blit(score_text, (sidebar_left + (sidebar_w - score_text.get_width()) // 2, y_offset))
                y_offset += spacing
                level_text = fonts['SCORE_FONT'].render(f"Level: {game.level}", True, TEXT_COLOR)
                self.screen.blit(level_text, (sidebar_left + (sidebar_w - level_text.get_width()) // 2, y_offset))
                y_offset += spacing
                lines_text = fonts['SCORE_FONT'].render(f"Lines: {game.lines_cleared}", True, TEXT_COLOR)
                self.screen.blit(lines_text, (sidebar_left + (sidebar_w - lines_text.get_width()) // 2, y_offset))
                y_offset += spacing
                math_score_text = fonts['SCORE_FONT'].render(f"Math Answers: {game.correct_answers}", True, TEXT_COLOR)
                self.screen.blit(math_score_text, (sidebar_left + (sidebar_w - math_score_text.get_width()) // 2, y_offset))
        # Overlays for local player
        if self.tetris_game.state == "math_challenge":
            self.draw_math_overlay()
        elif self.tetris_game.state == "feedback":
            self.draw_feedback_overlay()

    def draw_math_overlay(self):
        if not self.tetris_game:
            return
        sw, sh = self.screen_width, self.screen_height
        modal_w, modal_h = min(500, sw * 0.6), min(220, sh * 0.3)
        modal_x = (sw - modal_w) // 2
        modal_y = (sh - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
        pygame.draw.rect(self.screen, WHITE, modal_rect, border_radius=16)
        pygame.draw.rect(self.screen, PRIMARY_COLOR, modal_rect, 4, border_radius=16)
        fonts = get_fonts()
        eq_text = fonts['BODY_FONT'].render(f"{self.tetris_game.math.equation}", True, TEXT_COLOR)
        self.screen.blit(eq_text, (modal_x + (modal_w - eq_text.get_width()) // 2, modal_y + 30))
        ans_text = fonts['BODY_FONT'].render(self.tetris_game.math.user_answer or "_", True, ACCENT_COLOR)
        self.screen.blit(ans_text, (modal_x + (modal_w - ans_text.get_width()) // 2, modal_y + 80))
        instr = fonts['SCORE_FONT'].render("Type answer and press Enter", True, TEXT_COLOR)
        self.screen.blit(instr, (modal_x + (modal_w - instr.get_width()) // 2, modal_y + 140))
        # No Back to Menu button in math overlay

    def draw_feedback_overlay(self):
        if not self.tetris_game:
            return
        sw, sh = self.screen_width, self.screen_height
        modal_w, modal_h = min(400, sw * 0.4), min(120, sh * 0.2)
        modal_x = (sw - modal_w) // 2
        modal_y = (sh - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
        pygame.draw.rect(self.screen, WHITE, modal_rect, border_radius=16)
        pygame.draw.rect(self.screen, self.tetris_game.feedback_color, modal_rect, 4, border_radius=16)
        fonts = get_fonts()
        msg = fonts['BODY_FONT'].render(self.tetris_game.feedback_message, True, self.tetris_game.feedback_color)
        self.screen.blit(msg, (modal_x + (modal_w - msg.get_width()) // 2, modal_y + (modal_h - msg.get_height()) // 2))
        # No Back to Menu button in feedback overlay

    def draw_game_over(self, mouse_pos, mouse_click):
        self.screen.fill(BG_COLOR)
        fonts = get_fonts()
        font = pygame.font.SysFont('Arial', 60, bold=True)
        game_over_text = font.render("GAME OVER", True, (231, 76, 60))
        text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 60))
        self.screen.blit(game_over_text, text_rect)
        score_text = fonts['BODY_FONT'].render(f"Score: {self.tetris_game.score if self.tetris_game else 0}", True, TEXT_COLOR)
        self.screen.blit(score_text, (self.screen_width // 2 - score_text.get_width() // 2, self.screen_height // 2 + 10))
        restart_text = fonts['BODY_FONT'].render("Press R to Restart", True, TEXT_COLOR)
        self.screen.blit(restart_text, (self.screen_width // 2 - restart_text.get_width() // 2, self.screen_height // 2 + 60))
        # Make back button a bit longer to cover the text
        self.back_btn.rect.topleft = (self.screen_width // 2 - 90, self.screen_height // 2 + 120)
        self.back_btn.rect.size = (180, 44)
        self.back_btn.draw(self.screen)
        self.back_btn.update(mouse_pos)
        if self.back_btn.is_clicked(mouse_pos, mouse_click):
            self.state = 'menu'
            self.name = ''
            self.difficulty = None
            self.tetris_game = None
