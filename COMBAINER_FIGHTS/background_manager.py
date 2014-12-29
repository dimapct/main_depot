__author__ = 'dimapct'


import pygame


class BackgroundManager():
    def __init__(self, game_map, target, camera, region_size, cell_size, nick):
        self.game_map = game_map
        self.target = target
        self.camera = camera
        self.region_size = region_size
        self.cell_size = cell_size
        self.region_width = self.region_size[0] * self.cell_size
        self.region_height = self.region_size[1] * self.cell_size
        self.background = pygame.Surface((1, 1))
        self.background_offset = [0, 0]
        self.container = pygame.sprite.Group()
        self.nick = nick

    def update(self):
        self.container.empty()
        self.camera.update()
        a1 = pygame.time.get_ticks()
        self.create_background()
        a2 = pygame.time.get_ticks()
        #print('Create background {0} mls'.format(a2-a1))

    def get_background_regions(self):
        regions = []
        collided_regions = pygame.sprite.spritecollide(self.camera, self.game_map.regions, False)

        all_coords = [region.coords for region in collided_regions]
        s = sorted(all_coords)

        topleft_coords = s[0]
        bottomright_coords = s[-1]

        for y in range(topleft_coords[1], bottomright_coords[1] + 1):
            regions.append([])
            for x in range(topleft_coords[0], bottomright_coords[0] + 1):
                # Always 1 item in the list
                reg = [region for region in collided_regions if region.coords == (x, y)]
                regions[-1].extend(reg)

                for key, item in reg[0].container.items():
                    self.container.add(item)

        return regions

    def create_background(self):
        s1 = pygame.time.get_ticks()
        #print('{0} Create backgrnd start ---------------'.format(self.nick))
        a1 = pygame.time.get_ticks()
        regions = self.get_background_regions()
        a2 = pygame.time.get_ticks()
        #print('Getting bckgrnd regions {0} mls'.format(a2-a1))

        a1 = pygame.time.get_ticks()

        regions_in_row = len(regions[0])
        regions_in_column = len(regions)

        w = regions_in_row * self.region_width
        h = regions_in_column * self.region_height

        if self.background.get_size() != (w, h):
            self.background = pygame.Surface((w, h))

        a2 = pygame.time.get_ticks()
        #print('Other staff {0} mls'.format(a2-a1))

        a1 = pygame.time.get_ticks()
        # Blit regions to background
        for y in range(regions_in_column):
            for x in range(regions_in_row):
                self.background.blit(regions[y][x].image, (x*self.region_width, y*self.region_height))

        a2 = pygame.time.get_ticks()
        #print('Draw {0} mls'.format(a2-a1))

        a1 = pygame.time.get_ticks()
        self.assign_background_xy(regions)
        a2 = pygame.time.get_ticks()

        a1 = pygame.time.get_ticks()
        self.calculate_background_offset()
        a2 = pygame.time.get_ticks()
        #print('Calculating bckgrnd offset {0} mls'.format(a2-a1))
        #print('{0} Create backgrnd end ------------------'.format(self.nick))
        s2 = pygame.time.get_ticks()
        #print('Create bckrnd {0} mls'.format(s2-s1))

    def calculate_background_offset(self):
        #point = self.calculate_point_on_background(regions)
        point = self.target.rect.center
        self.background_offset[0] = self.camera.rect.width//2 - point[0]
        self.background_offset[1] = self.camera.rect.height//2 - point[1]

    def assign_background_xy(self, regions):
        for y, row in enumerate(regions):
            for x, reg in enumerate(row):
                #print('BKGR region coords = {0}, container = {1}'.format(reg.coords, len(reg.container['combain'])))
                for item_type in reg.container.values():
                    for obj in item_type:
                        # if obj.name == 'ship':
                        #     print('{0} BKGRND MAN game_rect: {1}'.format(obj.name, obj.game_rect.center))
                        ignore, point = self.game_map.get_region_and_xy(obj.game_rect.center)
                        background_x = x * self.region_width + point[0]
                        background_y = y * self.region_height + point[1]
                        obj.rect.center = (background_x, background_y)
                        # if obj.name == 'ship':
                        #     print('{0} BKGRND MAN new rect_center {1}'.format(obj.name, obj.rect.center))
