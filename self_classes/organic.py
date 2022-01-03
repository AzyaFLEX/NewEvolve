class Organic:
    def __init__(self, world, x, y):
        self.world = world
        self.x, self.y = x, y

    def __str__(self):
        return f'Organic'

    def __repr__(self):
        return self.__str__()

    def do(self):
        if len(self.world.matrix) - 1 != self.y and not self.world.matrix[self.y + 1, self.x]:
            old_pos = (self.y, self.x)
            self.y += 1
            self.world.move_cell(old_pos, (self.y, self.x))
