__author__ = 'dimapct'

import random
import config as cnfg
import pygame


def generate_nature(game_map):
    a1 = pygame.time.get_ticks()
    generate_trees(game_map)
    generate_fields(game_map)
    generate_sea(game_map)
    a2 = pygame.time.get_ticks()
    # print('World creation time:', a2-a1)


def generate_sea(game_map):
    sea_height = cnfg.sea_height
    cell_size = cnfg.cell_size
    region_row_index = 0
    cell_rows_per_region = cnfg.region_size[1]
    while sea_height > 0:
        regions = game_map.regions_list[region_row_index]
        for cell_row_index in range(cell_rows_per_region):
            for region in regions:
                for cell in region.cells_list[cell_row_index]:
                    cell.assign_terrain(cnfg.sea)
            sea_height -= cell_size
        region_row_index += 1


def generate_trees(game_map):
    cells_on_map = cnfg.region_size[0] * cnfg.region_size[1] * cnfg.game_field_size[0] * cnfg.game_field_size[1]

    # Forests count is based on world size
    forests_count = max(1, int(cells_on_map / (cnfg.big_forest_size / cnfg.big_forest_density)))

    forests_small_count = max(1, int(cells_on_map / (cnfg.small_forest_size / cnfg.small_forest_density)))

    for i in range(forests_count):
        generate_forest(cnfg.big_forest_size, game_map, 4)

    for i in range(forests_small_count):
        generate_forest(cnfg.small_forest_size, game_map, 4)


def generate_fields(game_map):
    terrain = 3
    fields_count = 10

    for i in range(fields_count):
        field_sprites = pygame.sprite.Group()
        field_rects = generate_field_rects()

        # Assign game world xy
        start_cell = get_start_cell(game_map, (terrain, cnfg.forest))
        new_x, new_y = start_cell.game_rect.topleft
        random_rect = random.choice(field_rects)
        delta_x = new_x - random_rect.x
        delta_y = new_y - random_rect.y
        for rect in field_rects:
            rect.move_ip(delta_x, delta_y)

        # Create sprites
        for rect in field_rects:
            spr = pygame.sprite.Sprite()
            spr.rect = rect
            field_sprites.add(spr)

        # Assign terrain to cells
            # Get collided regions
        collided_regions = []
        for spr in field_sprites:
            collides = pygame.sprite.spritecollide(spr, game_map.regions, False)
            collided_regions.extend(collides)

            # Get all cells from collided regions
        all_cells = pygame.sprite.Group()
        for region in collided_regions:
            all_cells.add(region.cells)

            # Collide field rect with cells
        for field in field_sprites:
            for cell in pygame.sprite.spritecollide(field, all_cells, False):
                if cell.terrain != cnfg.forest:
                    cell.assign_terrain(terrain)


def get_start_cell(game_map, forbidden_terrain):
    while True:
            # Get random region
        row = random.choice(game_map.regions_list)
        region = random.choice(row)

        current_x = random.randint(0, cnfg.region_size[0] - 1)
        current_y = random.randint(0, cnfg.region_size[1] - 1)
        cell = region.cells_list[current_y][current_x]
        if cell.terrain not in forbidden_terrain:
            return cell


def generate_forest(squares_count, game_map, terrain):
    """
    This function randomly selects cells, which will be a part of forest, field, etc, of the given square.
    """

    # Generate height square
    square = squares_count
    # Get first cell
    while True:
        # Get random region
        row = random.choice(game_map.regions_list)
        region = random.choice(row)

        current_x = random.randint(0, cnfg.region_size[0] - 1)
        current_y = random.randint(0, cnfg.region_size[1] - 1)

        cell = region.cells_list[current_y][current_x]
        if cell.terrain != terrain:
            cell.terrain = terrain
            break

    # Get cells
    def look_for_non_terrain(start_cell, direction, terrain):
        """
        Looks up for cell which terrain is different to input terrain
        """
        non_terrain_cell = None

        while non_terrain_cell is None:
            neib_cell = game_map.get_neib_cell(start_cell, direction)

            if neib_cell is None:
                break

            if neib_cell.terrain != terrain:
                non_terrain_cell = neib_cell

            start_cell = neib_cell

        return non_terrain_cell

    h = 0
    while square > 0:
        if h == 10000:
            print('yyyyyyyyyyyyyyyyy')
            break
        h += 1

        neibs = game_map.get_4_neib_cells(cell)
        neibs_list = list(neibs)
        random.shuffle(neibs_list)

        for dirr in neibs_list:

            none_count = 0
            for c in neibs.values():
                if c is None:
                    none_count += 1

            if none_count == 4:
                print('All neibs are')

            if neibs[dirr] is None:
                continue

            # if neibs[dirr].terrain != terrain:
            #     neibs[dirr].assign_terrain(terrain)
            #     square -= 1
            #     cell = neibs[dirr]
            #     break

            neibs[dirr].assign_terrain(terrain)
            square -= 1
            cell = neibs[dirr]
            break

        else:
            direction = random.choice(cnfg.directions)
            non_terrain_cell = look_for_non_terrain(cell, direction, terrain)
            non_terrain_cell.assign_terrain(terrain)
            square -= 1
            cell = non_terrain_cell


def generate_field_rects():
    field_size = random.choice((cnfg.region_width, cnfg.region_height))
    rects_count = (1, 1, 1, 2, 2, 2, 3)
    rects = []
    count = random.choice(rects_count)
    for i in range(count):
        w = random.randint(cnfg.cell_size * 3, field_size)
        h = random.randint(cnfg.cell_size * 3, field_size)
        rect = pygame.Rect(0, 0, w, h)
        rects.append(rect)

    if len(rects) == 1:
        return rects

    else:
        surf = pygame.Surface((field_size, field_size))
        while True:
            for rect in rects:
                rect.x = random.randint(0, surf.get_width())
                rect.y = random.randint(0, surf.get_height())

            for rect in rects:
                if len(rect.collidelistall(rects)) < 2:
                    break
            else:
                return rects
