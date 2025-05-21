"""Button module for UI elements using pygame."""
import pygame
from .constants import SECONDARY_COLOR, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR

class Button:
    """A clickable button UI element for pygame applications."""
    # pylint: disable=too-many-arguments
    def __init__(self, x, y, width, height, text, font_size=32, color=BUTTON_COLOR,
                 hover_color=BUTTON_HOVER_COLOR, text_color=BUTTON_TEXT_COLOR, font=None):
        """
        Initialize a Button instance.

        Args:
            x (int): X position of the button.
            y (int): Y position of the button.
            width (int): Width of the button.
            height (int): Height of the button.
            text (str): Text to display on the button.
            font_size (int, optional): Font size. Defaults to 32.
            color (tuple, optional): Button color. Defaults to BUTTON_COLOR.
            hover_color (tuple, optional): Hover color. Defaults to BUTTON_HOVER_COLOR.
            text_color (tuple, optional): Text color. Defaults to BUTTON_TEXT_COLOR.
            font (pygame.font.Font, optional): Custom font. Defaults to None.
        """
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
        """
        Draw the button on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw the button on.
        """
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, SECONDARY_COLOR, self.rect, 3, border_radius=10)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        """
        Update the button's color based on mouse position.

        Args:
            mouse_pos (tuple): The current mouse position.

        Returns:
            bool: True if mouse is over the button, False otherwise.
        """
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            self.hovered = True
            return True
        self.current_color = self.color
        self.hovered = False
        return False

    def is_clicked(self, mouse_pos, mouse_click):
        """
        Check if the button is clicked.

        Args:
            mouse_pos (tuple): The current mouse position.
            mouse_click (bool): Whether the mouse button is pressed.

        Returns:
            bool: True if button is clicked, False otherwise.
        """
        return self.rect.collidepoint(mouse_pos) and mouse_click
