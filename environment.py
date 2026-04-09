import numpy as np
import random

class Grid:
    def __init__(self, size=15):
        self.size = size
        self.map = np.zeros((size, size), dtype=int)
        self.start = None
        self.goal = None

    def generate_map(self, obstacle_density=0.2):
        self.map = np.zeros((self.size, self.size), dtype=int)
        for row in range(self.size):
            for col in range(self.size):
                if random.random() < obstacle_density:
                    self.map[row][col] = 1  # obstacle

    def place_victim(self):
        free_cells = [(r, c) for r in range(self.size)
                      for c in range(self.size) if self.map[r][c] == 0]
        self.goal = random.choice(free_cells)
        self.map[self.goal[0]][self.goal[1]] = 2  # victim

    def place_drone(self):
        free_cells = [(r, c) for r in range(self.size)
                      for c in range(self.size) if self.map[r][c] == 0]
        self.start = random.choice(free_cells)

    def get_neighbours(self, pos):
        row, col = pos
        directions = [(-1,0), (1,0), (0,-1), (0,1)]  # up, down, left, right
        neighbours = []
        for dr, dc in directions:
            new_pos = (row + dr, col + dc)
            if self.is_valid(new_pos):
                neighbours.append(new_pos)
        return neighbours

    def is_valid(self, pos):
        row, col = pos
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False
        if self.map[row][col] == 1:  # obstacle
            return False
        return True

    def display(self):
        symbols = {0: '.', 1: '#', 2: 'V', 3: '*'}
        for row in range(self.size):
            print(' '.join(symbols.get(self.map[row][col], '?') 
                           for col in range(self.size)))
        print()