import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime as dt
import math
import statistics as stats

# Market Data Class
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


# Vanilla option class
class Contract:
    def __init__(self, strike, expiry, option_type, exercise_style,):
        self.strike = strike
        self.expiry = expiry
        self.option_type = option_type
        self.exercise_style = exercise_style

    def time_to_expiry(self, market):
        days = (self.expiry - market.asof).days
        return max(days / 365.0, 0.0)

# Pricing Models
# Black Scholes
class BlackScholesPricer:
    def price(self, contract, market, sigma_overide=None):
        option_type = contract.option_type
        S = market.spot
        E = float(contract.strike)
        r = market.rate
        D = market.div_yield
        T = contract.time_to_expiry(market)

        # use override if provided
        sigma = sigma_overide if sigma_overide is not None else market.sigma(E, T)

        d_1 = (math.log(S/E) + ((r - D + (0.5*sigma**2))*(T))) / (sigma*math.sqrt(T))
        d_2 = d_1 - (sigma*math.sqrt(T))

        if option_type == '1' or option_type == 'Call':
            value = (S*math.exp(-D*T)*stats.NormalDist(0,1).cdf(d_1))-(E*math.exp(-r*T)*stats.NormalDist(0,1).cdf(d_2))
        elif option_type == '2' or option_type == 'Put':
            value = (-S*math.exp(-D*T)*stats.NormalDist(0,1).cdf(-d_1))+(E*math.exp(-r*T)*stats.NormalDist(0,1).cdf(-d_2))
        else:
            raise ValueError('Option type specified incorrectly')
        
        return value
    def delta(self, contract, market):
        option_type = contract.option_type
        S = market.spot
        E = float(contract.strike)
        r = market.rate
        D = market.div_yield
        T = contract.time_to_expiry(market)
        sigma = market.sigma(E, T)

        d_1 = (math.log(S/E) + ((r - D + (0.5*sigma**2))*(T))) / (sigma*math.sqrt(T))

        if option_type == '1' or option_type == 'Call':
            delta = math.exp(-D*T)*stats.NormalDist(0,1).cdf(d_1)
        elif option_type =='2' or option_type =='Put':
            delta = math.exp(-D*T)*(stats.NormalDist(0,1).cdf(d_1)-1)
        else:
            raise ValueError("Option type specified incorrectly")
        
        return delta
    def gamma(self, contract, market):
        option_type = contract.option_type
        S = market.spot
        E = float(contract.strike)
        r = market.rate
        D = market.div_yield
        T = contract.time_to_expiry(market)
        sigma = market.sigma(E, T)

        d_1 = (math.log(S/E) + ((r - D + (0.5*sigma**2))*(T))) / (sigma*math.sqrt(T))

        if option_type == '1' or option_type == 'Call':
            gamma = (math.exp(-D*T)*stats.NormalDist(0,1).pdf(d_1)) / (sigma*S*math.sqrt(T))
        elif option_type =='2' or option_type =='Put':
            gamma = (math.exp(-D*T)*stats.NormalDist(0,1).pdf(d_1)) / (sigma*S*math.sqrt(T))
        else:
            raise ValueError("Option type specified incorrectly")
        
        return gamma
    def theta(self, contract, market):
        option_type = contract.option_type
        S = market.spot
        E = float(contract.strike)
        r = market.rate
        D = market.div_yield
        T = contract.time_to_expiry(market)
        sigma = market.sigma(E, T)

        d_1 = (math.log(S/E) + ((r - D + (0.5*sigma**2))*(T))) / (sigma*math.sqrt(T))
        d_2 = d_1 - (sigma*math.sqrt(T))

        if option_type == '1' or option_type == 'Call':
            theta = -(1/365)*((-(sigma*S*math.exp(-D*T)*stats.NormalDist(0,1).pdf(d_1))/(2*math.sqrt(T))) + (D*S*stats.NormalDist(0,1).cdf(d_1)*math.exp(-D*T)) - (r*E*math.exp(-r*T)*stats.NormalDist(0,1).cdf(d_2)))
        elif option_type =='2' or option_type =='Put':
            theta = -(1/365)*((-(sigma*S*math.exp(-D*T)*stats.NormalDist(0,1).pdf(-d_1))/(2*math.sqrt(T))) + (D*S*stats.NormalDist(0,1).cdf(-d_1)*math.exp(-D*T)) - (r*E*math.exp(-r*T)*stats.NormalDist(0,1).cdf(-d_2)))
        else:
            raise ValueError("Option type specified incorrectly")
        
        return theta
    def vega(self, contract, market, sigma_overide=None):
        option_type = contract.option_type
        S = market.spot
        E = float(contract.strike)
        r = market.rate
        D = market.div_yield
        T = contract.time_to_expiry(market)

        # use override if provided
        sigma = sigma_overide if sigma_overide is not None else market.sigma(E, T)

        d_1 = (math.log(S/E) + ((r - D + (0.5*sigma**2))*(T))) / (sigma*math.sqrt(T))

        if option_type == '1' or option_type == 'Call':
            vega = (S*math.sqrt(T)*math.exp(-D*T)*stats.NormalDist(0,1).pdf(d_1))
        elif option_type =='2' or option_type =='Put':
            vega = (S*math.sqrt(T)*math.exp(-D*T)*stats.NormalDist(0,1).pdf(d_1))
        else:
            raise ValueError("Option type specified incorrectly")
        
        return vega
    def rho(self, contract, market):
        option_type = contract.option_type
        S = market.spot
        E = float(contract.strike)
        r = market.rate
        D = market.div_yield
        T = contract.time_to_expiry(market)
        sigma = market.sigma(E, T)

        d_1 = (math.log(S/E) + ((r - D + (0.5*sigma**2))*(T))) / (sigma*math.sqrt(T))
        d_2 = d_1 - (sigma*math.sqrt(T))

        if option_type == '1' or option_type == 'Call':
            rho = (E*T*math.exp(-r*T)*stats.NormalDist(0,1).cdf(d_2))/100
        elif option_type =='2' or option_type =='Put':
            rho = (-E*T*math.exp(-r*T)*stats.NormalDist(0,1).cdf(-d_2))/100
        else:
            raise ValueError("Option type specified incorrectly")
        
        return rho
    def implied_vol(self, contract, market, ticker, sigma0=0.15, tol=1e-6, max_iter=50):
        expiry = contract.expiry
        strike = float(contract.strike)

        chain = get_option_chain(ticker)

        # map option type to chain option_type
        # (your chain uses "call"/"put")
        if contract.option_type in ("1", "Call"):
            opt_type = "call"
        elif contract.option_type in ("2", "Put"):
            opt_type = "put"
        else:
            raise ValueError("Option type specified incorrectly")

        row = chain[
            (chain["expiry"] == expiry) &
            (chain["strike"] == strike) &
            (chain["option_type"] == opt_type)
        ]

        if row.empty:
            raise ValueError("No matching option found in chain for that expiry/strike/type")

        market_price = float(row["mid"].iloc[0])

        sigma = float(sigma0)

        for _ in range(max_iter):
            e = self.price(contract, market, sigma_overide=sigma) - market_price
            if abs(e) < tol:
                return sigma

            v = self.vega(contract, market, sigma_overide=sigma)
            if v < 1e-10:
                break  # vega too small -> Newton unstable

            sigma = sigma - (e / v)
            sigma = max(1e-6, min(sigma, 5.0))  # keep sigma sane

        raise RuntimeError("IV solver did not converge")
    
# Binomial Asset Pricing Model
class BinomialAssetPricer:
    ...
# Monte Carlo
class MonteCarloPricer:
    ...
# Heston
class HestonPricer:
    ...

# Data pulling
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

#Analytics
# Term Structure Plot Function

# Volatility Smile Plot Function

# IV Surface Function

# Vol Analytics Function

# Function to pull up the main menu
def show_main_menu():
    print("OPTIONS DASHBOARD V1.0 ")
    print("MENU")
    print("1. Contract Analysis")
    print("2. Strategy Analysis")
    main_menu_selection = input("")
    return main_menu_selection

# Function to pull up the contract analysis menu
def show_contract_menu():
    print("CONTRACT ANALYSIS")
    print("1. Pricing")
    print("2. Term Structure Plot")
    print("3. Voltility Smile Plot")
    print("4. IV Surface")
    print("5. Vol Analysis")
    contract_menu_selection = input("")
    return contract_menu_selection

# Function to pull up the pricing menu
def show_pricing_menu():
    print("PRICING")
    print("1. Binomial Asset Pricing Model")
    print("2. Black-Scholes Pricing Model")
    print("3. Monte Carlo Pricing")
    print("4. Heston Model")
    pricing_menu_selection = input("")
    return pricing_menu_selection

# Function to pull up the contract info menu
def show_contract_info_menu(ticker):
    print("CONTRACT INFO")
    print("Select Option Type")
    print("1. Call")
    print("2. Put")
    option_type = input("")
    print("Select Expiration")
    print(get_option_chain(ticker)['expiry'].unique())
    expiry = input("")
    expiry = dt.datetime.strptime(expiry, "%Y-%m-%d").date()
    print("Select Strike")
    print(get_option_chain(ticker)['strike'].unique())
    strike = input("")
    return option_type, expiry, strike

# Function to pull up the vol analysis menu
def show_vol_analysis_menu():
    print("VOL ANALYSIS")
    print("1. Implied Volatility")
    volume_analysis_selection = input("")
    return volume_analysis_selection

# Show the main menu initially
main_menu_selection = show_main_menu()

# Loop to continue showing the main menu untill a valid selection is made
main_menu = True
market = None
while main_menu == True:
    if main_menu_selection == "1" or main_menu_selection == "Contract Analysis":
        ticker = input("Yahoo Finance Ticker:").strip().upper()
        asof = dt.date.today()
        spot, history = get_spot_and_history(ticker)
        rate = get_rate()
        div_yield = get_div_yield(ticker)
        vol = 0.1417
        market = MarketData(asof=asof, spot=spot, rate=rate, div_yield=div_yield, vol=vol)
        contract_menu_selection = show_contract_menu()
        main_menu = False
    elif main_menu_selection == "2" or main_menu_selection == "Strategy Analysis":
        print("Strategy Analysis Coming Soon")
        main_menu_selection = show_main_menu()
    else:
        print("Not an option, select from the menu")
        main_menu_selection = show_main_menu()

# Loop to continue showing the contract menu untill a valid selection is made
if main_menu_selection == "1" or main_menu_selection == "Contract Analysis":
    contract_menu = True
    while contract_menu == True:
        if contract_menu_selection == "1" or contract_menu_selection == "Pricing":
            pricing_menu_selection = show_pricing_menu()
            contract_menu = False
        elif contract_menu_selection == "2" or contract_menu_selection == "Term Structure Plot":
            print("Term structure coming soon")
            contract_menu = False
        elif contract_menu_selection == "3" or contract_menu_selection == "Volatility Smile Plot":
            maturity = input("Select a maturity")
            contract_menu = False
        elif contract_menu_selection == "4" or contract_menu_selection == "IV Surface":
            print("Vol surface coming soon")
            contract_menu = False
        elif contract_menu_selection == "5" or contract_menu_selection == "Vol Analysis":
            vol_analysis_selection = show_vol_analysis_menu()
            contract_menu = False
        else:
            print("Not an option, select from the menu")
            contract_menu_selection = show_contract_menu()

# Loop to continue showing the pricing menu unitll a valid selection is made
if contract_menu_selection == "1" or contract_menu_selection == "Pricing":
    pricing_menu = True
    while pricing_menu == True:
        if pricing_menu_selection == "1" or pricing_menu_selection == "Binomial Asset Pricing Model":
            pricing_menu = False
        elif pricing_menu_selection == "2" or pricing_menu_selection == "Black-Scholes Pricing Model":
            option_type, expiry, strike = show_contract_info_menu(ticker)
            contract = Contract(strike=strike, expiry=expiry, option_type=option_type, exercise_style='European')
            pricer = BlackScholesPricer()
            value = pricer.price(contract, market)
            delta = pricer.delta(contract, market)
            gamma = pricer.gamma(contract, market)
            theta = pricer.theta(contract, market)
            vega = pricer.vega(contract, market)/100
            print(f"Contract Value: {value}")
            print(f"Contract Delta: {delta}")
            print(f"Contract Gamma: {gamma}")
            print(f"Contract Theta: {theta}")
            print(f"Contract Vega: {vega}")

            pricing_menu = False
        elif pricing_menu_selection == "3" or pricing_menu_selection == "Monte Carlo Pricing":
            pricing_menu = False
        elif pricing_menu_selection == "4" or pricing_menu_selection == "Heston Model":
            pricing_menu = False
        else:
            print("Not an option, select from the menu")
            pricing_menu_selection = show_pricing_menu()

# Loop to continue showing the vol analysis menu untill a valis selection is made
if contract_menu_selection == "5" or contract_menu_selection == "Vol Analysis":
    vol_analysis_menu = True
    while vol_analysis_menu == True:
        if vol_analysis_selection == "1" or vol_analysis_selection == "Implied Volatility":
            option_type, expiry, strike = show_contract_info_menu(ticker)
            contract = Contract(strike=strike, expiry=expiry, option_type=option_type, exercise_style='European')
            pricer = BlackScholesPricer()
            iv = pricer.implied_vol(contract, market, ticker)
            print(f"IV: {iv}")