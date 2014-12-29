__author__ = 'dimapct'


import pygame
from pygame.locals import *
import pyganim
import game_map
from combain import Combain, OtherCombain
import config as c
import mechanisms


class World():
    def __init__(self, start_data, id):
        self.game_map = None
        self.id = id
        self.players_dict = {}
        self.combains_dict = {}
        self.nps_dict = {}
        self.start_data = start_data
        self.create_world(self.start_data)

    def create_world(self, start_data):
        self.create_game_map(start_data)

    def create_game_map(self, start_data):
        game_world_size = start_data['game_field_size']
        region_size = start_data['region_size']
        cell_size = start_data['cell_size']
        self.game_map = game_map.GameMap(game_world_size, region_size, cell_size)
        self.game_map.create_game_map()

    def process_region_data(self, region_data):
        reg_x, reg_y = region_data['coords']
        terrain_data = region_data['terrain_data']
        region = self.game_map.regions_list[reg_y][reg_x]

        for y in range(len(terrain_data)):
            for x in range(len(terrain_data[y])):
                value = terrain_data[y][x]
                region.cells_list[y][x].assign_terrain(value)

    def create_players(self, players_data, combain_images):
        print('Players #{0} data {1}'.format(self.id, players_data))
        for player_id, data in players_data.items():
            new_images = [image.copy() for image in combain_images]
            color = data['color']
            comb_dict = self.generate_combain_dict(new_images, color)
            start_game_xy = data['game_xy']
            bunker_size = c.combain_bunker_size
            if player_id == self.id:
                combain = Combain(player_id, name='combain', hp=c.combain_hp, speed=c.combain_speed, armor=c.combain_armor,
                                  game_map=self.game_map, comb_dict=comb_dict, game_xy=start_game_xy, image=new_images[0],
                                  rotation_speed=c.combain_rotation_speed, bunker_size=bunker_size, image_size=(1, 1))
            else:
                combain = OtherCombain(player_id, name='combain', hp=c.combain_hp, speed=c.combain_speed, armor=c.combain_armor,
                                       game_map=self.game_map, comb_dict=comb_dict, game_xy=start_game_xy, image=new_images[0],
                                       rotation_speed=c.combain_rotation_speed, bunker_size=bunker_size, image_size=(1, 1))

            # Format combain id in order to follow the convention
            combain.id = combain.id[0], combain.id[0]

            self.players_dict[player_id] = {combain.id: combain}
            self.combains_dict[player_id] = combain

            # if player_id != self.id:
            region, xy = self.game_map.get_region_and_xy(combain.game_position)
            region.container['combain'].add(combain)

    def assign_player_color(self, image, color):
        for y in range(image.get_height()):
            for x in range(image.get_width()):
                if image.get_at((x, y)) == c.combain_raw_color:
                    image.set_at((x, y), color)

    def generate_combain_dict(self, combain_images, col):
        for im in combain_images:
            self.assign_player_color(im, col)

        indices = range(c.max_degrees)
        comb_dict = {i: {'animations': None, 'zhatka': None} for i in indices}
        animation_speeds = [0.1] * len(combain_images)
        animations_list = list(zip(combain_images, animation_speeds))

        # Generate combain images
        for i in range(c.max_degrees):
            animation = pyganim.PygAnimation(animations_list)
            animation.rotate(i)
            comb_dict[i]['animations'] = animation

        # Generate combain zhatka pixels
        for degree in comb_dict:
            anim = comb_dict[degree]['animations']
            im = anim.getFrame(0)
            rect = im.get_rect()
            offsets = list()
            for x in range(im.get_width()):
                for y in range(im.get_height()):
                    colour = im.get_at((x, y))
                    if colour in c.zhatka_colors:
                        dx = rect.centerx - x
                        dy = rect.centery - y
                        offsets.append((dx, dy))
            comb_dict[degree]['zhatka'] = tuple(offsets)

        comb_dict['conductor'] = pyganim.PygConductor([comb_dict[dirr]['animations'] for dirr in comb_dict.keys()])

        return comb_dict

    def create_nps(self, nps_data, nps_images):
        self.create_ships(nps_data['ships'], nps_images['ship_image'])

    def create_ships(self, ships_data, ship_image):
        for id, ship_data in ships_data.items():
            ship = mechanisms.Ship(None,
                                   id=id,
                                   name='ship',
                                   game_map=self.game_map,
                                   game_xy=ship_data['game_xy'],
                                   speed=ship_data['speed'],
                                   image=ship_image,
                                   )
            region, xy = self.game_map.get_region_and_xy(ship.game_position)
            region.container['ship'].add(ship)
            self.nps_dict[id] = ship
            print('SHIP created', ship.game_position, ship.rect)



