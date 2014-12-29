__author__ = 'dimapct'


import pygame
from pygame.locals import Color
import game_object
import config as c
import math


class Weapon(pygame.sprite.Sprite):
    def __init__(self, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.name = kwargs.get('name')
        self.image = kwargs.get('image')
        if self.image is not None:
            self.rect = self.image.get_rect()
        # self.game_rect = pygame.Rect(kwargs.get('game_xy'), self.rect.size)
        self.owner = kwargs.get('owner')
        self.direction = kwargs.get('direction')
        # self.update_game_xy()
        self.gun_dict = kwargs.get('gun_dict')
        self.bullet_image = kwargs.get('bullet_image')
        self.world = kwargs.get('world')
        self.hit_sound = kwargs.get('hit_sound')
        self.shoot_sound = kwargs.get('shoot_sound')

    def shoot(self):
        raise NotImplementedError

    def reload(self):
        raise NotImplementedError

    def change_direction(self):
        raise NotImplementedError

    def update_game_xy(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError


class Gun(Weapon):

    def shoot(self):
        self.shoot_sound.play()
        direction = self.direction

        game_point = self.owner.game_rect.center

        x = game_point[0] - self.gun_dict[direction]['bullet_point'][0]
        y = game_point[1] - self.gun_dict[direction]['bullet_point'][1]
        game_xy = x, y

        heading_x = math.sin(direction * math.pi / 180.0)
        heading_y = math.cos(direction * math.pi / 180.0)
        heading = pygame.math.Vector2(heading_x, heading_y)
        heading *= -1

        set_time = pygame.time.get_ticks()
        bullet = Bullet(name='bullet', speed=c.bullet_speed, image=self.bullet_image, direction=direction,
                        game_xy=game_xy, heading=heading, game_map=self.owner.game_map, damage=c.bullet_damage,
                        hit_sound=self.hit_sound, set_time=set_time)
        bullet.game_rect.center = bullet.game_position

        region, xy = self.owner.game_map.get_region_and_xy(bullet.game_position)
        region.container['bullet'].add(bullet)

        self.world.all_objects.add(bullet)

    def reload(self):
        pass

    def change_direction(self):
        pass

    def update_game_xy(self):
        self.rect.center = self.owner.rect.center

    def update_image(self):
        self.image = self.gun_dict[self.direction]['image']
        self.rect = self.image.get_rect()

    def update(self):
        self.change_direction()
        self.update_image()
        # self.update_game_xy()


class Miner(Weapon):

    def shoot(self):
        game_xy = self.owner.game_rect.center
        set_time = pygame.time.get_ticks()
        mine = Mine(name='mine', game_map=self.owner.game_map, game_xy=game_xy, image=self.bullet_image,
                    damage=c.mine_damage, set_time=set_time, hit_sound=self.hit_sound)
        mine.game_rect.center = mine.game_position

        region, xy = self.owner.game_map.get_region_and_xy(mine.game_position)
        region.container['mine'].add(mine)

        self.world.all_objects.add(mine)

    def reload(self):
        pass

    def change_direction(self):
        raise NotImplementedError('this method call is not applicable with Miner object')

    def update_game_xy(self):
        pass

    def update(self):
        pass


class Bullet(game_object.GameObject):
    def __init__(self, **kwargs):
        game_object.GameObject.__init__(self, **kwargs)
        self.hit_sound = kwargs.get('hit_sound')
        self.set_time = kwargs.get('set_time')
        self.activated = False

    def move(self):
        new_position = self.game_position + self.heading * self.speed
        x = new_position[0]
        y = new_position[1]
        if not 0 <= x < self.game_map.game_world_width or not 0 <= y < self.game_map.game_world_height:
            self.kill()
        else:
            self.game_position = new_position
            self.game_rect.center = self.game_position

    def update_activation(self):
        new_time = pygame.time.get_ticks()
        delta = new_time - self.set_time
        if delta >= c.bullet_activation_time:
            self.activated = True

    def update(self):
        self.move()
        self.update_region()
        if not self.activated:
            self.update_activation()

    def hit(self, target):
        self.hit_sound.play()
        target.hp -= self.damage
        self.kill()


class Mine(game_object.GameObject):
    def __init__(self, **kwargs):
        game_object.GameObject.__init__(self, **kwargs)
        self.set_time = kwargs.get('set_time')
        self.hit_sound = kwargs.get('hit_sound')
        self.activated = False

    def update(self):
        if not self.activated:
            self.update_activation()

    def update_activation(self):
        new_time = pygame.time.get_ticks()
        delta = new_time - self.set_time
        if delta >= c.mine_activation_time:
            self.activated = True

    def explode(self, target):
        self.hit_sound.play()
        target.hp -= self.damage
        self.kill()

    def hit(self, target):
        self.explode(target)