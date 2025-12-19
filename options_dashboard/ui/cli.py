import datetime as dt

from options_dashboard.core.market import MarketData
from options_dashboard.core.contract import Contract
from options_dashboard.pricing.blackscholes import BlackScholesPricer
from options_dashboard.data.data import get_spot_and_history, get_option_chain, get_rate, get_div_yield, get_mid_from_chain
from options_dashboard.analytics.volanalytics import VolModels

def run():
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
        print("1. Pricing and Greeks")
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
            vol = VolModels.rolling_realized(history)
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
                chain = get_option_chain(ticker)
                opt_type = "call" if option_type in ("1", "Call") else "put"
                market_price = get_mid_from_chain(chain, expiry, float(strike), opt_type)
                iv = pricer.implied_vol(contract, market, market_price)
                rolling_vol = VolModels.rolling_realized(history)
                ewma_vol = VolModels.ewma(history)
                print(f"IV: {iv}")
                print(f"20d Realized Vol: {rolling_vol}")
                print(f"EWMA Vol Forecast: {ewma_vol}")
                print(f"IV - 20d Rolling RV Spread: {iv - rolling_vol}")
                print(f"IV - RV EWMA spread {iv - ewma_vol}")

if __name__ == "__main__":
    run()