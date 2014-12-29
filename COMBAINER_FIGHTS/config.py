__author__ = 'dimapct'

import string
from pygame.locals import *


# Server data
server_host = '185.25.119.112'
server_host = 'localhost'
server_port = 31224

separator = b'kitti'
other_player_frames_buffer = 2

# Game data
game_name = 'Combainer Fights'
menu_fps = 10
game_fps = 60
res_folder = 'res'

# Screen data
screen_length = 800
screen_height = 500
fullscreen = False

# GUI texts
enter_your_nick_text = "Введіть ігрове ім'я: "
start_game_text = 'Почати гру <Enter>'
exit_text = 'Вийти <Esc> '
lobby_player_list_text = 'Гравців на сервері: '
lobby_name = 'Server Lobby'
cyryllic_chars = 'абвгдеєжзиійїклмнопрстуфхцчшщфюяёэыъь'
allowed_chars = string.ascii_letters + \
                string.digits + \
                ' ' + \
                cyryllic_chars + cyryllic_chars.upper()


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
wheat_report_frequency = 300  # mls

# Game events
changed_direction = USEREVENT
changed_position = USEREVENT + 1
toggled_zhatka = USEREVENT + 2
wheat_count_changed = USEREVENT + 3
dropped = USEREVENT + 4
to_check_wheat_to_report = USEREVENT + 7

no_need_to_send_events = (to_check_wheat_to_report,)

# Functional keys
forward = 10
backward = 11
left = 12
right = 13
toggle_zhatka = 14
fire_gun = 15
set_mine = 16
direction_arrows = (left, right)
position_arrows = (forward, backward)


# Main config
directions = ['up', 'down', 'left', 'right']
directions_diagonal = ['dl', 'dr', 'ul', 'ur']

# Terrains
meadow = 1
sea = 2
wheat = 3
forest = 4

# Combain params
combain_hp = 100
combain_speed = 100. / 1000  # pixels / millisecond
combain_armor = 0
max_degrees = 360
combain_raw_color = (255, 174, 201, 255)
zhatka_colors = ((127, 127, 127, 255), (200, 191, 231))
harvested_field_color = (100, 50, 0, 255)
wheat_color = Color('yellow')
harvested_wheat_color = wheat_color - (1, 1, 1, 0)
wheat_in_heap_color = wheat_color + (1, 1, 1, 0)
combain_rotation_speed = 360. / 5 / 1000  # degrees / millisecond
bullet_image_size = 1
bullet_speed = 10.
bullet_damage = 3
mine_damage = 70
bullet_activation_time = 200  # milliseconds
mine_activation_time = 5000  # milliseconds
combain_bunker_size = 10 * 1000  # kg
wheat_pixel_cost = 1  # g


