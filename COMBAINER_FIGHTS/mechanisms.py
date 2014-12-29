__author__ = 'dimapct'


import game_object


class Ship(game_object.GameObject):
    def __init__(self, owner_id, **kwargs):
        game_object.GameObject.__init__(self, owner_id, **kwargs)

    def update(self, t):
        # print(456, 'SHIP update', self.game_position)
        self.update_position_with_interpolation(t)

    def draw(self, background):
        background.blit(self.image, self.rect.topleft)

