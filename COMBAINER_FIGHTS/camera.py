__author__ = 'dimapct'

import pygame


class Camera(pygame.sprite.Sprite):
    def __init__(self, target=None):
        pygame.sprite.Sprite.__init__(self)
        self.target = target
        self.rect = pygame.Rect((0, 0), pygame.display.get_surface().get_size())

    def update(self):
        self.update_game_rect()

    def update_game_rect(self):
        self.rect.center = self.target.game_rect.center