__author__ = 'dimapct'

import pygame
from game_tools import Vector2
import sys
# Thread import
if sys.version[0] == '2':
    import thread
elif sys.version[0] == '3':
    import _thread as thread
import config as c
import math
from collections import deque


class GameObject(pygame.sprite.Sprite):
    def __init__(self, owner_id, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.id = kwargs.get('id', (owner_id, id(self)))
        self.owner = kwargs.get('game_owner')
        self.name = kwargs.get('name')
        self.state = kwargs.get('state')
        self.hp = kwargs.get('hp')
        self.weight = kwargs.get('weight')
        self.speed = kwargs.get('speed')
        self.armor = kwargs.get('armor')
        self.game_map = kwargs.get('game_map')
        self.direction = kwargs.get('direction', 0)
        self.account = kwargs.get('start_money')
        self.original_image = kwargs.get('image')
        image_size = kwargs.get('image_size', (1, 1))
        self.image = kwargs.get('image', pygame.Surface(image_size))
        self.rect = self.image.get_rect()
        game_xy = kwargs.get('game_xy', (50, 50))
        self.game_rect = pygame.Rect((0, 0), self.rect.size)
        self.game_rect.center = game_xy
        self.move_targets = deque()
        self.rotation_targets = deque()
        self.gear = 'front'  # front or back
        self.action = 'stopped'
        self.damage = kwargs.get('damage')
        self.game_position = Vector2(game_xy[0], game_xy[1])
        self.heading = kwargs.get('heading')
        self.rotation = 0.
        self.rotation_speed = kwargs.get('rotation_speed')
        self.region = None
        self.update_region()

        # self.rotation_lock = thread.allocate_lock()
        # self.position_lock = thread.allocate_lock()

    def get_standing_cell(self):
        cell = self.game_map.get_cell_by_point(self.rect.center)
        return cell

    def check_game_world_boundary(self):
        flag = False

        if self.game_rect.left < 0:
            self.game_rect.left = 0
            flag = True

        elif self.game_rect.right > self.game_map.game_world_width:
            self.game_rect.right = self.game_map.game_world_width
            flag = True

        if self.game_rect.top < 0:
            self.game_rect.top = 0
            flag = True

        elif self.game_rect.bottom > self.game_map.game_world_height:
            self.game_rect.bottom = self.game_map.game_world_height
            flag = True

        if flag:
            a = self.game_rect.center
            self.game_position = Vector2(float(a[0]), float(a[1]))

    def check_immovables(self, new_position):
        # Look up region
        rect_temp = self.rect.copy()

        self.rect = self.game_rect.copy()
        self.rect.center = new_position

        regions_in_scope = self.get_regions_in_scope()

        # Collide with all forest cells
        for region in regions_in_scope:
            collided_forest_cells = pygame.sprite.spritecollide(self, region.immovables_container['forest'], False)

            if collided_forest_cells:
                self.rect = rect_temp
                return True
        else:
            self.rect = rect_temp
            return False

    def update_region(self):
        x, y = self.game_rect.center
        region, xy = self.game_map.get_region_and_xy((x, y))
        if self.region is None:
            self.region = region
            self.region.container[self.name].add(self)
            return

        if self.region != region:
            self.region.container[self.name].remove(self)
            region.container[self.name].add(self)
            self.region = region

    def get_regions_in_scope(self):
        return pygame.sprite.spritecollide(self, self.game_map.regions, False)

    def update_rotation(self, arrow_keys):
        rotation_direction = 0.
        movement_direction = 0.
        rotation_time = 0.

        if arrow_keys[c.backward]:
            movement_direction = 1.0
        if arrow_keys[c.forward]:
            movement_direction = -1.0

        if arrow_keys[c.left]:
            if movement_direction == -1.0:
                rotation_direction = 1.0
            elif movement_direction == 1.0:
                rotation_direction = -1.0
            else:
                rotation_direction = 1.0
            rotation_time = arrow_keys[c.left]

        if arrow_keys[c.right]:
            if movement_direction == -1.0:
                rotation_direction = -1.0
            elif movement_direction == 1.0:
                rotation_direction = 1.0
            else:
                rotation_direction = -1.0
            rotation_time = arrow_keys[c.right]

        self.rotation += rotation_direction * self.rotation_speed * rotation_time
        self.update_direction()

    def update_rotation_with_interpolation(self, t):

        if self.rotation_targets:
            # print(123, self.rotation_targets, self.rotation_targets[0], self.rotation, t, t*self.rotation_speed)
            target = self.rotation_targets[0]
            current = self.rotation
            step = self.rotation_speed * t
            if target - current > step:
                self.rotation += step
            else:
                self.rotation = target
                self.rotation_targets.popleft()

    def update_position(self, arrow_keys):
        movement_direction = 0.
        movement_time = 0.

        if arrow_keys[c.backward]:
            movement_direction = 1.0
            movement_time = arrow_keys[c.backward]
        if arrow_keys[c.forward]:
            movement_direction = -1.0
            movement_time = arrow_keys[c.forward]

        heading_x = math.sin(self.rotation * math.pi / 180.0)
        heading_y = math.cos(self.rotation * math.pi / 180.0)
        heading = Vector2(heading_x, heading_y)
        heading *= movement_direction

        new_game_position = self.game_position + heading * (self.speed * movement_time)

        # Check for obstacles
        # if not self.check_immovables(new_game_position):
        #     self.game_position = new_game_position
        #
        #     # Update game rect
        #     self.game_rect.center = self.game_position
        #     self.check_game_world_boundary()

        self.game_position = new_game_position

        # Update game rect
        self.game_rect.center = self.game_position[0], self.game_position[1]
        self.check_game_world_boundary()

    def update_position_with_interpolation(self, t):
        if self.move_targets:
            if self.name == 'ship':
                print(456, self.move_targets, t)

            current_point = self.game_position.x, self.game_position.y
            target_point = self.move_targets[0]
            # Make it float
            target_point = float(target_point[0]), float(target_point[1])

            vector = Vector2.from_points(current_point, target_point)

            distance_to_target = vector.get_lentgh()
            obj_1_step_distance = self.speed * t
            if distance_to_target > obj_1_step_distance:
                vector.norm()
                self.game_position += vector * obj_1_step_distance
                print('interpolation', self.game_position)

            else:
                # If distance is less than 1 step, then no need in interpolation
                self.game_position.x = target_point[0]
                self.game_position.y = target_point[1]
                self.move_targets.popleft()
                print('directly', self.game_position)


            self.game_rect.center = self.game_position[0], self.game_position[1]

    def update_direction(self):
        rotation = round(self.rotation, 0)
        self.direction = int(rotation - rotation // 360 * 360)