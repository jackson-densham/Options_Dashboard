import yfinance as yf
import pandas as pd
import math

def get_spot_and_history(ticker):
    history = yf.Ticker(ticker).history(period='1y', interval='1d', actions=False)['Close']
    spot = yf.Ticker(ticker).fast_info.get('lastPrice')
    return spot, history

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

def get_rate(ticker='^IRX'):
    rate = (yf.Ticker(ticker).history(period='5d', interval='1d', actions=False)['Close'].dropna().iloc[-1]) / 100
    return math.log(1 + rate)

def get_div_yield(ticker):
    div_yield = yf.Ticker(ticker).info.get('dividendYield')
    return 0.0 if div_yield is None else math.log(1 + div_yield)

def get_mid_from_chain(chain, expiry, strike, opt_type):
    row = chain[(chain["expiry"] == expiry) & (chain["strike"] == strike) & (chain["option_type"] == opt_type)]
    if row.empty:
        raise ValueError("No matching option found")
    return float(row["mid"].iloc[0])