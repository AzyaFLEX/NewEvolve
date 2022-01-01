from random import randint, choice
from self_classes.board import Board
from debug import *
import numpy


the_dict_of_life = {
    0: 'self.photosynthesis()',
    1: 'self.move((1, 0))',
    2: 'self.move((-1, 0))',
    3: 'self.move((0, 1))',
    4: 'self.move((0, -1))',
    5: 'self.create_new_cell()'
}


class Cell:
    def __init__(self, world, x, y, code=None):
        if code is None:
            code = [0 for _ in range(31)] + [5]
        self.world = world
        self.x, self.y = x, y
        self.code = code
        self.energy = 500
        self.current = 0
        self.mineral = 0

    def do(self):
        exec(the_dict_of_life[self.code[self.current]])
        self.energy -= 15
        self.current = (self.current + 1) % len(self.code)

    def cells_around(self):
        result = []
        for i in range(self.y - 1, self.y + 2):
            if i >= 0:
                result += [[[j, i] for j in range(self.x - 1, self.x + 2)]]
        return result

    def photosynthesis(self):
        self.energy += 20

    def move(self, way):
        pass

    def create_new_cell(self):
        variats, result = self.cells_around(), []
        for row in variats:
            for elm in row:
                if self.world.matrix[elm[0], elm[1]] == 0:
                    result += [elm]
        random_cell = choice(result)
        self.world.create_new_cell(*random_cell)
