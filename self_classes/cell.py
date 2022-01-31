from self_classes.board import Board
from random import randint, choice
from math import radians, sin, cos
from numba import prange, njit
from debug import *
import configparser


def get_config_int(config, request):
    return int(config[request])


def find_by_key(dict_: dict, value: str):
    for key, _value in dict_.items():
        if _value == value:
            return key


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

        """[self.world and other that connected with world]"""
        self.world = world
        self.max_x = self.world.cells_x
        self.max_y = self.world.cells_y

        """[self.cell main params]"""
        self.id = id
        self.x, self.y = x, y
        self.way = tuple([choice((-1, 1)) for _ in range(2)])
        self.alive = True
        self.code = code

        """[self.cell resources]"""
        self.energy = self.base_energy
        self.current = 0
        self.mineral = 0

        """[self.cell code dict]"""
        self.the_dict_of_life = {
            0: 'self.photosynthesis()',
            1: 'self.eat()',
            2: 'self.eat()',
            3: 'self.move()',
            4: 'self.change_way()',
            5: 'self.change_way(reverse=True)',
            6: 'self.change_way_abs()',
            7: 'self.change_way_abs(reverse=True)',
            8: 'self.look_for_cells_around()',
            9: 'self.look_for_free_place_around()',
            10: 'self.eat_organic()',
            11: 'self.is_organic_near()',
            12: 'self.is_organic_near(reverse=True)',
            14: 'self.eat()',
            15: 'self.eat(with_way=False)',
            16: 'self.look_at_sun()',
            17: 'look_at_energy()'
        }

        self.code_for_death = find_by_key(self.the_dict_of_life, 'self.move()')

    def __str__(self):
        return f'''{"Cell" if self.alive else "Organic"} with coords {self.y, self.x}
Energy: {self.energy}
Way: {self.way}
Code: {self.code}'''

    def __repr__(self):
        return f'[{self.id}]'

    def __bool__(self):
        return self.alive

    # The basic principle of moving cells on my board
    def correct_pos(self, data):
        if tuple(data) not in self.world.right_pos:
            y, x = data
            if x < 0:
                x = self.max_x - 1
            elif x == self.max_x:
                x = 0
            if y < 0:
                y = 0
            elif y == self.max_y:
                y = self.max_y - 1
            self.world.right_pos[tuple(data)] = (y, x)
        return self.world.right_pos[tuple(data)]

    def change_way(self, angle=45, reverse=False, abs_=False):
        x, y = self.way if not abs_ else (0, 1)
        angle = radians(angle) * (1 if reverse else -1)
        self.way = round(x * cos(angle) - y * sin(angle)), round(x * sin(angle) + y * cos(angle))

    def change_way_abs(self, reverse=False):
        next_code = self.code[(self.current + 1) % len(self.code)]
        self.change_way(angle=45 * next_code % 8, reverse=reverse, abs_=True)

    def look_for_cells_around(self, free=False):
        def correct_way(way):
            result = []
            for elm in way:
                if elm > 1:
                    elm = 1
                if elm < -1:
                    elm = -1
                result += [elm]
            return tuple(result)

        around = self.cells_to_eat_around(free=free)
        if around:
            any_ = choice(around)
            self.way = correct_way((any_[1] - self.x, any_[0] - self.y))

    def look_for_free_place_around(self):
        self.look_for_cells_around(free=True)

    def check_death(self):
        if self.energy <= 0:
            self.death()
            return True
        return False

    def death(self):
        self.alive = False
        self.way = (0, 1)
        self.code = [self.code_for_death]
        self.current = 0
        self.energy = 0

    def do(self):
        if self.energy >= self.create_energy:
            self.create_new_cell()
            return
        try:
            if self.alive or self.y != self.max_y - 1:
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
                    if i < self.max_y:
                        pre_res += [[i, j if j < self.max_x else 0]]
                result += [pre_res]
        return result

    def cells_to_eat_around(self, free=False):
        cells_around = self.cells_around()
        result = []
        if not free:
            for row in cells_around:
                for elm in row:
                    if self.world.matrix[elm[0], elm[1]] not in {0, self.id}:
                        result += [elm]
        else:
            for row in cells_around:
                for elm in row:
                    if self.world.matrix[elm[0], elm[1]] == 0:
                        result += [elm]
        return result

    def get_organic_near(self):
        variants = []
        for coords in self.cells_to_eat_around():
            if not self.world.object_dict[self.world.get_id(coords)]:
                variants += [coords]
        return variants

    def photosynthesis(self):
        for i in self.world.season_dict:
            if i[1] >= self.y >= i[0] and not self.world.season_dict[i][0]:
                self.energy += self.photosynthesis_energy * self.world.season_dict[i][1]

    def eat(self, with_way=True):
        if not with_way:
            self.energy -= self.move_cost // 4
            around = self.cells_to_eat_around()
            if around:
                self.energy += self.world.kill(choice(around))
        else:
            first, second = (self.correct_pos((self.y + self.way[1], self.x + self.way[0])))
            obj_id = self.world.matrix[first, second]
            if obj_id:
                self.energy += self.world.kill((first, second))

    def eat_organic(self):
        variants = self.get_organic_near()
        if variants:
            self.world.kill(choice(variants))
            self.energy += self.base_energy * 0.8

    def move(self):
        old_pos = (self.y, self.x)
        new_pos = self.correct_pos((self.y + self.way[1], self.x + self.way[0]))
        try:
            if not self.world.matrix[new_pos[0], new_pos[1]]:
                self.y, self.x = new_pos
                self.world.move_cell(old_pos, new_pos)
        except IndexError as error:
            print(error, self.way, old_pos, new_pos)

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

    def look_at_sun(self):
        for i in self.world.season_dict:
            if i[1] >= self.y >= i[0] and not self.world.season_dict[i][0]:
                if self.world.season_dict[i][1] < 0.5:
                    self.current += 1

    def look_at_energy(self):
        if self.energy < self.base_energy:
            self.current += 1

    # def place_block(self):
    #     self.energy -= 200
    #     first, second = (self.correct_pos((self.y + self.way[1], self.x + self.way[0])))
    #     if not self.world.matrix[first, second]:
    #         self.world.matrix[first, second] = -1
