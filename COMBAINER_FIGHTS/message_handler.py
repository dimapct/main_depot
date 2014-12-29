__author__ = 'dimapct'

import config as c
import time


class MessageHandler():
    def __init__(self):
        self.last_messages = []
        self.packet_id = 0

    def get_new_id(self):
        self.packet_id += 1
        return self.packet_id

    @staticmethod
    def get_message(events, t):
        events_transformed = MessageHandler.transform_events(events)
        message = {c.client_game_message: {c.timestamp: t,
                                           c.events: events_transformed}}
        return message

    @staticmethod
    def transform_events(events):
        events_transformed = {event.type: event.__dict__ for event in events}
        return events_transformed