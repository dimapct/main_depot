__author__ = 'dimapct'


import os
import _thread
import time

players_count = 2

main_filepath = r'D:\PycharmProjects_copy\COMBAINER_FIGHTS\main.py '

names = ('dima', 'Зорян', 'roma', 'stas', 'luda', 'ka4ka', '12345', 'babax', 'zhaba', 'Аргентум', 'стогін', 'бойкот')

# names = [name + '2' for name in names]

for player in range(players_count):
    command = 'python ' + main_filepath + names[player]
    _thread.start_new_thread(os.system, (command,))
    # time.sleep(1)

while True:
    time.sleep(10)