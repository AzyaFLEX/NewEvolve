from random import randint, choice
from self_classes.board import Board
import configparser
from debug import *
import numpy


def get_config_int(config, request):
    return int(config[request])


class Cell:
    def __init__(self, world, x, y, code=None):
        if code is None:
            code = [randint(0, 4) for _ in range(31)] + [5]

        """[self.cell config params]"""
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.config = config['Cell']
        self.move_cost = get_config_int(self.config, 'move_cost')
        self.photosynthesis_energy = get_config_int(self.config, 'photosynthesis')
        self.create_energy = get_config_int(self.config, 'create_new_cell_cost')
        base_energy = get_config_int(self.config, 'base_energy')

        """[self.cell main params]"""
        self.world = world
        self.x, self.y = x, y
        self.alive = True
        self.code = code

        """[self.cell resources]"""
        self.energy = 2000
        self.current = 0
        self.mineral = 0

        """[self.cell code dict]"""
        self.the_dict_of_life = {
            0: 'self.photosynthesis()',
            1: 'self.move((1, 0))',
            2: 'self.move((-1, 0))',
            3: 'self.move((0, 1))',
            4: 'self.move((0, -1))',
            5: 'self.create_new_cell()'
        }

    def __str__(self):
        return f'Cell with coords {self.y, self.x}'

    def __repr__(self):
        return self.__str__()

    def __bool__(self):
        return self.alive

    # The basic principle of moving cells on my board
    def correct_pos(self, data):
        y, x = data
        if x < 0:
            x = self.world.cells_x - 1
        elif x == self.world.cells_x:
            x = 0
        if y < 0:
            y = 0
        elif y == self.world.cells_y:
            y = self.world.cells_y - 1
        return y, x

    def check_death(self):
        if self.energy <= 0:
            self.death()
            return True
        return False

    def death(self):
        self.alive = False
        self.code = [3]
        self.current = 0

    def do(self):
        exec(self.the_dict_of_life[self.code[self.current]])
        self.energy -= self.move_cost
        self.check_death()
        self.current = (self.current + 1) % len(self.code)

    def cells_around(self):
        result = []
        for i in range(self.y - 1, self.y + 2):
            if i >= 0:
                result += [[[i if i < self.world.cells_y else 0, j if j < self.world.cells_x else 0]
                            for j in range(self.x - 1, self.x + 2)]]
        return result

    def photosynthesis(self):
        self.energy += self.photosynthesis_energy

    def move(self, way):
        old_pos = (self.y, self.x)
        new_pos = self.correct_pos((self.y + way[1], self.x + way[0]))
        if not self.world.matrix[new_pos[0], new_pos[1]]:
            self.y, self.x = new_pos
            self.world.move_cell(old_pos, new_pos)

    def create_new_cell(self):
        variats, result = self.cells_around(), []
        for row in variats:
            for elm in row:
                if self.world.matrix[elm[0], elm[1]] == 0:
                    result += [elm]
        if result:
            self.energy -= self.create_energy
            if self.check_death():
                return
            random_cell = self.correct_pos(choice(result))
            self.world.create_new_cell(*random_cell)
        else:
            self.death()
