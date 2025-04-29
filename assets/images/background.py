class Background:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = self.load_image()

    def load_image(self):
        import pygame
        return pygame.image.load(self.image_path)

    def draw(self, surface):
        surface.blit(self.image, (0, 0))