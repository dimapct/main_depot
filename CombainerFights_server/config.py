__author__ = 'dimapct'


from pygame.locals import *

blue = (0, 51, 204)
orange = (186, 118, 18)
pink = (178, 26, 38)
purple = (128, 0, 128)
white = (254, 254, 254)
black = (0, 0, 0)
red = (200, 0, 0)
color1 = (175, 171, 16)
color2 = (255, 128, 0)
color3 = (128, 128, 255)

separator = b'kitti'

available_colors = (blue, orange, pink, purple, white, black, red, color1, color2, color3) * 2
available_teams = (None, 1, 2, 3, 4, 5, 6, 7)

distributions_per_second = 60

# Lobby events mapping
new_nick = 10
color_change = 20
team_change = 30
chat_entered = 40
ready_to_start = 50
quit_lobby = 60
game_started = 70
start_data_loaded = 80
client_game_message = 85
main_loop_started = 90

# Game messages mapping
timestamp = 1
client_prediction = 2
events = 3
position = 4
direction = 5
new_object_born = 6

# Repeated events
ship_report_frequency = 300  # mls

# Game events
changed_direction = USEREVENT
changed_position = USEREVENT + 1
toggled_zhatka = USEREVENT + 2
wheat_count_changed = USEREVENT + 3
dropped = USEREVENT + 4
ship_bought = USEREVENT + 5
broadcast_ship_updates = USEREVENT + 7

# Functional keys
forward = 10
backward = 11
left = 12
right = 13
arrow_events = {forward, backward, left, right}
toggle_zhatka = 14
fire_gun = 15
set_mine = 16

lobby_message_template = {'nick': None, 'color': None, 'team': None, 'ready_to_start': None}


# Main config
name = 'Combiner Fights'
# fps = 60
game_field_size = (1, 4)  # regions per map (columns, rows)
region_size = (50, 51)  # cells per region (columns, rows)
cell_size = 20  # always square, pixels
region_width = region_size[0] * cell_size
region_height = region_size[1] * cell_size
game_world_width = game_field_size[0]*region_size[0]*cell_size  # pixel
game_world_height = game_field_size[1]*region_size[1]*cell_size  # pixel
directions = ['up', 'down', 'left', 'right']
directions_diagonal = ['dl', 'dr', 'ul', 'ur']
bullet_speed = 10.
bullet_damage = 3
mine_damage = 70
bullet_activation_time = 200  # milliseconds
mine_activation_time = 5000  # milliseconds

print('Game World size:', game_world_width, game_world_height)

# Terrains
meadow = 1
sea = 2
wheat = 3
forest = 4

# Forests
big_forest_density = 0.10  # square of big forests in the world / world square
big_forest_size = 1000  # number of cells in the big forest
small_forest_density = 0.20  # percentage of small forests in the world
small_forest_size = 200  # number of cells in the small forest


world_data_template = {'game_world_size': {'game_field_size': 0,
                                           'region_size': 0,
                                           'cell_size': 0},
                       'region_data': {'coords': []},
                       'user_list': {'id': {'nick': 0, 'color': 0, 'team': 0, 'game_xy': 0}}}

# WHEAT
harvested_field_color = (100, 50, 0, 255)
wheat_color = Color('yellow')
harvested_wheat_color = (wheat_color[0]-1, wheat_color[1]-1, wheat_color[2]-1, wheat_color[3]-0)
wheat_pixel_cost = 1  # kg
wheat_price = 1  # UAH / kg


#   --------------------    MECHANISMS    ----------------------
#   SHIP
sea_height = 1000
ships_per_1000_pixels = 1
ship_speed = 30.0 / 1000  # pixels / millisecond
ship_bunker_size = 30 * 1000  # kg
ship_image_size = (156, 369)
ship_buy_radius = 100
ship_overlap = 30

#   COMBAIN
combain_bunker_size = 10 * 1000  # kg
comb_speed = 100.0 / 1000  # pixels / millisecond
comb_rotate_speed = 360.0 / 5 / 1000  # degrees / millisecond
combain_image_size = (30, 30)
combain_start_money = 0

#   ZHATKA
zhatka_colors = ((127, 127, 127, 255), (200, 191, 231))