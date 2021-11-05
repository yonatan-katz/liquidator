from reserve_asset import get_crypto_asset_usd_price

class GlobalPos:
    def __init__(self):
        self.position = {}

    def increase_pos(self, asset, amount):
        if asset in self.position:
            self.position[asset] += amount
        else:
            self.position[asset] = amount
        pass

    def decrease_pos(self, asset, amount):
        if asset in self.position:
            self.position[asset] -= amount
        else:
            self.position[asset] = -amount
        pass

    def get_pos(self):
        return self.position

    def pos_sum_in_usd(self):
        pos = 0.0
        for asset in self.position.keys():
            pos += get_crypto_asset_usd_price(asset) * self.position[asset]
        return pos