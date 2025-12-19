class Contract:
    def __init__(self, strike, expiry, option_type, exercise_style,):
        self.strike = strike
        self.expiry = expiry
        self.option_type = option_type
        self.exercise_style = exercise_style

    def time_to_expiry(self, market):
        days = (self.expiry - market.asof).days
        return max(days / 365.0, 0.0)