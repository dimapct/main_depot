__author__ = 'dimapct'


import sys
if sys.version[0] == '2':
    import thread
    import Queue as queue
elif sys.version[0] == '3':
    import _thread as thread
    import queue
import time
from game_tools import Listener
import config as c


class ClientWaitress():
    def __init__(self, socket, waitresses, color, id, active_director=None, nick=None):
        print('-- New client started')
        self.socket = socket
        self.waitresses = waitresses
        self.active = True
        self.nick = nick
        self.active_director = active_director
        self.id = id
        self.color = color
        self.team = None
        self.ready_to_start = False
        self.client_actions_q = queue.Queue()
        self.loaded = False
        self.listener = Listener(name=self.nick, separator=c.separator)
        # self.sender = Sender()
        self.in_queue = queue.Queue()

    def serve_forever(self):
        print('-- Started serving client')
        self.listener.socket = self.socket
        self.listener.queue = self.in_queue
        thread.start_new_thread(self.listener.start, ())
        thread.start_new_thread(self.process_in_queue, ())

        # Main loop
        while self.active:
            time.sleep(10)

    def get_new_color(self, direction):
        color_index = c.available_colors.index(self.color)
        if direction == 'forward':
            next_color_index = color_index + 1
            if not next_color_index < len(c.available_colors):
                next_color_index = 0
        elif direction == 'back':
            next_color_index = color_index - 1

        else:
            raise NotImplementedError('Incorrect direction', direction)

        self.color = c.available_colors[next_color_index]

    def get_new_team(self, direction):
        team_index = c.available_teams.index(self.team)
        if direction == 'forward':
            next_team_index = team_index + 1
            if not next_team_index < len(c.available_teams):
                next_team_index = 0
        elif direction == 'back':
            next_team_index = team_index - 1
        else:
            raise NotImplementedError('Incorrect direction', direction)

        self.team = c.available_teams[next_team_index]

    def process_in_queue(self):
        while self.active:
            try:
                item = self.in_queue.get(block=False)
                # print('Client waitress #{0} got message {1}'.format(self.id, item))
                message = {self.id: item}
                self.active_director.in_queue.put(message, block=False)
            except queue.Empty:
                time.sleep(0.02)


