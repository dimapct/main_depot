__author__ = 'dimapct'


import os


files_to_send = [r'D:\PycharmProjects_copy\CombainerFights_server\server.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\client_waitress.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\config.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\lobby.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\main.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\game_map.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\event_handler.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\message_handler.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\generator.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\game.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\world.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\game_object.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\combain.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\weapon.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\bunker.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\mechanisms.py',
                 r'D:\PycharmProjects_copy\CombainerFights_server\broadcaster.py',
                 r'C:\Python33\Lib\site-packages\game_tools.py']
target = '/usr/games/c'

# files_to_send = [r'C:\Python33\Lib\site-packages\pygame\math.pyd']
# target = '/usr/lib/python2.7'

files_to_send = list(map(lambda x: x + ' ', files_to_send))

file_paths = ''
for s in files_to_send:
    file_paths += s

login = 'root'
server_address = '185.25.119.112'

command = 'pscp ' + '-pw Pickandroll1 ' + file_paths + login + '@' + server_address + ':' + target

os.system(command)
