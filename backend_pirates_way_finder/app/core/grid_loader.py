import json

class Grid:
    def __init__(self):
        self.grid = None
        self.cell_size = None
        self.w = None
        self.h = None

    def load(self, path):
        with open(path , "r") as f:
            data = json.load(f)
            self.grid = data["grid"]
            self.cell_size = data["cell_size"]
            self.w = data["width"]
            self.h = data["height"]

grid_instance = Grid()