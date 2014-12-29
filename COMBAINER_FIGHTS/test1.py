

import pygame
import random
from pygame.locals import *
pygame.init()

s = pygame.display.set_mode((500, 500))

while True:
    x = random.randint(0, 499)
    y = random.randint(0, 499)
    if s.get_at((x, y)) == (0, 0, 0):
        s.set_at((x, y), Color('yellow'))
    pygame.display.flip()