__author__ = 'dimapct'


import socket as s
import pickle
import time

host = 'localhost'
port = 31224


socket = s.socket(s.AF_INET, s.SOCK_STREAM)
socket.connect((host, port))
print('Connected to server at', time.ctime())

message = b''
attempt = 0
size = int(1024 / 8)
while True:
    print('Attempt:', attempt)
    data = socket.recv(size)
    attempt += 1
    if not data:
        print('No data')
        continue

    print('Len data', len(data))
    # if b'.' in data:
    #     prev_message, ignore, next_message = data.partition(b'.')
    # print('Data:', data)
    obj = pickle.loads(data)
    print('Client got obj {0} at {1}, len: {2}'.format(obj, attempt, len(data)))
    print('--------------')


    # time.sleep(0.5)



