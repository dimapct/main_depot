__author__ = 'dimapct'


import sys
# Thread import
if sys.version[0] == '2':
    import thread
elif sys.version[0] == '3':
    import _thread as thread
    
import pygame



class Broadcaster():
    def __init__(self, recipients, sender):
        self.recipients = recipients
        self.sender = sender

    def broadcast_message(self, message, threaded=0):
        """
        Broadcasts message to all players
        """
        # print('Server broadcasts message =>', message)

        if threaded:
            # print('!!!!!!!! sending message START !!!!!!!!!!!')
            # a1 = pygame.time.get_ticks()
            for recipient in self.recipients.values():
                thread.start_new_thread(self.sender.send_message, (message, recipient.socket))
            # a2 = pygame.time.get_ticks()
            # print(444, a2-a1)

        else:
            # print('!!!!!!!! sending message START !!!!!!!!!!!')
            # a1 = pygame.time.get_ticks()
            for recipient in self.recipients.values():
                self.sender.send_message(message, recipient.socket)
            # a2 = pygame.time.get_ticks()
            # print(444, a2-a1)
            # print('Server finished broadcasting message =>', message)

    def broadcast_unknown_game_messages(self, message):
        """
        Broadcasts message to all players, except the message owner
        """
        for something in message.values():
            message_owner = list(something.keys())[0]

            for recipient_id, recipient in self.recipients.items():
                if recipient_id != message_owner:
                    self.sender.send_message(message, recipient.socket)