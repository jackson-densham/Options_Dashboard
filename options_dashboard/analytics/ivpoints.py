from options_dashboard.data.data import get_spot_and_history, get_option_chain, get_mid_from_chain

def iv_points(ticker):
    spot = get_spot_and_history(ticker)
    chain = get_option_chain(ticker)

    # Loop through each available expiry

    # Loop through each contract for each expiry
    # Create a data frame with DTE, strike, and IV for each contract