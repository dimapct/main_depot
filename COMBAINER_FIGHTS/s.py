__author__ = 'dimapct'

import _thread
import socket as s
import pickle
import pygame
import game_tools as t

host = ''
port = 31224

socket = s.socket(s.AF_INET, s.SOCK_STREAM)
socket.bind((host, port))
socket.listen(10)

def do():
    print('Do')
    while True:
        l = [325324 for i in range(1000000)]
        del l

for i in range(0):
    _thread.start_new_thread(do, ())

pygame.init()

def send_message(message, socket, i):
    print('!!!!!!!! sending message START !!!!!!!!!!!')
    a1 = pygame.time.get_ticks()
    byte_data = pickle.dumps(message)
    a = socket.send(byte_data)
    print('send {0} bytes'.format(a))
    a2 = pygame.time.get_ticks()
    print(i, a2-a1)
    print('------- sending message END ----------')


client_socket, address = socket.accept()
sender = t.Sender(socket=client_socket)

print('Client connected', address)
mes = {'game_xy': {1: (1234, 123), 2: (345, 342)}, 'dir': {1: 33, 2: 123}}
# mes = 1

for i in range(1000):
    sender.send_message(mes, client_socket)

