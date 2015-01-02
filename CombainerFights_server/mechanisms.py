__author__ = 'dimapct'


import game_object
import bunker
from pygame import sprite, Rect


class Ship(game_object.GameObject):
    def __init__(self, owner_id, **kwargs):
        game_object.GameObject.__init__(self, owner_id, **kwargs)
        self.price = kwargs.get('price')
        self.sea_height = kwargs.get('sea_height')
        self.bunker = bunker.Bunker(kwargs.get('bunker_size'),
                                    name='cargo_hold')
        self.overlap = kwargs.get('overlap')

        # Set buying machine
        self.buying_machine = sprite.Sprite()
        h = kwargs.get('buy_radius') * 2
        x = self.game_rect.centerx
        y = self.game_rect.bottom
        rect = Rect(0, 0, h, h)
        rect.center = x, y
        self.buying_machine.rect = rect
        self.purchases_to_send = []

    def update(self, t):
        if self.state == 'swimming_to_buy':
            self.swim_to_buy(t)
            self.check_landing()
        elif self.state == 'swimming_to_sell':
            self.swim_to_sell(t)
            self.check_if_sell()
        elif self.state == 'buying':
            self.buy()
            self.check_if_full()
        else:
            raise NotImplementedError('Invalid SHIP state:', self.state)

    def swim_to_buy(self, t):
        self.game_position.y += self.speed * t
        self.game_rect.centery = self.game_position.y
        self.buying_machine.rect.bottom = self.game_rect.bottom
        print('SWIM TO BUY', self.game_position, t)
        self.update_region()

    def swim_to_sell(self, t):
        self.game_position.y -= self.speed * t
        self.game_rect.centery = self.game_position.y
        self.buying_machine.rect.bottom = self.game_rect.bottom
        self.update_region()

    def check_landing(self):
        region_height = self.game_map.region_size[1] * self.game_map.cell_size
        dd = divmod(self.sea_height, region_height)
        if dd[1]:
            regions_under_sea = dd[0] + 1
        else:
            regions_under_sea = dd[0]
        true_sea_height = regions_under_sea * region_height
        if self.game_rect.bottom > true_sea_height + self.overlap:
            self.state = 'buying'

    def check_if_sell(self):
        if self.game_position.y <= 0:
            self.bunker.accumulator = 0
            self.state = 'swimming_to_buy'

    def buy(self):
        collided_regions = sprite.spritecollide(self.buying_machine, self.game_map.regions, False)
        available_wheat = []
        we_buy_this = []
        for region in collided_regions:
            [available_wheat.append(product) for product in region.container['wheat']]

        for product in available_wheat:
            if sprite.collide_circle(product, self.buying_machine):
                we_buy_this.append(product)

        self.pay_to_all(we_buy_this)
        self.onboard_purchases(we_buy_this)

    def pay_to_all(self, products):
        for product in products:
            cost = self.price * product.weight
            product.owner.account += cost
            purchase = (product.id, cost)
            self.purchases_to_send.append(purchase)

    def onboard_purchases(self, products):
        for product in products:
            self.bunker += product.weight
            print('SHIP bought {0} kg of wheat'.format(product.weight))
            product.kill()

    def check_if_full(self):
        if self.bunker.accumulator == self.bunker.size:
            self.state = 'swimming_to_sell'