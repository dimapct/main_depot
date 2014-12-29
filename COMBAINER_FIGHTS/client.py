__author__ = 'dimapct'


import pygame
import sys
# Thread import
if sys.version[0] == '2':
    import thread
elif sys.version[0] == '3':
    import _thread as thread
import config as c
import gui
import socket as s
from game import Game
import game_tools as tools


class Client():
    def __init__(self):
        pygame.init()
        self.resources = self.load_all()
        self.server_socket = None
        self.client_static = self.initialize_client_objects()
        self.state = 'intro'
        self.listener = tools.Listener(separator=c.separator)
        self.sender = tools.Sender(separator=c.separator)
        self.socket = None
        self.nick = None
        self.id = None

    def run_client(self):
        while True:
            if self.state == 'intro':
                self.state = gui.run_intro()

            elif self.state == 'nick':
                if len(sys.argv) > 1:
                    self.nick = sys.argv[1]
                    self.state = 'lobby'
                else:
                    self.nick, self.state = gui.run_enter_nick(self.client_static)

                # Update nick when we get player nick
                self.listener.name = self.nick
                self.sender.name = self.nick

            elif self.state == 'lobby':
                self.socket = self.join_server()
                lobby = gui.Lobby(self.client_static, self.socket, self.nick, self.sender)
                # Run new listener and sender
                self.listener.socket = self.socket
                self.listener.queue = lobby.in_queue
                thread.start_new_thread(self.listener.start, ())

                # self.sender.socket = socket
                # self.sender.queue = lobby.out_queue
                # thread.start_new_thread(self.sender.start, ())

                self.state, self.id = lobby.run()
                # De-activate listener and sender in order to finish their threads
                # self.listener.working = False
                # self.sender.working = False

            elif self.state == 'game':
                game = Game(self.id, self.sender, self.nick, self.socket)
                self.listener.queue = game.in_queue
                # self.sender.queue = game.out_queue
                print('+++Game started!')
                self.state = game.run_game()
                print('+++Game exited with:', self.state)
                # De-activate listener and sender in order to finish their threads
                # self.listener.working = False
                # self.sender.working = False

            # Exit application directly from game
            elif self.state == 'client_exit':
                break

            else:
                raise NotImplementedError('Incorrect client state:', self.state)

    def join_server(self):
        try:
            socket = s.socket(s.AF_INET, s.SOCK_STREAM)
            socket.connect((c.server_host, c.server_port))
            # Send client's nick to server
            # message = {c.new_nick: self.nick}
            # socket.send(pickle.dumps(message, protocol=2))
            print('Connected to server')
            return socket

        except ConnectionRefusedError:
            print('!!! Connection to server refused')

    def initialize_client_objects(self):
        static_data = {'font_small': pygame.font.SysFont('comicsans', 8),
                       'font_big': pygame.font.SysFont('comicsans', 30),
                       'font_extra_big': pygame.font.SysFont('comicsans', 50),
                       'clock': pygame.time.Clock()}

        tools.create_screen(c.screen_length, c.screen_height, c.fullscreen)

        return static_data

    def load_all(self):
        resources = {}
        return resources
