# analytics/ivpoints.py
import pandas as pd
import numpy as np
import math

def build_iv_points(chain_df, pricer, market,
                    price_col="mid",
                    min_price=1e-4):

    rows = []

    for _, row in chain_df.iterrows():
        price = row[price_col]
        if price is None or price <= min_price:
            continue

        contract = row["contract"]  # or however you store it

        # intrinsic check (European)
        S = market.spot
        K = contract.strike
        T = contract.time_to_expiry(market.asof)
        r = market.rate

        if contract.option_type == "C":
            intrinsic = max(0.0, S - K * math.exp(-r * T))
        else:
            intrinsic = max(0.0, K * math.exp(-r * T) - S)

        if price < intrinsic:
            continue

        iv = pricer.implied_vol(
            contract=contract,
            market=market,
            market_price=price
        )

        if not np.isfinite(iv):
            continue

        rows.append({
            "expiry": contract.expiry,
            "T": T,
            "strike": K,
            "option_type": contract.option_type,
            "mid": price,
            "iv": iv
        })

    return pd.DataFrame(rows)
