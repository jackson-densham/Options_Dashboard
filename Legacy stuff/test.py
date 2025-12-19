import pandas as pd
import datetime as dt
from datetime import date
import yfinance as yf
def get_option_chain(ticker):
    tkr = yf.Ticker(ticker)
    expiries = tkr.options

    all_rows = []
    for exp in expiries:
        oc = tkr.option_chain(exp)

        calls = oc.calls.copy()
        calls["option_type"] = "call"

        puts = oc.puts.copy()
        puts["option_type"] = "put"

        df = pd.concat([calls, puts], ignore_index=True)
        df["expiry"] = pd.to_datetime(exp).date()

        df = df[df["bid"].notna() & df["ask"].notna()]
        df = df[(df["bid"] > 0) & (df["ask"] > 0)]
        df["mid"] = (df["bid"] + df["ask"]) / 2
        df = df[df["mid"] > 0]

        all_rows.append(df)
    full_chain = pd.concat(all_rows, ignore_index=True)
    return full_chain

print(get_option_chain('SPY'))