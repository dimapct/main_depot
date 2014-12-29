__author__ = 'dimapct'

from client import *
import sys


def main():
    client = Client()
    client.run_client()


if __name__ == '__main__':
    print(' --- Client started --- ')
    main()
    print(' --- Client finished --- ')