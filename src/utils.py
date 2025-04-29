def load_image(filepath):
    """Load an image from the specified filepath."""
    try:
        image = pygame.image.load(filepath)
        return image
    except pygame.error as e:
        print(f"Unable to load image at {filepath}: {e}")
        return None

def load_font(font_path, size):
    """Load a font from the specified path with the given size."""
    try:
        font = pygame.font.Font(font_path, size)
        return font
    except FileNotFoundError:
        print(f"Font file not found at {font_path}")
        return None

def scale_image(image, width, height):
    """Scale an image to the specified width and height."""
    return pygame.transform.scale(image, (width, height))