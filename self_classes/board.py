import self_classes
from debug import *
import pygame
import numpy


class Board:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cells_x = width // cell_size
        self.cells_y = height // cell_size
        self.cell_size = cell_size
        self.matrix = numpy.array([[0 for _ in range(self.cells_x)]
                                   for _ in range(self.cells_y)])
        self.object_dict = {}
        self.last_cell_id = 0
        self.is_world_stopped = False

    def __str__(self):
        return f'{self.matrix}'

    def __repr__(self):
        return self.__str__()

    @time_test
    def update(self):
        for key in self.object_dict.copy():
            self.object_dict[key].do()

    @time_test
    def render(self, screen):
        screen.fill((0, 0, 0))
        for y in range(self.cells_y):
            for x in range(self.cells_x):
                if self.matrix[y, x]:
                    pygame.draw.rect(screen, (0, 255, 0),
                                     (x * self.cell_size, y * self.cell_size,
                                      self.cell_size, self.cell_size))
        pygame.display.flip()

    def run(self):
        screen = pygame.display.set_mode((self.width, self.height))
        run = True
        while run:
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

    def create_new_cell(self, y, x, code=None):
        if self.matrix[y, x] == 0:
            self.last_cell_id += 1
            self.object_dict[self.last_cell_id] = self_classes.cell.Cell(self, x, y, code)
            self.matrix[y, x] = self.last_cell_id

    def move_cell(self, old_pos, new_pos):
        self.matrix[old_pos[0], old_pos[1]], self.matrix[
            new_pos[0], new_pos[1]] = 0, self.matrix[old_pos[0], old_pos[1]]