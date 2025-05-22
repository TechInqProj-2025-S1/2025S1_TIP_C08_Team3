"""Button UI for pygame"""
import pygame
from .constants import SECONDARY_COLOR, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR

class Button:
    # Clickable button for pygame
    # pylint: disable=too-many-arguments
    def __init__(self, x, y, width, height, text, font_size=32, color=BUTTON_COLOR,
                 hover_color=BUTTON_HOVER_COLOR, text_color=BUTTON_TEXT_COLOR, font=None):
        # Init Button
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.text_color = text_color
        self.hovered = False
        if font is not None:
            self.font = font
        else:
            self.font = pygame.font.SysFont('arial', font_size, bold=True)

    def draw(self, surface):
        # Draw button
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, SECONDARY_COLOR, self.rect, 3, border_radius=10)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        # Update color on hover
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            self.hovered = True
            return True
        self.current_color = self.color
        self.hovered = False
        return False

    def is_clicked(self, mouse_pos, mouse_click):
        # Check if clicked
        return self.rect.collidepoint(mouse_pos) and mouse_click
