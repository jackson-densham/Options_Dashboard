import pandas as pd
import numpy as np

class VolModels:
    @staticmethod
    def _to_returns(history, log=True):
        s = pd.Series(history).dropna()
        if log:
            return np.log(s).diff().dropna()
        return s.pct_change().dropna()

    @staticmethod
    def rolling_realized(history, window=20, annualize=252, log=True):
        r = VolModels._to_returns(history, log=log)
        vol_series = r.rolling(window=window).std() * np.sqrt(annualize)
        return float(vol_series.dropna().iloc[-1])
    
    @staticmethod
    def ewma(history, span=20, annualize=252, log=True, adjust=False):
        r = VolModels._to_returns(history, log=log)
        vol_series = r.ewm(span=span, adjust=adjust).std() * np.sqrt(annualize)
        return float(vol_series.dropna().iloc[-1])
    
    @staticmethod
    def garch():
        pass