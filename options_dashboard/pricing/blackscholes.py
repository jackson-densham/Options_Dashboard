import math
import statistics as stats

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
    def implied_vol(self, contract, market, market_price, sigma0=0.15, tol=1e-6, max_iter=50):
        expiry = contract.expiry
        strike = float(contract.strike)

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