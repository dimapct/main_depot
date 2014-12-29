__author__ = 'dimapct'


import pygame
from pygame.locals import *
import sys
import config as c
import queue


def run_intro():
    return 'nick'


def run_enter_nick(game_static):
    next_state = 'lobby'
    screen = pygame.display.get_surface()
    font = game_static['font_big']
    nick_file = 'nick.txt'
    clock = game_static['clock']

    text_invite = font.render(c.enter_your_nick_text, True, Color('white'))
    text_exit = font.render(c.exit_text, True, Color('white'))
    x_exit = 0
    y_exit = screen.get_height() - text_exit.get_height()

    # Get previous nick, if exist
    try:
        nick = open(nick_file).read()
    except FileNotFoundError:
        nick = ''

    # Main loop
    while True:
        for event in pygame.event.get():
            # Exit buttons handling
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                sys.exit('Game exited by user action')

            if event.type == KEYDOWN:
                # Type letter
                if event.unicode in c.allowed_chars:
                    nick += event.unicode

                # Erase last letter
                if event.key == K_BACKSPACE:
                    nick = nick[0:-1]

                # Enter nick
                if event.key == K_RETURN and nick:
                    # First character 'space' is not allowed
                    if nick[0] != ' ':
                        # Save new nick to file
                        open(nick_file, 'w').write(nick)
                        pygame.display.set_caption(nick)
                        return nick, next_state

        # Draw
        text_to_display = font.render(nick + '_', True, Color('green'))
        screen.fill(Color('black'))
        x = screen.get_width() / 2 - text_invite.get_width() / 2
        y = screen.get_height() / 2 - text_invite.get_height() / 2
        screen.blit(text_invite, (x, y))
        screen.blit(text_to_display, (x, y + 30))
        screen.blit(text_exit, (x_exit, y_exit))
        pygame.display.flip()

        clock.tick(c.menu_fps)


class Lobby():
    def __init__(self, game_static, socket, nick, sender):
        self.game_static = game_static
        self.user_list = []
        self.game_run = False
        self.running = True
        # self.user_list_surf = None
        self.in_queue = queue.Queue()
        self.sender = sender
        # self.init_user_list_surf()
        self.socket = socket
        self.all_clients_db = None
        self.nick = nick
        self.id = None
        message = {c.new_nick: self.nick}
        self.sender.send_message(message, self.socket)

    def run(self):
        clock = self.game_static['clock']
        # Run lobby
        while self.running and not self.game_run:
            self.update()
            self.draw()
            clock.tick(c.menu_fps)
        else:
            if self.game_run:
                print('LOBBY exit to GAME')
                return 'game', self.id
            elif not self.running:
                return 'nick', None

    def draw(self):
        font = self.game_static['font_big']
        screen = pygame.display.get_surface()
        # Exit text
        text_exit = font.render(c.exit_text, True, Color('white'))
        x_exit = 0
        y_exit = screen.get_height() - text_exit.get_height()

        # Start game text
        screen.fill(Color('black'))
        text_start_game = font.render(c.start_game_text, True, Color('white'))
        screen.blit(text_start_game, (0, y_exit - text_start_game.get_height()))
        screen.blit(text_exit, (x_exit, screen.get_height() - text_exit.get_height()))
        self.draw_players()
        self.draw_name()
        pygame.display.flip()

    def init_user_list_surf(self):
        w = 250
        h = pygame.display.get_surface().get_height()
        self.user_list_surf = pygame.Surface((w, h))

    def draw_name(self):
        screen = pygame.display.get_surface()
        font = self.game_static['font_extra_big']
        text_name = font.render(c.game_name, True, Color('gold'))
        x = screen.get_width() // 2 - text_name.get_width() // 2
        y = 0
        screen.blit(text_name, (x, y))

    def draw_players(self):
        font = self.game_static['font_big']
        screen = pygame.display.get_surface()

        y = 100

        player_line_height = 30
        team_label_width = 20
        ready_to_start_width = 20
        color_label_width = 50

        for player in sorted(self.user_list):
            my_nick = False
            start_x = int(screen.get_width() * 0.66)
            x = start_x

            nick = self.user_list[player]['nick']
            color = self.user_list[player]['color']
            team = self.user_list[player]['team']
            ready_to_start = self.user_list[player]['ready_to_start']

            # Identify my name
            if nick == self.nick:
                my_nick = True

            text_nick = font.render(nick, True, Color('white'))
            color_surf_height = text_nick.get_height()
            color_surf = pygame.Surface((color_surf_height*2, color_surf_height))
            color_surf.fill(color)
            if team is None:
                text_team = font.render('x', True, Color('white'))
            else:
                text_team = font.render(str(team), True, Color('white'))

            if ready_to_start:
                pygame.draw.circle(screen, Color('green'), (x, y + text_nick.get_height()//2), 7)
            x += ready_to_start_width
            screen.blit(text_team, (x, y))
            if my_nick:
                pygame.draw.line(screen, Color('white'), (x, y), (x, y + player_line_height), 2)
            x += team_label_width
            screen.blit(color_surf, (x, y))
            x += color_label_width
            screen.blit(text_nick, (x, y))
            y += player_line_height

    def update(self):
        self.process_in_queue()
        self.process_inputs()

    def process_in_queue(self):
        # print('Client is processing in_queue')
        try:
            item = self.in_queue.get(block=False)
            # print('Client got message,', item)
            for key, value in item.items():
                if key == 'user_list':
                    self.user_list = value
                    print('{0} lobby got user list: {1}'.format(self.nick, value))
                elif key == c.game_started:
                    self.start_game()

                elif key == 'id':
                    self.id = value

        except queue.Empty:
            pass

    def process_inputs(self):
        for event in pygame.event.get():
            # Exit buttons handling
            if event.type == QUIT:
                message = {c.quit_lobby: None}
                self.sender.send_message(message, self.socket)
                sys.exit('Client exit')

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    message = {c.quit_lobby: None}
                    self.sender.send_message(message, self.socket)
                    self.running = False

                elif event.key == K_RETURN:
                    # self.game_run = True
                    message = {c.ready_to_start: True}
                    self.sender.send_message(message, self.socket)

                elif event.key == K_LEFT:
                    message = {c.color_change: 'back'}
                    self.sender.send_message(message, self.socket)

                elif event.key == K_RIGHT:
                    message = {c.color_change: 'forward'}
                    self.sender.send_message(message, self.socket)

                elif event.key == K_DOWN:
                    message = {c.team_change: 'back'}
                    self.sender.send_message(message, self.socket)

                elif event.key == K_UP:
                    message = {c.team_change: 'forward'}
                    self.sender.send_message(message, self.socket)

    def start_game(self):
        self.game_run = True
