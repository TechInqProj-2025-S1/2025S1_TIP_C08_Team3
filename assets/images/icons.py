class IconManager:
    def __init__(self, icon_paths):
        self.icons = {}
        self.load_icons(icon_paths)

    def load_icons(self, icon_paths):
        for name, path in icon_paths.items():
            self.icons[name] = self.load_icon(path)

    def load_icon(self, path):
        try:
            icon = pygame.image.load(path)
            icon = pygame.transform.scale(icon, (32, 32))  # Scale to a standard size
            return icon
        except pygame.error as e:
            print(f"Failed to load icon at {path}: {e}")
            return None

    def get_icon(self, name):
        return self.icons.get(name, None)