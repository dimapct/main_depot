__author__ = 'dimapct'

import pygame
from pygame.locals import *
import config as c


class GameMap(pygame.sprite.Sprite):
    def __init__(self, game_field_size, region_size, cell_size):
        a1 = pygame.time.get_ticks()
        pygame.sprite.Sprite.__init__(self)
        self.regions = pygame.sprite.Group()
        self.game_field_size = game_field_size
        self.region_size = region_size
        self.cell_size = cell_size
        self.game_world_width = self.game_field_size[0] * self.region_size[0] * self.cell_size
        self.game_world_height = self.game_field_size[1] * self.region_size[1] * self.cell_size
        a2 = pygame.time.get_ticks()
        # print('Map generation time:', a2-a1)

    def create_game_map(self):
        game_field_size = self.game_field_size
        region_size = self.region_size
        cell_size = self.cell_size

        # Create empty rows of regions
        self.regions_list = [[] for i in range(game_field_size[1])]

        # Create regions
        reg_width = region_size[0] * cell_size
        reg_height = region_size[1] * cell_size
        count = 1
        for y in range(len(self.regions_list)):
            reg_y = reg_height * y
            for x in range(game_field_size[0]):
                reg_x = reg_width * x
                region = Region((reg_x, reg_y), (x, y), (reg_width, reg_height), cell_size)
                # print('Region', count)
                count += 1
                self.regions_list[y].append(region)
                self.regions.add(region)

    def get_region_and_xy(self, game_xy):
        region_width = self.region_size[0] * self.cell_size
        region_height = self.region_size[1] * self.cell_size
        coord_x = int(game_xy[0]) // region_width
        coord_y = int(game_xy[1]) // region_height

        # print('Region rows, columns', len(self.regions_list), len(self.regions_list[0]))
        # print('coord_x, coord_y', coord_x, coord_y)
        region = self.regions_list[coord_y][coord_x]

        x = game_xy[0] - coord_x * region_width
        y = game_xy[1] - coord_y * region_height
        return region, (x, y)

    def get_4_neib_cells(self, cell):
        return {dirr: self.get_neib_cell(cell, dirr) for dirr in c.directions}

    def get_8_neib_cells(self, cell):
        neib_cells = self.get_4_neib_cells(cell)
        for dirr in c.directions_diagonal:
            neib_cells[dirr] = None

        down = self.get_neib_cell(cell, 'down')
        if down is not None:
            neib_cells['dl'] = self.get_neib_cell(down, 'left')
            neib_cells['dr'] = self.get_neib_cell(down, 'right')

        up = self.get_neib_cell(cell, 'up')
        if up is not None:
            neib_cells['ul'] = self.get_neib_cell(down, 'left')
            neib_cells['ur'] = self.get_neib_cell(down, 'right')

        return neib_cells

    def get_neib_cell(self, cell, direction):

        if direction == 'up':
            neib_coord_x = cell.coords[0]
            neib_region_coord_x = cell.region.coords[0]
            if cell.coords[1] == 0:
                if cell.region.coords[1] == 0:
                    return
                else:

                    neib_region_coord_y = cell.region.coords[1] - 1
                neib_coord_y = self.region_size[1] - 1

            else:
                neib_coord_y = cell.coords[1] - 1
                neib_region_coord_y = cell.region.coords[1]

        elif direction == 'down':
            neib_coord_x = cell.coords[0]
            neib_region_coord_x = cell.region.coords[0]
            if cell.coords[1] == self.region_size[1] - 1:
                if cell.region.coords[1] == self.game_field_size[1] - 1:
                    return
                else:
                    neib_region_coord_y = cell.region.coords[1] + 1

                neib_coord_y = 0

            else:
                neib_coord_y = cell.coords[1] + 1
                neib_region_coord_y = cell.region.coords[1]

        elif direction == 'right':
            neib_coord_y = cell.coords[1]
            neib_region_coord_y = cell.region.coords[1]
            if cell.coords[0] == self.region_size[0] - 1:
                if cell.region.coords[0] == self.game_field_size[0] - 1:
                    return
                else:
                    neib_region_coord_x = cell.region.coords[0] + 1

                neib_coord_x = 0

            else:
                neib_coord_x = cell.coords[0] + 1
                neib_region_coord_x = cell.region.coords[0]

        elif direction == 'left':
            neib_coord_y = cell.coords[1]
            neib_region_coord_y = cell.region.coords[1]
            if cell.coords[0] == 0:
                if cell.region.coords[0] == 0:
                    return
                else:
                    neib_region_coord_x = cell.region.coords[0] - 1

                neib_coord_x = self.region_size[0] - 1

            else:
                neib_coord_x = cell.coords[0] - 1
                neib_region_coord_x = cell.region.coords[0]

        else:
            raise Exception('Incorrect direction name')

        neib_region = self.regions_list[neib_region_coord_y][neib_region_coord_x]
        neib_cell = neib_region.cells_list[neib_coord_y][neib_coord_x]

        return neib_cell


class Region(pygame.sprite.Sprite):
    def __init__(self, xy, coords, region_size, cell_size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(region_size)
        self.rect = self.image.get_rect()
        self.rect.topleft = xy
        self.coords = coords
        self.cells_list = list()
        self.cells = pygame.sprite.Group()
        self.create_cells(region_size, cell_size)
        self.immovables_container = {4: pygame.sprite.Group()}
        self.container = {'mine': pygame.sprite.Group(),
                          'bullet': pygame.sprite.Group(),
                          'combain': pygame.sprite.Group(),
                          'ship': pygame.sprite.Group(),
                          'wheat': pygame.sprite.Group()}
        # pygame.draw.rect(self.image, Color('red'), (0, 0, self.rect.width, self.rect.height), 1)

    def create_cells(self, reg_size, cell_size):
        for y1 in range(0, reg_size[1], cell_size):
            self.cells_list.append([])
            for x1 in range(0, reg_size[0], cell_size):
                cell = Cell((x1, y1), cell_size, self, reg_size, (x1//cell_size, y1//cell_size))
                self.cells_list[-1].append(cell)
                self.cells.add(cell)


class Cell(pygame.sprite.Sprite):
    def __init__(self, xy, cell_size, region, region_size, coords, terrain=1):
        pygame.sprite.Sprite.__init__(self)
        self.tiles = list()
        self.height = 0
        self.image = pygame.Surface((cell_size, cell_size))
        self.region = region
        self.coords = coords
        self.region_rect = pygame.Rect(xy, (cell_size, cell_size))

        game_x = self.region_rect.x + self.region.coords[0] * region_size[0]
        game_y = self.region_rect.y + self.region.coords[1] * region_size[1]
        self.game_rect = pygame.Rect((game_x, game_y), self.region_rect.size)
        self.rect = self.game_rect
        self.terrain = None
        self.assign_terrain(terrain)

    def assign_terrain(self, terrain):
        fill = self.image.fill

        if terrain == 1:
            fill(Color('darkgreen'))

        elif terrain == 2:
            fill(Color('darkblue'))

        elif terrain == 3:
            fill(Color('yellow'))

        elif terrain == 4:
            fill((10, 75, 10))
            if self not in self.region.immovables_container[terrain]:
                self.region.immovables_container[terrain].add(self)

        self.terrain = terrain
        # pygame.draw.rect(self.image, Color('black'), (0, 0, self.rect.width, self.rect.height), 1)
        self.rect = self.region_rect
        self.region.image.blit(self.image, self.rect.topleft)
        self.rect = self.game_rect