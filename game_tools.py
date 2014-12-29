__author__ = 'dimapct'

import pygame
from pygame.locals import *
import time
import os
import sys
if sys.version[0] == '2':
    import Queue as queue
elif sys.version[0] == '3':
    import queue
import pickle
import math


def get_all_from_q(q):
    items = []
    while True:
        try:
            item = q.get(block=False)
            items.append(item)
        except queue.Empty:
            break
    return items

def load_image(name, res_folder='', colorkey=None):
    fullname = os.path.join(res_folder, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print('Cannot load image:', fullname)
        raise SystemExit()
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image

def create_screen(screen_length, screen_height, fullscreen=False):
    """
    If fullscreen: get the current screen size of the computer
    """
    if fullscreen:
        info = pygame.display.Info()
        screen_length, screen_height = info.current_w, info.current_h
        pygame.display.set_mode((screen_length, screen_height), FULLSCREEN)
    else:
        pygame.display.set_mode((screen_length, screen_height))

def draw_fps(clock, font):
    screen = pygame.display.get_surface()
    fps = clock.get_fps()
    string = 'FPS:' + str(round(fps, 1))
    text = font.render(string, True, Color('white'))

    x = screen.get_width() - 55
    y = screen.get_height() - text.get_height()

    screen.blit(text, (x, y))


def get_all_from_in_q(q):
    items = []
    while True:
        try:
            item = q.get(block=False)
            items.append(item)
        except queue.Empty:
            break
    return items


class Listener():
    def __init__(self, name=None, socket=None, queue=None, separator=b'.'):
        self.name = name
        self.socket = socket
        self.queue = queue
        self.separator = separator

    def start(self):
        print('-- Listener started to listen in_q')
        remainder = b''
        while True:
            if self.queue is not None:
                data = self.socket.recv(256)
                # if 'server' in self.name:
                #    print('Listener got {0} bytes'.format(len(data)))
                # else:
                #    print('{0} Listener got {1} bytes'.format(self.name, len(data)))

                if not data:
                    print('Listener: no data')
                    break
                remainder = self.get_complete_messages(remainder+data)
            else:
                raise NotImplementedError('Listener cannot start as self.queue is None')

        print('Listener quit')

    def get_complete_messages(self, data):
        # print('------------')
        # print('{} data ='.format(self.name), data)
        if self.separator in data:
            # print('{} Separator YES'.format(self.name))
            try:
                message, end_of_file, next_part = data.partition(self.separator)
                # print('{0}: \n   prev {1},\n   eof {2},\n   next {3}'.format(self.name, previous_part, end_of_file, next_part))
                message += b'.'
                # print('{0} message before unpickling:'.format(self.name), message)

                obj = pickle.loads(message)
                # print('{0} putting object in queue => {1}'.format(self.name, obj))
                self.queue.put(obj)
            except EOFError:
                print('!!!+++!!! {} EOFError !!!+++!!!'.format(self.name))
                print('message:', message)
                print('next_part:', next_part)
                pass

            if self.separator in next_part:
                # print('{} Recursion started!!'.format(self.name))
                remainder = self.get_complete_messages(next_part)
                # print('{} Recursion ended :( !!'.format(self.name))
            else:
                # print('{} Ha!'.format(self.name))
                remainder = next_part

            return remainder

        else:
            return data


class Sender():
    def __init__(self, name=None, socket=None, queue=None, separator=b'.'):
        self.name = name
        self.socket = socket
        self.queue = queue
        self.working = False
        self.separator = separator
        self.bytes_count = 0

    def send_message(self, message, socket):
        # print('!!!!!!!! sending message START !!!!!!!!!!!')

        # if sep is None:
        #     separator = self.separator
        # else:
        #     separator = b'.'

        a1 = pygame.time.get_ticks()
        byte_data = pickle.dumps(message, protocol=2)
        byte_data = byte_data[:-1] + self.separator
        bytes_sent = socket.send(byte_data)
        self.bytes_count += bytes_sent
        a2 = pygame.time.get_ticks()
        # if 'server' in self.name:
        #print('Send time:', a2-a1, 'milisec')

        # print('!!!!!!!! sending message END !!!!!!!!!!!')

        # if 'server' in self.name:
        #     print('Sender sent {0} of {1} bytes'.format(message, bytes_sent))
        # else:
        #     print('{0} Sender sent {1} of {2} bytes'.format(self.name, message, bytes_sent))



class Vector2():
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __repr__(self):
        return str((self.x, self.y))

    def __str__(self):
        return 'Vector ({0} {1})'.format(self.x, self.y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __mul__(self, other):
        return Vector2(self.x * other, self.y * other)

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError('Index is out of range of the vector')

    @classmethod
    def from_points(cls, p1, p2):
        return cls(p2[0] - p1[0], p2[1] - p1[1])

    def get_lentgh(self):
        return math.sqrt(self.x**2 + self.y**2)

    def norm(self):
        length = self.get_lentgh()
        self.x /= length
        self.y /= length