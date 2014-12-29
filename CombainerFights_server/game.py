__author__ = 'dimapct'

import sys
# Thread import
if sys.version[0] == '2':
    import thread
    import Queue as queue
elif sys.version[0] == '3':
    import _thread as thread
    import queue
from game_map import *
from world import World
import game_tools as tools
from broadcaster import Broadcaster
import time
import pygame
import event_handler
import message_handler


class Game():
    def __init__(self, waitresses):
        self.in_queue = queue.Queue()
        self.waitresses = waitresses
        self.w = World(waitresses)
        self.broadcaster = Broadcaster(self.waitresses, tools.Sender(name='server', separator=c.separator))
        self.event_handler = event_handler.EventHandlerServer(self)
        self.message_handler = message_handler.MessageHandler(self.broadcaster)
        self.game_over = False
        self.out_MQ = None
        self.out_message_queue_lock = thread.allocate_lock()
        self.init_mq()

    def process_in_queue(self):
        print('Game started to process IN_Q')
        while not self.game_over:
            try:
                item = self.in_queue.get(block=False)
                # print('Server got:', item)
                waitress_id = list(item.keys())[0]
                waitress = self.waitresses[waitress_id]

                for event_type, message in item[waitress_id].items():
                    if event_type == c.client_game_message:
                        self.process_client_game_message(waitress_id, message)

                    elif event_type == c.start_data_loaded:
                        waitress.loaded = True

            except queue.Empty:
                # time.sleep(0.05)
                pass

    def process_nps_events(self):
        nps_events = self.event_handler.handle_nps_events(self.w.nps_dict['ships'])
        self.update_mq(nps_events)

    def process_client_game_message(self, waitress_id, message):
        player_events = self.event_handler.handle_player_events(waitress_id, message)
        self.update_mq(player_events)

    def update_mq(self, new_events):
        with self.out_message_queue_lock:
            for message_owner_id, events in new_events.items():
                owner_container = self.out_MQ[message_owner_id]
                for event in events:
                    for obj_id, event_data in event.items():
                        if obj_id in owner_container:
                            owner_container[obj_id].update(event_data)
                        else:
                            owner_container[obj_id] = event_data

    def run(self):
        thread.start_new_thread(self.process_in_queue, ())

        world_data = self.w.create_world()
        # time.sleep(1)
        self.broadcast_start_data(world_data)
        clock = pygame.time.Clock()
        self.wait_clients_to_load()

        self.event_handler.set_repeated_events(self.w.nps_dict['ships'])

        # *** KOSTIL for waiting players to create worlds
        # TO REDO to be dependant on world size
        time.sleep(2)
        t = clock.tick(c.distributions_per_second)
        dt = 0
        while True:
            self.update(dt)
            self.message_handler.distribute_changes(self.out_MQ, self.out_message_queue_lock)
            # print('FPS:', round(clock.get_fps(), 1))
            dt = clock.tick(c.distributions_per_second)
            t += dt

    def update(self, t):
        # Update NPS
        self.process_nps_events()
        for nps in self.w.nps_dict['ships'].values():
            nps.update(t)

    def broadcast_world_data(self, world_data):
        message = {'game_world_size': world_data['game_world_size']}
        self.broadcaster.broadcast_message(message)

        message = {'user_list': world_data['user_list']}
        self.broadcaster.broadcast_message(message)

        for coords, terrain_data in world_data['region_data'].items():
            message = {'region_data': {'coords': coords, 'terrain_data': terrain_data}}
            self.broadcaster.broadcast_message(message)

        message = world_data['nps']
        self.broadcaster.broadcast_message({'nps': message})

    def broadcast_start_data(self, world_data):
        self.broadcast_world_data(world_data)

    def wait_clients_to_load(self):
        # Wait for all client to load start data
        print('Server waits for all clients to load start data ...')
        while True:
            if all([client.loaded for client in self.waitresses.values()]):
                self.broadcaster.broadcast_message({c.main_loop_started: True})
                break
            time.sleep(0.3)
        print('Clients loaded all start data. GAME STARTED!')

    def init_mq(self):
        self.out_MQ = {w: {} for w in self.waitresses}
        self.out_MQ['nps'] = {}