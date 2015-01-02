__author__ = 'test'


import game_object


class Bunker():
    def __init__(self, size, name=None):
        self.name = name
        self.accumulator = 0
        self.size = size

    def has_space(self):
        if self.accumulator < self.size:
            return True

    def __add__(self, other):
        self.accumulator += other
        if self.accumulator > self.size:
            self.accumulator = self.size
        return self

    def __sub__(self, other):
        self.accumulator -= other
        if self.accumulator < 0:
            self.accumulator = 0
            raise NotImplementedError('You want to subtract from bunker more than available')
        return self


class Heap(Bunker, game_object.GameObject):
    def __init__(self, size, owner_id, **kwargs):
        name = kwargs.get('name')
        Bunker.__init__(self, size, name)
        game_object.GameObject.__init__(self, owner_id, **kwargs)

    @staticmethod
    def get_game_xy(center_xy, obj_size):
        x = center_xy[0] + obj_size[0]//2
        y = center_xy[1]
        return x, y