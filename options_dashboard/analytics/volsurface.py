class VolSurface:
    def __init__(self, points_df, asof, spot, rate_curve, div_curve=None, atm_definition="forward", x_axis="log_moneyness"):
        self