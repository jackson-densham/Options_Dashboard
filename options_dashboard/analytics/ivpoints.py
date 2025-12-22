import math
import pandas as pd

from options_dashboard.core.contract import Contract
from options_dashboard.data.data import get_option_chain
from options_dashboard.pricing.blackscholes import BlackScholesPricer


def build_iv_points(
    ticker: str,
    market,
    option_type: str = "call",      # "call" or "put" (matches your chain column)
    expiries=None,                  # list[date] or None
    strike_min=None,
    strike_max=None,
    min_mid: float = 0.01,
    max_spread_pct: float = 0.30,   # drop super-wide markets (30% of mid)
    pricer=None,
):
    """
    Returns a DataFrame of IV points with columns:
    expiry, T, strike, option_type, mid, iv
    """
    pricer = pricer or BlackScholesPricer()

    chain = get_option_chain(ticker)

    # --- filter ---
    df = chain.copy()
    df = df[df["option_type"] == option_type]

    if expiries is not None:
        df = df[df["expiry"].isin(expiries)]

    if strike_min is not None:
        df = df[df["strike"] >= float(strike_min)]
    if strike_max is not None:
        df = df[df["strike"] <= float(strike_max)]

    # liquidity / sanity filters
    df = df[df["mid"] >= float(min_mid)]
    df = df[(df["ask"] > 0) & (df["bid"] > 0)]

    # drop crazy-wide spreads
    spread = (df["ask"] - df["bid"]).astype(float)
    mid = df["mid"].astype(float)
    df = df[(spread / mid) <= float(max_spread_pct)]

    # --- compute IVs ---
    rows = []
    for r in df.itertuples(index=False):
        expiry = r.expiry
        strike = float(r.strike)
        market_price = float(r.mid)

        # your Contract expects option_type "1"/"2" or "Call"/"Put"
        bs_type = "Call" if option_type == "call" else "Put"
        contract = Contract(
            strike=strike,
            expiry=expiry,
            option_type=bs_type,
            exercise_style="European",
        )

        T = contract.time_to_expiry(market)
        if T <= 0:
            continue

        iv = pricer.implied_vol(contract, market, market_price)

        if iv is None or (isinstance(iv, float) and (math.isnan(iv) or iv <= 0)):
            continue

        rows.append(
            {
                "expiry": expiry,
                "T": T,
                "strike": strike,
                "option_type": option_type,
                "mid": market_price,
                "iv": float(iv),
            }
        )

    return pd.DataFrame(rows).sort_values(["expiry", "strike"]).reset_index(drop=True)
