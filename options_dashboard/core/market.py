import math

class MarketData:
    def __init__(self, asof, spot, rate, div_yield = 0.0, vol = None, vol_surface = None):
        self.asof = asof
        self.spot = spot
        self.rate = rate
        self.div_yield = div_yield
        self.vol = vol
        self.vol_surface = vol_surface

        if self.vol is None and self.vol_surface is None:
            raise ValueError("Must provide vol or vol_surface")
    
    def discount(self, T):
        return math.exp(-self.rate * T)
    
    def forward(self, T):
        return self.spot * math.exp((self.rate - self.div_yield)*T)
    
    def sigma(self, strike, T):
        if self.vol_surface is not None:
            return self.vol_surface.vol(strike, T)
        return self.vol