from abc import ABC, abstractmethod
import numpy as np
from scipy.stats import norm


class Equity(ABC):
    """Abstract class for equity
    """
    def get_name(self):
        """Getter for name
        :return: string, market name of the equity
        """
        return self._market_name

    def get_denominated(self):
        """Getter for denominated
        :return: string, denomination currency
        """
        return self._denominated

    def __repr__(self):
        """standard overload
        :return: a string
        """
        out = 'Equity: {0} ({1})'.format(self.get_name(), self.get_denominated())
        return out

    def __str__(self):
        """Standard overload
        :return: a string
        """
        return self.__repr__()

    def __init__(self, market_name, denominated, country, region):
        self._market_name = market_name
        self._denominated = denominated
        self._country = country
        self._region = region
        ABC.__init__(self)

    @abstractmethod
    def get_spot(self):
        pass


class TradableEquity(Equity):
    """Concrete class for an equity
    """
    def __init__(self, market_name, denominated, country, region):
        Equity.__init__(self, market_name, denominated, country, region)

    def get_spot(self):
        """Get the spot of the equity
        :return: a double
        """
        return 100.0


class Option(ABC):
    """Base class for an option
    """

    def get_underlyer(self):
        """Getter method for the underlyer
        :return: an Equity object
        """
        return self._underlyer

    def get_underlyer_spot(self):
        """Getter method
        :return: a double
        """
        underlyer = self.get_underlyer()
        return underlyer.spot()

    def get_strike(self):
        """Getter for option strike
        :return: a double
        """
        return self._strike

    def get_volatility(self):
        """Getter for option volatility
        :return: a double
        """
        return self._volatility

    def get_interest_rate(self):
        """Getter for option interest rate
        :return: a double
        """
        return self._interest_rate

    def get_time_to_expiry(self):
        """Getter for option time to expiry
        :return: a double
        """
        return self._time_to_expiry

    def get_option_type(self):
        """Getter for option type
        :return: a string
        """
        return self._option_type

    def __repr__(self):
        out = '{0} on {1}, with strike {2}, interest rate {3}, expiring in {4}, volatility = {5}'.format(
           self.get_option_type(),
           self.get_underlyer().get_name(),
           self.get_strike(),
           self.get_interest_rate(),
           self.get_time_to_expiry(),
           self.get_volatility(),
        )
        return out

    def __str__(self):
        return self.__repr__()

    def __init__(self, S, K, sigma, r, T, option_type):
        self._underlyer = S
        self._strike = K
        self._volatility = sigma
        self._interest_rate = r
        self._time_to_expiry = T
        self._option_type = option_type
        ABC.__init__(self)

    # TODO handle FX
    """
    @abstractmethod
    def dollar_price(self):
        pass
    """

    @abstractmethod
    def price(self):
        pass


class CallOption(Option):
    """Class for a call option
    """
    def __init__(self, S, K, sigma, r, T):
        Option.__init__(self, S, K, sigma, r, T, "call")

    def price(self):
        S = self.get_underlyer().get_spot()
        K = self.get_strike()
        t = self.get_time_to_expiry()
        r = self.get_interest_rate()
        sigma = self.get_volatility()

        sqrt_t = np.sqrt(t)
        d1 = np.log(S * np.exp(r * t) / K ) / (sigma * sqrt_t) + .5 * sigma * sqrt_t
        d2 = d1 - sigma * sqrt_t
        N = lambda x: norm.cdf(x)

        return S * N(d1) - K * np.exp(-r * t) * N(d2)


class PutOption(Option):
    """Class for a call option
    """
    def __init__(self, S, K, sigma, r, T):
        Option.__init__(self, S, K, sigma, r, T, "put")

    def price(self):
        S = self.get_underlyer().get_spot()
        K = self.get_strike()
        t = self.get_time_to_expiry()
        r = self.get_interest_rate()
        sigma = self.get_volatility()

        sqrt_t = np.sqrt(t)
        d1 = np.log(S * np.exp(r * t) / K ) / (sigma * sqrt_t) + .5 * sigma * sqrt_t
        d2 = d1 - sigma * sqrt_t
        N = lambda x: norm.cdf(x)

        return -S * N(-d1) + K * np.exp(-r * t) * N(-d2)


class Forward(Option):
    """Class for a forward
    """
    def __init__(self, S, K, r, T):
        Option.__init__(self, S, K, 0, r, T, "forward")

    def price(self):
        S = self.get_underlyer().get_spot()
        K = self.get_strike()
        t = self.get_time_to_expiry()
        r = self.get_interest_rate()

        return S - K * np.exp(-r * t)


s1 = TradableEquity(".SPX", "USD", "US", "North America")
K = 100
sigma = .2
r = .1
T = 1

c = CallOption(s1, K, sigma, r, T)
p = PutOption(s1, K, sigma, r, T)
f = Forward(s1, K, r, T)
print(s1)
print(c)
print(p)
print(f)
print('Checking the put call parity:')
print('c-p-f = {0}'.format(c.price() - p.price() - f.price()))
