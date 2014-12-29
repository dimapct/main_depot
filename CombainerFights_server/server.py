__author__ = 'dimapct'


import socket as s
from lobby import Lobby
from game import Game


class Server():
    def __init__(self):
        pass

    @staticmethod
    def run_server():
        host = ''
        port = 31224
        socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        socket.bind((host, port))
        socket.listen(10)

        while True:
            client_waitresses = Lobby(socket).run()

            game = Game(client_waitresses)
            for waitress in client_waitresses.values():
                waitress.active_director = game
            game.run()