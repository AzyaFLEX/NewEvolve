from pygame.locals import *
from numba import njit, prange
import configparser
import self_classes
from debug import *
import datetime
import random
import pygame
import numpy


class Board:
    def __init__(self, config_name='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_name)

        self.width = int(self.config['Board']['width'])
        self.height = int(self.config['Board']['height'])
        self.cell_size = int(self.config['Board']['cell_size'])
        self.cells_x = self.width // self.cell_size
        self.cells_y = self.height // self.cell_size
        self.matrix = numpy.array([[0 for _ in prange(self.cells_x)]
                                   for _ in prange(self.cells_y)])
        self.object_dict = {}
        self.season_dict = {}
        self.get_season()
        self.last_cell_id = 0
        self.max_gen = len(self_classes.cell.Cell(self, -1, -1, -1).the_dict_of_life) - 1
        self.is_world_stopped = False
        self.is_way_showing = False
        self.normal_fps = int(self.config['Board']['fps'])
        self.fps = self.normal_fps
        '''[optimization dict]'''
        self.right_pos = {}
        '''[config vars]'''
        self.eat_percent = float(self.config['Board']['eat_percent'])

    def __str__(self):
        return f'{self.matrix}'

    def __repr__(self):
        return self.__str__()

    def get_season(self):
        half = self.cells_y // 2
        quoter = half // 4
        for i in range(4):
            self.season_dict[(0 + quoter * i, quoter + quoter * i)] = (0, 1 - i * 1 / 4)

    def get_id(self, x):
        return self.matrix[x[0], x[1]]

    def get_color(self, id):
        try:
            obj = self.object_dict[id]
        except KeyError as error:
            print(error, self.object_dict)
            return
        if obj is not None and not obj:
            return 139, 139, 139
        else:
            len_code = len(obj.code)
            r = 0
            for elm in range(9, 18):
                r += obj.code.count(elm)
            r = round(r / len_code * 255)
            g = round(obj.code.count(0) / len_code * 255)
            b = 0
            r, g, b = (255, 255, 255) if not r + g + b else (r, g, b)
            return r, g, b

    def update(self):
        _dict = self.object_dict.copy()
        for key in _dict:
            try:
                self.object_dict[key].do()
            except KeyError:
                pass

    def render(self, screen):
        screen.fill((0, 0, 0))
        matrix = self.matrix[:]
        get_color = self.get_color
        cell_size = self.cell_size
        for y in prange(self.cells_y):
            for x in prange(self.cells_x):
                if matrix[y, x]:
                    pygame.draw.rect(screen, get_color(matrix[y, x]),
                                     (x * cell_size, y * cell_size,
                                      cell_size, cell_size))
                    if self.is_way_showing:
                        way = self.object_dict[matrix[y, x]].way
                        pygame.draw.line(screen, (0, 0, 0),
                                         (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2),
                                         (x * cell_size + cell_size // 2 + way[0] * (cell_size // 2),
                                          y * cell_size + cell_size // 2 + way[1] * (cell_size // 2))
                                         )
        pygame.display.flip()

    def run(self):
        pygame.init()
        flags = DOUBLEBUF
        screen = pygame.display.set_mode((self.width, self.height), flags)
        screen.set_alpha(None)
        run = True
        clock = pygame.time.Clock()
        while run:
            time1 = datetime.datetime.now()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.create_new_cell(event.pos[1] // self.cell_size,
                                             event.pos[0] // self.cell_size)
                    elif event.button == 3:
                        data = self.matrix[event.pos[1] // self.cell_size, event.pos[0] // self.cell_size]
                        if not data:
                            print('There is nothing here')
                        else:
                            print(self.object_dict[data])
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.is_world_stopped = not self.is_world_stopped
                    elif event.key == pygame.K_f:
                        self.fps = 0 if self.fps else self.normal_fps
                    elif event.key == pygame.K_l:
                        self.is_way_showing = not self.is_way_showing
            if not self.is_world_stopped:
                self.update()
                self.render(screen)
                clock.tick(self.fps)
                time2 = datetime.datetime.now()
                pygame.display.set_caption(f'obj\'s: {len(self.object_dict)},' +
                                           f' fps: {round(1 / ((time2 - time1).microseconds / 1000000))}')

    def create_new_cell(self, y, x, code=None):
        if not self.matrix[y, x]:
            self.last_cell_id += 1
            if code and random.randint(1, 100) <= 15:
                code[random.randint(0, 31)] = random.randint(0, self.max_gen)
            self.object_dict[self.last_cell_id] = self_classes.cell.Cell(self, self.last_cell_id, x, y, code)
            self.matrix[y, x] = self.last_cell_id

    def move_cell(self, old_pos, new_pos):
        self.matrix[old_pos[0], old_pos[1]], self.matrix[
            new_pos[0], new_pos[1]] = 0, self.matrix[old_pos[0], old_pos[1]]

    def kill(self, obj_coords):
        obj_id = self.matrix[obj_coords[0], obj_coords[1]]
        obj = self.object_dict[obj_id]
        energy = obj.energy * self.eat_percent
        self.matrix[obj.y, obj.x] = 0
        del obj
        self.object_dict.pop(obj_id)
        return energy
