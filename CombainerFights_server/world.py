__author__ = 'dimapct'


import config as c
import mechanisms
import generator
import game_map as gm
from combain import Combain
import random
import bunker


class World():
    def __init__(self, waitresses):
        self.game_map = None
        self.combains_dict = {}
        self.waitresses = waitresses
        self.players_dict = {w: {} for w in waitresses}
        self.nps_dict = {'ships': {}}

    def create_world(self):
        self.create_game_map()
        generator.generate_nature(self.game_map)
        self.create_combains()
        self.create_nps()
        world_data = self.create_world_data()
        return world_data

    def create_game_map(self):
        self.game_map = gm.GameMap(c.game_field_size, c.region_size, c.cell_size)
        self.game_map.create_game_map()

    def create_combains(self):
        start_game_xys = self.calculate_start_game_xys()
        for waitress, start_game_xy in zip(self.waitresses.keys(), start_game_xys):
            # Randomize start xy
            owner = waitress
            combain = Combain(owner,
                              name='combain',
                              game_map=self.game_map,
                              game_xy=start_game_xy,
                              rotation_speed=c.comb_rotate_speed,
                              speed=c.comb_speed,
                              bunker_size=c.combain_bunker_size,
                              image_size=c.combain_image_size,
                              start_money=c.combain_start_money)
            # Format combain id in order to follow the convention
            combain.id = combain.id[0], combain.id[0]

            # Append combain to various lists
            self.players_dict[waitress][combain.id] = combain
            self.combains_dict[waitress] = combain

    def calculate_start_game_xys(self):
        xys = []
        count = len(self.waitresses)
        distance_between_combains = c.game_world_width / (count + 1)

        y = c.sea_height + 50
        for i in range(count):
            x = distance_between_combains + distance_between_combains * i
            xys.append((float(x), float(y)))

        random.shuffle(xys)
        return xys

    def create_world_data(self):
        world_data = {'game_world_size': {},
                      'region_data': {},
                      'user_list': {},
                      'nps': {'ships': {}}}

        world_data['game_world_size'] = {'game_field_size': c.game_field_size,
                                         'region_size': c.region_size,
                                         'cell_size': c.cell_size}

        for id, waitress in self.waitresses.items():
            world_data['user_list'][id] = {'nick': waitress.nick,
                                           'color': waitress.color,
                                           'team': waitress.team,
                                           'game_xy': self.combains_dict[id].game_rect.center}

        for region in self.game_map.regions:
            terrain_data = [[] for _ in range(len(region.cells_list))]
            for y in range(len(region.cells_list)):
                for cell in region.cells_list[y]:
                    terrain_data[y].append(cell.terrain)

            world_data['region_data'][region.coords] = terrain_data

        for id, ship in self.nps_dict['ships'].items():
            world_data['nps']['ships'].update({id: {'game_xy': ship.game_rect.center,
                                                    'speed': c.ship_speed}})

        return world_data

    def create_nps(self):
        self.create_ships()

    def create_ships(self):
        ship_count = c.ships_per_1000_pixels
        world_width = self.game_map.game_world_width
        step = world_width // (ship_count + 1)
        y = 500
        for i in range(ship_count):
            x = step + step * i
            game_xy = x, y
            ship = mechanisms.Ship(None,
                                   name='ship',
                                   state='swimming_to_buy',
                                   game_map=self.game_map,
                                   game_xy=game_xy,
                                   speed=c.ship_speed,
                                   bunker_size=c.ship_bunker_size,
                                   price=c.wheat_price,
                                   image_size=c.ship_image_size,
                                   sea_height=c.sea_height,
                                   buy_radius=c.ship_buy_radius,
                                   overlap=c.ship_overlap)

            self.nps_dict['ships'][ship.id] = ship

    def create_heap(self, amount, point, player_id, obj_id, owner):
        game_xy = bunker.Heap.get_game_xy(point, c.combain_image_size)
        image_size = max(int(amount/1000), 1)

        heap = bunker.Heap(amount,
                           None,
                           name='wheat',
                           id=obj_id,
                           game_owner=owner,
                           image_size=(image_size, image_size),
                           game_xy=game_xy,
                           game_map=self.game_map,
                           weight=amount)
        heap.accumulator = amount
        heap.rect = heap.game_rect

        self.players_dict[player_id][heap.id] = heap

        return heap
