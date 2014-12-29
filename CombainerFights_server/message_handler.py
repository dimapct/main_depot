__author__ = 'test'


import config as c


class MessageHandler():
    def __init__(self, broadcaster):
        self.message_id = 0
        self.broadcaster = broadcaster

    def distribute_changes(self, mq, lock):
        with lock:
            for player_id, events in mq.items():
                if events:
                    message = {c.client_game_message: {player_id: events}}
                    # print('2356 Server sent message', message)
                    self.broadcaster.broadcast_unknown_game_messages(message)
            MessageHandler.nullify_mq(mq)

    @staticmethod
    def nullify_mq(mq):
        for player_messages in mq.values():
            player_messages.clear()