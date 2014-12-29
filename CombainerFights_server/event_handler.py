__author__ = 'dimapct'

import config as c
import pygame


class EventHandlerServer():
    def __init__(self, boss):
        self.boss = boss
        self.world = boss.w

    def set_repeated_events(self, ships):
        # Set ship update broadcast timer
        pygame.time.set_timer(c.broadcast_ship_updates, c.ship_report_frequency)

    def handle_nps_events(self, ships):
        events_for_sending = []
        ship_message = self.create_ship_messages(ships)
        events_for_sending.extend(ship_message)
        return {'nps': events_for_sending}


# {24: {'buttons': {10: 16, 11: 0, 12: 0, 13: 16}, 'owner': (0, 0)}, 25: {'buttons': {10: 16, 11: 0}, 'owner': (0, 0)}}
    def handle_player_events(self, player_id, message):
        events = message[c.events]
        events_for_sending = []
        for event_type, event_dict in events.items():
            obj_id = event_dict['obj_id']
            obj = self.world.players_dict[player_id][obj_id]

            processed_event = {obj.id: {}}

            # DIRECTION
            if event_type == c.changed_direction:
                obj.update_rotation(event_dict['data'])
                event_info = round(obj.rotation, 2)
                processed_event[obj.id][event_type] = event_info

            # POSITION
            elif event_type == c.changed_position:
                obj.update_position(event_dict['data'])
                # x = round(obj.game_position.x, 2)
                # y = round(obj.game_position.y, 2)
                event_info = obj.game_rect.center
                processed_event[obj.id][event_type] = event_info

            # TOGGLE ZHATKA
            elif event_type == c.toggled_zhatka:
                obj.zhatka.harvesting = not obj.zhatka.harvesting
                processed_event[obj.id][event_type] = ()

            # WHEAT COUNT CHANGE
            elif event_type == c.wheat_count_changed:
                # print('Got WHEAT:', event_dict['data'])
                change_amount = event_dict['data']
                obj.bunker.accumulator += change_amount
                event_info = obj.bunker.accumulator
                processed_event[obj.id][event_type] = event_info

            events_for_sending.append(processed_event)

        player_processed_events = {player_id: events_for_sending}

        return player_processed_events

    def create_ship_messages(self, ships):
        events_for_sending = []
        for ship in ships.values():
            ship_events = {ship.id: {}}

            if ship.state in ('swimming_to_buy', 'swimming_to_sell'):
                x = round(ship.game_position[0])
                y = round(ship.game_position[1])
                event_type = c.changed_position
                event_info = (x, y)
                ship_events[ship.id][event_type] = event_info

            elif ship.state == 'buying':
                pass

            else:
                raise NotImplementedError('Invalid SHIP state', ship.state)

            events_for_sending.append(ship_events)

        return events_for_sending

    def nullify_last_events(self):
        self.last_processed_events = []