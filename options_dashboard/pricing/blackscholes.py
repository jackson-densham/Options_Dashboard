import math
import statistics as stats
from options_dashboard.core.types import OptionType

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

        if option_type is OptionType.CALL:
            value = (S*math.exp(-D*T)*stats.NormalDist(0,1).cdf(d_1))-(E*math.exp(-r*T)*stats.NormalDist(0,1).cdf(d_2))
        elif option_type is OptionType.PUT:
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

        if option_type is OptionType.CALL:
            delta = math.exp(-D*T)*stats.NormalDist(0,1).cdf(d_1)
        elif option_type is OptionType.PUT:
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

        if option_type is OptionType.CALL:
            gamma = (math.exp(-D*T)*stats.NormalDist(0,1).pdf(d_1)) / (sigma*S*math.sqrt(T))
        elif option_type is OptionType.PUT:
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

        if option_type is OptionType.CALL:
            theta = -(1/365)*((-(sigma*S*math.exp(-D*T)*stats.NormalDist(0,1).pdf(d_1))/(2*math.sqrt(T))) + (D*S*stats.NormalDist(0,1).cdf(d_1)*math.exp(-D*T)) - (r*E*math.exp(-r*T)*stats.NormalDist(0,1).cdf(d_2)))
        elif option_type is OptionType.PUT:
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

        if option_type is OptionType.CALL:
            vega = (S*math.sqrt(T)*math.exp(-D*T)*stats.NormalDist(0,1).pdf(d_1))
        elif option_type is OptionType.PUT:
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

        if option_type is OptionType.CALL:
            rho = (E*T*math.exp(-r*T)*stats.NormalDist(0,1).cdf(d_2))/100
        elif option_type is OptionType.PUT:
            rho = (-E*T*math.exp(-r*T)*stats.NormalDist(0,1).cdf(-d_2))/100
        else:
            raise ValueError("Option type specified incorrectly")
        
        return rho

    def implied_vol(self, contract, market, market_price,
                sigma0=0.15, tol=1e-6, max_iter=50,
                sigma_min=1e-6, sigma_max=5.0,
                bisect_max_iter=100):
        # helper: pricing error as a function of sigma
        def f(sig: float) -> float:
            return self.price(contract, market, sigma_overide=sig) - market_price

        # --- 1) NEWTON TRY ---
        sigma = float(sigma0)
        last_err = None

        for _ in range(max_iter):
            err = f(sigma)

            if abs(err) < tol:
                return sigma

            v = self.vega(contract, market, sigma_overide=sigma)

            # Newton failure conditions
            if (not math.isfinite(err)) or (not math.isfinite(v)) or (v < 1e-10):
                break

            step = err / v
            sigma_new = sigma - step

            # If Newton jumps out of bounds or doesn't improve, bail to bisection
            if (sigma_new <= sigma_min) or (sigma_new >= sigma_max):
                break
            if last_err is not None and abs(err) >= abs(last_err) * 0.999:
                # not improving (or improving too slowly) -> fallback
                break

            sigma = sigma_new
            last_err = err

        # --- 2) BISECTION FALLBACK ---
        # Find a bracket [lo, hi] such that f(lo) <= 0 <= f(hi) (or vice-versa)
        lo = sigma_min
        hi = min(max(sigma0, 0.3), sigma_max)  # start hi somewhat reasonable

        f_lo = f(lo)
        f_hi = f(hi)

        # Expand hi until we bracket, or hit sigma_max
        # (for deep OTM options you may need large vol to raise price)
        expand_count = 0
        while f_lo * f_hi > 0 and hi < sigma_max and expand_count < 30:
            hi = min(hi * 2.0, sigma_max)
            f_hi = f(hi)
            expand_count += 1

        # If still no bracket, try shrinking lo upward (rare case where f(lo)>0)
        # This can happen if market_price is below intrinsic/arb, or pricing mismatch.
        if f_lo * f_hi > 0:
            lo2 = 1e-4
            while f_lo * f_hi > 0 and lo2 < hi:
                lo2 *= 2.0
                f_lo = f(lo2)
            lo = lo2

        # If we cannot bracket, return NaN (or raise) — market price likely inconsistent
        if not (math.isfinite(f_lo) and math.isfinite(f_hi)) or f_lo * f_hi > 0:
            return float("nan")

        # Standard bisection
        for _ in range(bisect_max_iter):
            mid = 0.5 * (lo + hi)
            f_mid = f(mid)

            if abs(f_mid) < tol:
                return mid

            # Keep the sub-interval that brackets the root
            if f_lo * f_mid <= 0:
                hi = mid
                f_hi = f_mid
            else:
                lo = mid
                f_lo = f_mid

            # Optional: interval width stop
            if (hi - lo) < 1e-10:
                return 0.5 * (lo + hi)

        return 0.5 * (lo + hi)
