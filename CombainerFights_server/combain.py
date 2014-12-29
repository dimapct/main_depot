__author__ = 'dimapct'

import pygame
from game_tools import Vector2
import game_object
import random
import config as c
import bunker


class Combain(game_object.GameObject):
    def __init__(self, owner_id, **kwargs):
        game_object.GameObject.__init__(self, owner_id, **kwargs)
        self.comb_dict = kwargs.get('comb_dict')
        # self.comb_dict['conductor'].play()
        # self.comb_dict['conductor'].pause()
        combain_bunker_size = kwargs.get('bunker_size')
        self.bunker = bunker.Bunker(combain_bunker_size, name='bunker')
        self.zhatka = Zhatka()
        self.weapons_dict = dict()

    def update(self, key_pressed):
        self.update_rect_size()
        self.update_weapons()
        if self.zhatka.harvesting:
            self.get_harvest()

        self.check_mines_and_bullets()

    def get_harvest(self):
        point = self.game_rect.center
        for offset in self.comb_dict[self.direction]['zhatka']:
            x = point[0] - offset[0]
            y = point[1] - offset[1]

            # Check for game boundary
            if not 0 <= x < c.game_world_width or not 0 <= y < c.game_world_height:
                continue

            region, xy = self.game_map.get_region_and_xy((x, y))

            if region.image.get_at(xy) == c.wheat_color:
                self.wheat_count += 1
                rand = random.randint(0, 100)
                if rand < 90:
                    region.image.set_at(xy, c.harvested_field_color)
                else:
                    region.image.set_at(xy, c.harvested_wheat_color)

    def check_mines_and_bullets(self):
        # Update combain rect
        temp_rect = self.rect.copy()
        self.rect = self.game_rect.copy()

        regions_in_scope = self.get_regions_in_scope()

        # Get all mines in scope
        danger_in_scope = pygame.sprite.Group()

        for region in regions_in_scope:
            danger_in_scope.add(region.container['mine'])
            danger_in_scope.add(region.container['bullet'])

        if not danger_in_scope:
            self.rect = temp_rect
            return

        # Update rect of each mine
        for danger in danger_in_scope:
            danger.rect = danger.game_rect.copy()

        # Collide
        collided_danger = pygame.sprite.spritecollide(self, danger_in_scope, False)
        for danger in collided_danger:
            if danger.activated:
                danger.hit(self)

        self.rect = temp_rect

    def update_rect_size(self):
        image = self.comb_dict[self.direction]['animations'].getCurrentFrame()
        self.rect.size = image.get_size()

    def update_weapons(self):
        for weapon in self.weapons_dict.values():
            weapon.update()

    def draw(self, background):
        animation = self.comb_dict[self.direction]['animations']
        animation.blit(background, self.rect.topleft)


class EnemyCombain(Combain):
    def __init__(self, owner_id, **kwargs):
        Combain.__init__(self, owner_id, **kwargs)

    def update(self, key_pressed=None):
        # self.update_region()
        self.check_mines_and_bullets()


class Zhatka():
    def __init__(self):
        self.harvesting = False
