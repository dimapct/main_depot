__author__ = 'dimapct'

import pygame
from pygame.locals import *
import config as c
import sys
import bunker


class EventHandler():
    def __init__(self, boss):
        self.boss = boss
        self.world = boss.w
        self.inputs = {c.forward: ButtonHandler(c.forward),
                       c.backward: ButtonHandler(c.backward),
                       c.left: ButtonHandler(c.left),
                       c.right: ButtonHandler(c.right),
                       c.toggle_zhatka: ButtonHandler(c.toggle_zhatka),
                       c.fire_gun: ButtonHandler(c.fire_gun),
                       c.set_mine: ButtonHandler(c.set_mine)}

    def handle_user_events(self):
        # Process KEYDOWN, KEYUP, QUIT events
        self.process_keyboard_input()

        # Process USER events
        all_events = pygame.event.get()

        for event in all_events:
            if event.type == c.changed_direction:
                self.process_dir_change(event.data)

            elif event.type == c.changed_position:
                self.process_pos_change(event.data)

            elif event.type == c.toggled_zhatka:
                self.process_toggle_zhatka()

            elif event.type == c.to_check_wheat_to_report:
                self.check_wheat_to_report()

            elif event.type == c.wheat_count_changed:
                pass

            elif event.type == c.dropped:
                heap = self.process_dropped(self.boss.my_combain.id, self.boss.my_combain.id[0])
                event.obj_id = heap.id

        events_to_send = [e for e in all_events
                          if e.type >= USEREVENT
                          and e.type not in c.no_need_to_send_events]
        return events_to_send

    def process_server_message(self, message):
        self.process_other_player_update(message)
        self.process_nps(message)

    def process_nps(self, message):
        world = self.boss.w
        if 'nps' in message:
            for obj_id, events in message['nps'].items():
                    obj = world.nps_dict[obj_id]

                    for event_type, event_info in events.items():

                        # POSITION
                        if event_type == c.changed_position:
                            print('client got SHIP at', event_info)
                            self.process_pos_change_other(obj, event_info)

                        # SHIP BOUGHT WHEAT
                        elif event_type == c.ship_bought:
                            self.process_wheat_sell(event_info)

    def process_other_player_update(self, message):
        world = self.boss.w
        for player_id, data in message.items():
            if player_id in world.players_dict:
                for event_owner_id, events in data.items():
                    obj = world.players_dict[player_id][event_owner_id]

                    for event_type, event_info in events.items():

                        # DIRECTION
                        if event_type == c.changed_direction:
                            self.process_dir_change_other(obj, event_info)

                        # POSITION
                        elif event_type == c.changed_position:
                            self.process_pos_change_other(obj, event_info)

                        # TOGGLE ZHATKA
                        elif event_type == c.toggled_zhatka:
                            self.process_toggle_zhatka_other(obj)

                        # WHEAT CHANGE
                        elif event_type == c.wheat_count_changed:
                            self.wheat_count_changed_other(obj, event_info)

                        # WHEAT DROP
                        elif event_type == c.dropped:
                            weight = event_info[0]
                            xy = event_info[1]
                            id = event_info[2]
                            self.process_dropped(event_owner_id,
                                                 player_id,
                                                 amount=weight,
                                                 xy=xy,
                                                 id=id)

    def set_repeated_events(self):
        # Set wheat_report timer
        pygame.time.set_timer(c.to_check_wheat_to_report, c.wheat_report_frequency)

    def process_keyboard_input(self):
        changed_direction = False
        changed_position = False
        toggled_zhatka = False
        drop = False

        # QUIT
        if pygame.event.get(QUIT):
            sys.exit('Client exit')

        # KEYDOWN
        for event in pygame.event.get(KEYDOWN):
            if event.key == K_ESCAPE:
                self.boss.game_over = True

            elif event.key == K_UP:
                self.inputs[c.forward].process_keydown()
                changed_position = True

            elif event.key == K_DOWN:
                self.inputs[c.backward].process_keydown()
                changed_position = True

            elif event.key == K_LEFT:
                self.inputs[c.left].process_keydown()
                changed_direction = True

            elif event.key == K_RIGHT:
                self.inputs[c.right].process_keydown()
                changed_direction = True

            elif event.key == K_o:
                toggled_zhatka = True
                # self.inputs[c.toggle_zhatka].process_keydown()

            elif event.key == K_SPACE:
                self.inputs[c.fire_gun].process_keydown()

            elif event.key == K_x:
                self.inputs[c.set_mine].process_keydown()

            elif event.key == K_d:
                drop = True
                # self.inputs[c.].process_keydown()

        # KEYUP
        for event in pygame.event.get(KEYUP):
            if event.key == K_UP:
                self.inputs[c.forward].process_keyup()

            elif event.key == K_DOWN:
                self.inputs[c.backward].process_keyup()

            elif event.key == K_LEFT:
                self.inputs[c.left].process_keyup()

            elif event.key == K_RIGHT:
                self.inputs[c.right].process_keyup()

        # Increment time pressed if no KEYUP event
        now = pygame.time.get_ticks()
        for key, button in self.inputs.items():
            if button.pressed:
                button.increment_time_pressed(now)
                if key in c.position_arrows:
                    changed_position = True
                elif key in c.direction_arrows:
                    changed_direction = True

        # Generate events and put them back to the event queue
        owner = self.boss.my_combain.id
        if changed_direction:
            buttons = {c.left: self.inputs[c.left].time_pressed,
                       c.right: self.inputs[c.right].time_pressed,
                       c.forward: self.inputs[c.forward].time_pressed,
                       c.backward: self.inputs[c.backward].time_pressed}
            event = pygame.event.Event(c.changed_direction, owner_id=owner, data=buttons)
            pygame.event.post(event)

        if changed_position:
            buttons = {c.forward: self.inputs[c.forward].time_pressed,
                       c.backward: self.inputs[c.backward].time_pressed}
            event = pygame.event.Event(c.changed_position, owner_id=owner, data=buttons)
            pygame.event.post(event)

        if toggled_zhatka:
            event = pygame.event.Event(c.toggled_zhatka, owner_id=owner)
            pygame.event.post(event)

        if drop:
            amount = self.boss.my_combain.bunker.accumulator
            if amount:
                xy = self.boss.my_combain.game_rect.center
                data = amount, xy
                event = pygame.event.Event(c.dropped, owner_id=owner, data=data)
                pygame.event.post(event)

        # Nullify buttons time pressed
        [self.inputs[button].nullify() for button in c.direction_arrows + c.position_arrows]

    def process_dir_change(self, buttons):
        combain = self.boss.my_combain
        combain.update_rotation(buttons)
        combain.update_rect_size()

    def process_pos_change(self, buttons):
        combain = self.boss.my_combain
        combain.update_position(buttons)
        combain.update_region()

    def process_toggle_zhatka(self):
        combain = self.boss.my_combain
        combain.zhatka.harvesting = not combain.zhatka.harvesting
        combain.comb_dict['conductor'].togglePause()

    def check_wheat_to_report(self):
        wheat_to_report = self.boss.my_combain.wheat_to_report
        if wheat_to_report:
            event = pygame.event.Event(c.wheat_count_changed,
                                       owner_id=self.boss.my_combain.id,
                                       data=wheat_to_report)
            pygame.event.post(event)
            self.boss.my_combain.wheat_to_report = 0

    def process_dropped(self, owner_id, player_id, amount=None, xy=None, id=None):
        obj = self.world.players_dict[player_id][owner_id]
        if amount is None:
            weight = obj.bunker.accumulator
        else:
            weight = amount

        if weight:
            obj.bunker.accumulator = 0
            heap_size = weight
            if xy is None:
                game_xy = bunker.Heap.get_game_xy(obj.game_rect.center, obj.game_rect.size)
            else:
                game_xy = xy
            image_size = max(int(weight/1000), 1)
            image = pygame.Surface((image_size, image_size))
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
            rect = image.get_rect()
            pygame.draw.circle(image, c.wheat_in_heap_color, rect.center, image_size//2)
            if id is None:
                # Create self heap
                heap = bunker.Heap(heap_size,
                                   player_id,
                                   name='wheat',
                                   game_map=self.world.game_map,
                                   game_xy=game_xy,
                                   image=image,
                                   weight=weight)
            else:
                # Create heap for other combains
                heap = bunker.Heap(heap_size,
                                   player_id,
                                   id=id,
                                   name='wheat',
                                   game_map=self.world.game_map,
                                   game_xy=game_xy,
                                   image=image,
                                   weight=weight)
            self.world.players_dict[player_id][heap.id] = heap
            obj.bunker.accumulator = 0
            return heap

    def process_dir_change_other(self, obj, data):
        # obj.rotation = data
        # obj.update_direction()
        # obj.update_rect_size()
        obj.rotation_targets.append(data)

    def process_pos_change_other(self, obj, data):
        # obj.game_rect.center = data
        # obj.update_region()
        # print(345, obj, obj.game_rect.center, data)
        obj.move_targets.append(data)

    def process_toggle_zhatka_other(self, obj):
        obj.zhatka.harvesting = not obj.zhatka.harvesting
        obj.comb_dict['conductor'].togglePause()

    def wheat_count_changed_other(self, obj, data):
        obj.bunker.accumulator = data

    def process_wheat_sell(self, deals):
        for deal in deals:
            heap_id = deal[0]
            player_id = deal[0][0]
            price = deal[1]
            combain = self.world.combains_dict[player_id]
            combain.account += price
            heap = self.world.players_dict[player_id][heap_id]
            heap.kill()
            del self.world.players_dict[player_id][heap_id]


class ButtonHandler():
    def __init__(self, name):
        self.name = name
        self.time_pressed = 0
        self.keydown_timestamp = None
        self.keyup_timestamp = None
        self.pressed = False

    def increment_time_pressed(self, final_timestamp):
        self.time_pressed += final_timestamp - self.keydown_timestamp
        self.keydown_timestamp = final_timestamp

    def process_keydown(self):
        self.pressed = True
        self.keydown_timestamp = pygame.time.get_ticks()

    def process_keyup(self):
        self.pressed = False
        self.keyup_timestamp = pygame.time.get_ticks()
        self.increment_time_pressed(self.keyup_timestamp)

    def nullify(self):
        self.time_pressed = 0