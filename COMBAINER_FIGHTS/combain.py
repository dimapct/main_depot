__author__ = 'dimapct'

import pygame
from pygame.locals import *
import game_object
import random
import game
from game_tools import Vector2
import config as c
import bunker


class Combain(game_object.GameObject):
    def __init__(self, owner_id, **kwargs):
        game_object.GameObject.__init__(self, owner_id, **kwargs)
        self.comb_dict = kwargs.get('comb_dict')
        self.comb_dict['conductor'].play()
        self.comb_dict['conductor'].pause()
        self.update_rect_size()
        combain_bunker_size = kwargs.get('bunker_size')
        self.bunker = bunker.Bunker(combain_bunker_size, name='bunker')
        self.zhatka = Zhatka(self)
        self.weapons_dict = dict()
        self.wheat_to_report = 0

    def update(self, t):
        self.zhatka.get_harvest_and_report()

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

    def update_image(self):
        self.image = self.comb_dict[self.direction]['animations'].getCurrentFrame()

    def update_rect_size(self):
        self.update_image()
        self.rect.size = self.image.get_size()

    def update_weapons(self):
        for weapon in self.weapons_dict.values():
            weapon.update()

    def draw(self, background):
        animation = self.comb_dict[self.direction]['animations']
        animation.blit(background, self.rect.topleft)
        # print('Drawing combain on {0} game_xy'.format(self.game_rect.center))


class OtherCombain(Combain):
    def __init__(self, owner_id, **kwargs):
        Combain.__init__(self, owner_id, **kwargs)
        print('Client created OTHER COMBAIN')

    def update(self, t):
        self.update_rotation_with_interpolation(t)
        self.update_direction()
        self.update_rect_size()
        self.update_position_with_interpolation(t)
        self.update_region()
        self.zhatka.get_harvest()


class Zhatka():
    def __init__(self, combain):
        self.combain = combain
        self.bunker = combain.bunker
        self.harvesting = False

    def get_harvest_and_report(self):
        if self.harvesting and self.bunker.has_space():
            point = self.combain.game_rect.center
            wheat_count = 0
            for offset in self.combain.comb_dict[self.combain.direction]['zhatka']:
                x = point[0] - offset[0]
                y = point[1] - offset[1]

                # Check for game boundary
                if not 0 <= x < self.combain.game_map.game_world_width \
                        or not 0 <= y < self.combain.game_map.game_world_height:
                    continue

                region, xy = self.combain.game_map.get_region_and_xy((x, y))

                if region.image.get_at(xy) == c.wheat_color:
                    wheat_count += c.wheat_pixel_cost

                    rand = random.randint(0, 100)
                    if rand < 90:
                        region.image.set_at(xy, c.harvested_field_color)
                    else:
                        region.image.set_at(xy, c.harvested_wheat_color)

            # Handle situation when we put more wheat into bunker then its size
            prev_bunker_amount = self.bunker.accumulator
            self.bunker += wheat_count
            delta = self.bunker.accumulator - prev_bunker_amount
            self.combain.wheat_to_report += delta

    def get_harvest(self):
        if self.harvesting and self.bunker.has_space():
            point = self.combain.game_rect.center
            wheat_count = 0
            for offset in self.combain.comb_dict[self.combain.direction]['zhatka']:
                x = point[0] - offset[0]
                y = point[1] - offset[1]

                # Check for game boundary
                if not 0 <= x < self.combain.game_map.game_world_width \
                        or not 0 <= y < self.combain.game_map.game_world_height:
                    continue

                region, xy = self.combain.game_map.get_region_and_xy((x, y))

                if region.image.get_at(xy) == c.wheat_color:
                    wheat_count += c.wheat_pixel_cost

                    rand = random.randint(0, 100)
                    if rand < 90:
                        region.image.set_at(xy, c.harvested_field_color)
                    else:
                        region.image.set_at(xy, c.harvested_wheat_color)