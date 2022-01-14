from pygame.locals import *
from numba import njit, prange
import self_classes
from debug import *
import datetime
import random
import pygame
import numpy


class Board:
    def __init__(self, width, height, cell_size, fps):
        self.width = int(width)
        self.height = int(height)
        self.cell_size = int(cell_size)
        self.cells_x = self.width // self.cell_size
        self.cells_y = self.height // self.cell_size
        self.matrix = numpy.array([[0 for _ in prange(self.cells_x)]
                                   for _ in prange(self.cells_y)])
        self.object_dict = {}
        self.last_cell_id = 0
        self.is_world_stopped = False
        self.normal_fps = int(fps)
        self.fps = int(fps)
        '''[optimization dict]'''
        self.right_pos = {}

    def __str__(self):
        return f'{self.matrix}'

    def __repr__(self):
        return self.__str__()

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
            return r, g, 0

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
            if not self.is_world_stopped:
                self.update()
                self.render(screen)
                clock.tick(self.fps)
                time2 = datetime.datetime.now()
                pygame.display.set_caption(f'obj\'s: {len(self.object_dict)}, fps: {round(1 / ((time2 - time1).microseconds / 1000000))}')

    def create_new_cell(self, y, x, code=None):
        if not self.matrix[y, x]:
            self.last_cell_id += 1
            if code and random.randint(1, 100) <= 15:
                for _ in range(random.randint(1, 3)):
                    code[random.randint(0, 31)] = random.randint(0, 17)
            self.object_dict[self.last_cell_id] = self_classes.cell.Cell(self, self.last_cell_id, x, y, code)
            self.matrix[y, x] = self.last_cell_id

    def move_cell(self, old_pos, new_pos):
        self.matrix[old_pos[0], old_pos[1]], self.matrix[
            new_pos[0], new_pos[1]] = 0, self.matrix[old_pos[0], old_pos[1]]

    def kill(self, obj_coords):
        obj_id = self.matrix[obj_coords[0], obj_coords[1]]
        obj = self.object_dict[obj_id]
        energy = obj.energy * 0.95
        self.matrix[obj.y, obj.x] = 0
        del obj
        self.object_dict.pop(obj_id)
        return energy
