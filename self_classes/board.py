from pygame.locals import *
import self_classes
from debug import *
import datetime
import random
import pygame
import numpy


class Board:
    def __init__(self, width, height, cell_size):
        self.width = int(width)
        self.height = int(height)
        self.cell_size = int(cell_size)
        self.cells_x = self.width // self.cell_size
        self.cells_y = self.height // self.cell_size
        self.matrix = numpy.array([[0 for _ in range(self.cells_x)]
                                   for _ in range(self.cells_y)])
        self.object_dict = {}
        self.last_cell_id = 0
        self.is_world_stopped = False
        '''[optimization dict]'''
        self.cash_coords_around = {}
        self.right_pos = {}

    def __str__(self):
        return f'{self.matrix}'

    def __repr__(self):
        return self.__str__()

    def get_color(self, id):
        obj = self.object_dict[id]
        if not obj:
            return 139, 139, 139
        else:
            # TODO
            return 0, 255, 0

    def update(self):
        _dict = self.object_dict.copy()
        for key in _dict:
            _dict[key].do()

    def render(self, screen):
        screen.fill((0, 0, 0))
        matrix = self.matrix[:]
        get_color = self.get_color
        cell_size = self.cell_size
        for y in range(self.cells_y):
            for x in range(self.cells_x):
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
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.is_world_stopped = not self.is_world_stopped
            if not self.is_world_stopped:
                self.update()
                self.render(screen)
                time2 = datetime.datetime.now()
                pygame.display.set_caption(f'fps: {1 / ((time2 - time1).microseconds / 1000000)}')

    def create_new_cell(self, y, x, code=None):
        if not self.matrix[y, x]:
            self.last_cell_id += 1
            if code and random.randint(1, 100) <= 17:
                code[random.randint(0, 31)] = random.randint(0, 5)
            self.object_dict[self.last_cell_id] = self_classes.cell.Cell(self, x, y, code)
            self.matrix[y, x] = self.last_cell_id

    def move_cell(self, old_pos, new_pos):
        self.matrix[old_pos[0], old_pos[1]], self.matrix[
            new_pos[0], new_pos[1]] = 0, self.matrix[old_pos[0], old_pos[1]]