__author__ = 'dimapct'

from server import *


def main():
    server = Server()
    server.run_server()


if __name__ == '__main__':
    print(' --- Server started --- ')
    main()
    print(' --- Server finished --- ')