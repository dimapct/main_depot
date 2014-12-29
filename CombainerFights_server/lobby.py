__author__ = 'dimapct'


import config as c
import sys
# Thread import
if sys.version[0] == '2':
    import thread
    import Queue as queue
elif sys.version[0] == '3':
    import _thread as thread
    import queue
import client_waitress
import time
from game_tools import Sender
import pickle
import pygame


class Lobby():
    def __init__(self, incoming_socket):
        self.incoming_socket = incoming_socket
        self.waitresses = {}
        self.in_queue = queue.Queue()
        self.sender = Sender(name='server', separator=c.separator)
        self.game_started = False
        self.waitress_lock = thread.allocate_lock()

    def run(self):
        clock = pygame.time.Clock()
        thread.start_new_thread(self.onboard_new_clients, ())
        thread.start_new_thread(self.process_in_queue, ())
        while not self.game_started:
            self.check_start_game()
            # time.sleep(3)
            clock.tick()
            # print('FPS:', clock.get_fps())
        else:
            return self.waitresses

    def check_start_game(self):
        with self.waitress_lock:
            ready = [client.ready_to_start for client in self.waitresses.values()]
        if ready and all(ready):
            self.start_game()

    def provide_color(self, id):
        return c.available_colors[id]

    def onboard_new_clients(self):
        # Waiting for new clients

        while not self.game_started:
            client_socket, address = self.incoming_socket.accept()

            # Get nick
            data = client_socket.recv(128)
            data = data.replace(c.separator, b'.')
            message = pickle.loads(data)
            nick = message[c.new_nick]+'_server'

            print('-- New client connected from: ', address)

            new_id = len(self.waitresses)
            color = self.provide_color(new_id)
            waitress = client_waitress.ClientWaitress(client_socket, self.waitresses, color, new_id, self, nick=nick)
            with self.waitress_lock:
                self.waitresses[new_id] = waitress
            # print('new waitress added', [(client.nick, client.id) for client in self.waitresses.values()])
            thread.start_new_thread(waitress.serve_forever, ())
            waitress.in_queue.put(message)
            self.sender.send_message({'id': waitress.id}, waitress.socket)

    def process_in_queue(self):
        while not self.game_started:
            try:
                item = self.in_queue.get(block=False)
                print('Server got:', item)

                waitress_id = list(item.keys())[0]
                waitress = self.waitresses[waitress_id]

                for event_type, event_value in item[waitress_id].items():

                    if event_type == c.new_nick:
                        self.process_new_nick(event_value, waitress)

                    elif event_type == c.color_change:
                        self.process_new_color(event_value, waitress)

                    elif event_type == c.team_change:
                        self.process_new_team(event_value, waitress)

                    elif event_type == c.quit_lobby:
                        self.process_client_quit(waitress)

                    elif event_type == c.ready_to_start:
                        self.process_ready_to_start(event_value, waitress)

                    else:
                        raise NotImplementedError(__name__, 'Incorrect event type', event_type)

            except queue.Empty:
                pass

    def process_ready_to_start(self, new_value, waitress):
        waitress.ready_to_start = new_value
        self.broadcast_user_list()

    def process_new_color(self, event_value, waitress):
        waitress.get_new_color(event_value)
        self.broadcast_user_list()

    def process_new_team(self, event_value, waitress):
        waitress.get_new_team(event_value)
        self.broadcast_user_list()

    def process_new_nick(self, new_nick, waitress):
        waitress.nick = new_nick
        self.broadcast_user_list()

    def process_client_quit(self, waitress):
        waitress.active = False
        waitress.listener.working = False
        # waitress.sender.working = False
        del self.waitresses[waitress.id]
        self.broadcast_user_list()

    def start_game(self):
        message = {c.game_started: None}
        self.broadcast_message(message)
        self.game_started = True
        print('Server decided to start game')

    def broadcast_user_list(self):
        message = self.get_new_user_list_message()
        self.broadcast_message(message)

    def broadcast_message(self, message):
        waitresses = self.waitresses.copy()
        for waitress in waitresses.values():
            self.sender.send_message(message, waitress.socket)

    def get_new_user_list_message(self):
        message = {'user_list': {client.id: {} for client in self.waitresses.values()}}
        for client_id in message['user_list']:
            # Wait for nick to arrive
            while self.waitresses[client_id].nick is None:
                time.sleep(0.1)

            # Enrich message
            message['user_list'][client_id]['nick'] = self.waitresses[client_id].nick
            message['user_list'][client_id]['color'] = self.waitresses[client_id].color
            message['user_list'][client_id]['team'] = self.waitresses[client_id].team
            message['user_list'][client_id]['ready_to_start'] = self.waitresses[client_id].ready_to_start

        return message