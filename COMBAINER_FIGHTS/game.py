__author__ = 'dimapct'


import pygame
from pygame.locals import *
import sys
import game_tools as tools
import queue
import world
import _thread as thread
import config as c
import time
import camera
import background_manager as bm
import event_handler
from message_handler import MessageHandler


class Game():
    def __init__(self, id, sender, nick, socket):
        self.event_handler = None
        self.message_handler = None
        self.in_queue = queue.Queue()
        self.game_static = self.initialize_game_objects()
        self.resources = {}
        self.load_all()
        self.camera = None
        self.bm = None
        self.id = id
        self.socket = socket
        self.nick = nick
        self.sender = sender
        self.game_over = False
        self.loaded = {'regions': False, 'user_list': False, 'nps': False}
        self.regions_loaded = 0
        self.start_game = False
        self.w = None
        self.my_combain = None
        self.all_combains = None
        self.background_manager = None
        self.stdout_lock = thread.allocate_lock()

    def run_game(self):
        clock = self.game_static['clock']
        thread.start_new_thread(self.process_in_q, ())
        print('{} loading start data ...'.format(self.nick))
        self.wait_for_loading_all_start_data()
        print('{} loading resources ...'.format(self.nick))

        print('{} loaded start data. Waiting for other players'.format(self.nick))
        self.wait_for_other_clients()
        print('{}: Everybody is ready! GAME STARTED!'.format(self.nick))

        self.create_initial_objects()

        # ----------------- MAIN LOOP ---------------- ####
        t = 0
        dt = 0
        while not self.game_over:
            # if self.id == 0:
            #     print(123, self.sender.bytes_count)
            # elif self.id == 1:
            #     print(345, self.sender.bytes_count)
            self.update(dt)
            self.draw()
            dt = clock.tick(c.game_fps)
            t += dt
        else:
            return 'lobby'

    def update(self, t):
        # print(666, self.my_combain.rotation)

        # Handle input events
        events = self.event_handler.handle_user_events()

        # Handle per-frame events
        for player_container in self.w.players_dict.values():
            for obj in player_container.values():
                obj.update(t)
        for nps in self.w.nps_dict.values():
            nps.update(t)

        # Send events
        if events:
            message = MessageHandler.get_message(events, t)
            self.sender.send_message(message, self.socket)

    def draw(self):
        font_small = self.game_static['font_small']
        font_big = self.game_static['font_big']
        screen = pygame.display.get_surface()

        self.background_manager.update()
        screen.fill(Color('black'))

        for spr in self.background_manager.container:
            spr.draw(self.background_manager.background)

        # for ship in self.w.nps_dict.values():
        #     self.background_manager.background.blit(ship.image, ship.rect.topleft)

        screen.blit(self.background_manager.background, self.background_manager.background_offset)

        text_wheat = font_big.render('Wheat ' + str(self.my_combain.bunker.accumulator), True, Color('white'))
        text_hp = font_big.render('HP ' + str(self.my_combain.hp), True, Color('white'))

        screen.blit(text_wheat, (5, 5))
        screen.blit(text_hp, (5, 35))
        tools.draw_fps(self.game_static['clock'], font_small)

        pygame.display.flip()

    def create_initial_objects(self):
        self.event_handler = event_handler.EventHandler(self)
        self.message_handler = MessageHandler()
        self.my_combain = self.w.combains_dict[self.id]
        self.all_combains = pygame.sprite.Group(list(self.w.combains_dict.values()))
        self.camera = camera.Camera(self.my_combain)
        self.background_manager = bm.BackgroundManager(self.w.game_map,
                                                       self.my_combain,
                                                       self.camera,
                                                       self.w.start_data['region_size'],
                                                       self.w.game_map.cell_size,
                                                       self.nick)
        # Set events
        self.event_handler.set_repeated_events()

    def process_in_q(self):
        print('Client in_q processing started')
        while not self.game_over:
            try:
                item = self.in_queue.get(block=False)
                # print('Client in_q processing item {}'.format(item))
                for key, value in item.items():

                    if key == c.client_game_message:
                        # KOSTIL to wait until event handler is created
                        # while True:
                        #     if self.event_handler is not None:
                        self.event_handler.process_server_message(value)
                                # break

                    elif key == 'game_world_size':
                        print('Client got game world size')
                        self.create_world(value)

                    elif key == 'region_data':
                        print('Client got region_data')
                        # Wait for world creation
                        while True:
                            if self.w is not None:
                                self.w.process_region_data(value)
                                # Check for all regions to be loaded
                                self.regions_loaded += 1
                                if self.regions_loaded == len(self.w.game_map.regions):
                                    self.loaded['regions'] = True
                                    # del self.regions_loaded
                                break

                    elif key == 'user_list':
                        print('Client got user_list')
                        # Wait for world creation
                        while True:
                            if self.w is not None:
                                self.w.create_players(value, self.resources['combain_images'])
                                self.loaded['user_list'] = True
                                break

                    elif key == 'nps':
                        while True:
                            if self.w is not None:
                                self.w.create_nps(value, self.resources['nps_images'])
                                self.loaded['nps'] = True
                                break

                    elif key == c.main_loop_started:
                        self.start_game = True

                    else:
                        pass
                        # raise NotImplementedError('Unknown message type')

            except queue.Empty:
                time.sleep(0.03)

        print('{} IN_Q exit'.format(self.nick))

    def create_world(self, game_world_size):
        self.w = world.World(game_world_size, self.id)
        print('{0} world created!'.format(self.nick))

    def wait_for_loading_all_start_data(self):
        while True:
            # print(self.loaded)
            if all(self.loaded.values()):
                self.sender.send_message({c.start_data_loaded: True}, self.socket)
                break
            time.sleep(0.3)
        del self.loaded

    def wait_for_other_clients(self):
        while not self.start_game:
            time.sleep(0.3)
        del self.start_game

    def load_all(self):
        self.resources['combain_images'] = [tools.load_image('combain1.png', c.res_folder),
                                            tools.load_image('combain2.png', c.res_folder),
                                            tools.load_image('combain3.png', c.res_folder)]
        [image.set_colorkey((255, 255, 255, 255)) for image in self.resources['combain_images']]
        self.resources['nps_images'] = {'ship_image': tools.load_image('ship.png', c.res_folder, colorkey=-1)}

    # def create_game_message_event(self, message):
    #     event = pygame.event.Event(c.other_player_update, message=message)
    #     pygame.event.post(event)
        # print('{0} create game message event: {1}'.format(self.nick, message))

    @staticmethod
    def initialize_game_objects():
        game_static = {'font_small': pygame.font.SysFont('comicsans', 16),
                       'font_big': pygame.font.SysFont('comicsans', 30),
                       'font_extra_big': pygame.font.SysFont('comicsans', 50),
                       'clock': pygame.time.Clock()}

        return game_static