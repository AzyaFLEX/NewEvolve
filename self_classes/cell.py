from random import randint, choice
from self_classes.board import Board
from numba import prange, njit
import configparser
from debug import *
import op_tools
import numpy


def get_config_int(config, request):
    return int(config[request])


class Cell:
    def __init__(self, world, id, x, y, code=None):
        if code is None:
            code = [0 for _ in prange(32)]

        """[self.cell config params]"""
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.config = config['Cell']
        self.move_cost = get_config_int(self.config, 'move_cost')
        self.photosynthesis_energy = get_config_int(self.config, 'photosynthesis')
        self.create_energy = get_config_int(self.config, 'create_new_cell_cost')
        self.organic_decomposition_time = get_config_int(self.config, 'organic_decomposition_time')
        self.base_energy = get_config_int(self.config, 'base_energy')

        """[self.cell main params]"""
        self.id = id
        self.world = world
        self.x, self.y = x, y
        self.alive = True
        self.code = code

        """[self.cell resources]"""
        self.energy = self.base_energy
        self.current = 0
        self.mineral = 0

        """[self.cell code dict]"""
        self.the_dict_of_life = {
            0: 'self.photosynthesis()',
            1: 'self.move((1, 0))',
            2: 'self.move((-1, 0))',
            3: 'self.move((0, 1))',
            4: 'self.move((0, -1))',
            5: 'self.move((1, 1))',
            6: 'self.move((1, -1))',
            7: 'self.move((-1, 1))',
            8: 'self.move((-1, -1))',
            9: 'self.eat((1, 0))',
            10: 'self.eat((-1, 0))',
            11: 'self.eat((0, 1))',
            12: 'self.eat((0, -1))',
            13: 'self.eat((1, 1))',
            14: 'self.eat((1, -1))',
            15: 'self.eat((-1, 1))',
            16: 'self.eat((-1, -1))',
            17: 'self.eat()',
            18: 'self.eat_organic()',
            19: 'self.is_organic_near()',
            20: 'self.is_organic_near(reverse=True)',
        }

    def __str__(self):
        return f'{"Cell" if self.alive else "Organic"} with coords {self.y, self.x}\nCode: {self.code}'

    def __repr__(self):
        return f'[{self.id}]'

    def __bool__(self):
        return self.alive

    # The basic principle of moving cells on my board
    def correct_pos(self, data):
        if tuple(data) not in self.world.right_pos:
            y, x = data
            if x < 0:
                x = self.world.cells_x - 1
            elif x == self.world.cells_x:
                x = 0
            if y < 0:
                y = 0
            elif y == self.world.cells_y:
                y = self.world.cells_y - 1
            self.world.right_pos[tuple(data)] = (y, x)
        return self.world.right_pos[tuple(data)]

    def check_death(self):
        if self.energy <= 0:
            self.death()
            return True
        return False

    def death(self):
        self.alive = False
        self.code = [3]
        self.current = 0
        self.energy = 0

    def do(self):
        if self.energy >= self.create_energy:
            self.create_new_cell()
            return
        try:
            exec(self.the_dict_of_life[self.code[self.current]])
        except KeyError:
            pass
        if self.alive:
            self.energy -= self.move_cost
            self.check_death()
            self.current = (self.current + 1) % len(self.code)

    def cells_around(self):
        result = []
        for i in prange(self.y - 1, self.y + 2):
            if i >= 0:
                pre_res = []
                for j in prange(self.x - 1, self.x + 2):
                    if i < self.world.cells_y:
                        pre_res += [[i, j if j < self.world.cells_x else 0]]
                result += [pre_res]
        return result

    def cells_to_eat_around(self):
        cells_around = self.cells_around()
        result = []
        for row in cells_around:
            for elm in row:
                if self.world.matrix[elm[0], elm[1]] not in {0, self.id}:
                    result += [elm]
        return result

    def get_organic_near(self):
        variants = []
        for coords in self.cells_to_eat_around():
            if not self.world.object_dict[self.world.get_id(coords)]:
                variants += [coords]
        return variants

    def photosynthesis(self):
        self.energy += self.photosynthesis_energy

    def eat(self, way: tuple = None):
        if way is None:
            around = self.cells_to_eat_around()
            if around:
                self.energy += self.world.kill(choice(around))
        else:
            obj_id = self.world.matrix[self.correct_pos((self.y + way[0], self.x + way[1]))]
            if obj_id:
                self.energy += self.world.kill(self.correct_pos((self.y + way[0], self.x + way[1])))

    def eat_organic(self):
        variants = self.get_organic_near()
        if variants:
            self.world.kill(choice(variants))
            self.energy += self.base_energy * 0.8

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
                if not self.world.matrix[elm[0], elm[1]]:
                    result += [elm]
        if result:
            self.energy -= self.create_energy // 2
            if self.check_death():
                return
            random_cell = self.correct_pos(choice(result))
            self.world.create_new_cell(*random_cell, self.code[:])
        else:
            self.death()

    def is_organic_near(self, reverse=False):
        task = not self.get_organic_near()
        if task if not reverse else not task:
            self.current += 1
