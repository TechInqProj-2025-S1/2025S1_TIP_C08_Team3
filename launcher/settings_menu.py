"""Settings menu for the game launcher."""
import sys
import json
import pygame
from .constants import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, PRIMARY_COLOR, BUTTON_COLOR, BUTTON_HOVER_COLOR,
    BUTTON_TEXT_COLOR, WHITE, BLACK
)
from .button import Button

def show_settings_menu(games, screen, clock, config_path, fonts):
    """
    Display and handle the settings menu for the launcher and games.

    Args:
        games (list): List of game objects.
        screen (pygame.Surface): The main display surface.
        clock (pygame.time.Clock): The game clock.
        config_path (str): Path to the config file.
        fonts (tuple): Tuple of pygame fonts (title, body, score, etc).
    """
    # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    title_font, _subtitle_font, body_font, score_font = fonts
    running = True
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    font = body_font
    tetris_multiplayer = config.get("games", {}).get("tetris_math_multiplayer", {})
    host_ip = tetris_multiplayer.get("host_ip", "127.0.0.1")
    host_port = str(tetris_multiplayer.get("host_port", "5000"))
    input_active = None
    real_screen_width, real_screen_height = screen.get_width(), screen.get_height()
    back_button = Button(
        real_screen_width // 2 - 150, real_screen_height - 120, 300, 60, "Back",
        color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR,
        text_color=BUTTON_TEXT_COLOR, font=body_font
    )
    # Layout: [Host IP:][input]   [Host Port:][input]
    ip_label = font.render("Host IP:", True, TEXT_COLOR)
    port_label = font.render("Host Port:", True, TEXT_COLOR)
    ip_box_width = 220
    port_box_width = 120
    box_height = 50
    # Calculate positions for horizontal alignment
    total_width = (
        ip_label.get_width() + ip_box_width + 40 + port_label.get_width() + port_box_width
    )
    start_x = real_screen_width // 2 - total_width // 2
    ip_label_x = start_x
    ip_box_x = ip_label_x + ip_label.get_width() + 10
    port_label_x = ip_box_x + ip_box_width + 30
    port_box_x = port_label_x + port_label.get_width() + 10
    input_y = 350
    ip_box = pygame.Rect(ip_box_x, input_y, ip_box_width, box_height)
    port_box = pygame.Rect(port_box_x, input_y, port_box_width, box_height)
    while running:
        screen.fill(BG_COLOR)
        title = title_font.render("Settings", True, TEXT_COLOR)
        screen.blit(title, (real_screen_width // 2 - title.get_width() // 2, 60))
        y = 180
        launcher_label = font.render("Launcher Settings", True, PRIMARY_COLOR)
        screen.blit(launcher_label, (real_screen_width // 2 - launcher_label.get_width() // 2, y))
        y += 50
        launcher_setting = font.render("(No settings yet)", True, TEXT_COLOR)
        screen.blit(launcher_setting, (real_screen_width // 2 - launcher_setting.get_width() // 2, y))
        y += 80
        tetris_label = font.render("Tetris Math Multiplayer", True, PRIMARY_COLOR)
        screen.blit(
            tetris_label,
            (real_screen_width // 2 - tetris_label.get_width() // 2, y)
        )
        y += 40
        # Draw IP label and box
        screen.blit(
            ip_label,
            (ip_label_x, input_y + (box_height - ip_label.get_height()) // 2)
        )
        pygame.draw.rect(screen, WHITE, ip_box, 2, border_radius=8)
        ip_surf = font.render(host_ip, True, BLACK)
        screen.blit(
            ip_surf,
            (ip_box.x + 10, ip_box.y + (box_height - ip_surf.get_height()) // 2)
        )
        # Draw Port label and box
        screen.blit(
            port_label,
            (port_label_x, input_y + (box_height - port_label.get_height()) // 2)
        )
        pygame.draw.rect(screen, WHITE, port_box, 2, border_radius=8)
        port_surf = font.render(host_port, True, BLACK)
        screen.blit(
            port_surf,
            (port_box.x + 10, port_box.y + (box_height - port_surf.get_height()) // 2)
        )
        instr = score_font.render(
            "Set IP/Port for LAN play. Host: share your IP/port. Join: enter host's IP/port.",
            True, TEXT_COLOR
        )
        screen.blit(
            instr,
            (real_screen_width // 2 - instr.get_width() // 2, 430)
        )
        y = 530
        for game in games:
            if game.name != "Tetris Math":
                game_label = font.render(f"{game.name} Settings", True, PRIMARY_COLOR)
                screen.blit(
                    game_label,
                    (real_screen_width // 2 - game_label.get_width() // 2, y)
                )
                y += 40
                game_setting = font.render("(No settings yet)", True, TEXT_COLOR)
                screen.blit(
                    game_setting,
                    (real_screen_width // 2 - game_setting.get_width() // 2, y)
                )
                y += 60
        back_button.update(pygame.mouse.get_pos())
        back_button.draw(screen)
        mouse_click = False
        for event in pygame.event.get():
            # pylint: disable=no-member
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True
                if ip_box.collidepoint(event.pos):
                    input_active = 'ip'
                elif port_box.collidepoint(event.pos):
                    input_active = 'port'
                else:
                    input_active = None
            if event.type == pygame.KEYDOWN and input_active:
                if input_active == 'ip':
                    if event.key == pygame.K_BACKSPACE:
                        host_ip = host_ip[:-1]
                    elif (
                        len(host_ip) < 15 and
                        (event.unicode.isdigit() or event.unicode == '.' or event.unicode == ':')
                    ):
                        host_ip += event.unicode
                elif input_active == 'port':
                    if event.key == pygame.K_BACKSPACE:
                        host_port = host_port[:-1]
                    elif len(host_port) < 5 and event.unicode.isdigit():
                        host_port += event.unicode
        if back_button.is_clicked(pygame.mouse.get_pos(), mouse_click):
            config.setdefault("games", {})["tetris_math_multiplayer"] = {
                "host_ip": host_ip,
                "host_port": int(host_port) if host_port.isdigit() else 5000
            }
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            running = False
        pygame.display.flip()
        clock.tick(60)
