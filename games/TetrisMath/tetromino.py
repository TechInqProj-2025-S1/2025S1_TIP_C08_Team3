
# Tetromino shapes and logic
from .constants import BLOCK_COLORS

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]]
]
SHAPE_COLORS = BLOCK_COLORS[:7]

class Tetromino:
    # Tetromino piece
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

    def rotate(self):
        # Rotate piece
        self.rotation = (self.rotation + 1) % 4
        self.shape = self.get_rotated_shape()

    def get_rotated_shape(self):
        # Get rotated shape
        if self.shape is not None:
            if self.rotation == 0:
                return self.shape
            elif self.rotation == 1:
                rows = len(self.shape)
                cols = len(self.shape[0])
                rotated = [[0 for _ in range(rows)] for _ in range(cols)]
                for r in range(rows):
                    for c in range(cols):
                        rotated[c][rows - 1 - r] = self.shape[r][c]
                return rotated
            elif self.rotation == 2:
                rows = len(self.shape)
                cols = len(self.shape[0])
                rotated = [[0 for _ in range(cols)] for _ in range(rows)]
                for r in range(rows):
                    for c in range(cols):
                        rotated[rows - 1 - r][cols - 1 - c] = self.shape[r][c]
                return rotated
            elif self.rotation == 3:
                rows = len(self.shape)
                cols = len(self.shape[0])
                rotated = [[0 for _ in range(rows)] for _ in range(cols)]
                for r in range(rows):
                    for c in range(cols):
                        rotated[cols - 1 - c][r] = self.shape[r][c]
                return rotated
