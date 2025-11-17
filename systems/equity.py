## ingests and builds 'book' of quotes from gateway_in

# imports
from collections import deque
import numpy as np

class Equity:
    """
    Works with Alpaca and AlphaVantage API
    """
    _instances = {}  

    def __new__(cls, symbol):
        symbol = symbol.upper()
        if symbol not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[symbol] = instance
        return cls._instances[symbol]

    def __init__(self, symbol: str):
        if not hasattr(self, "_initialized"):
            self.symbol = symbol.upper()
            self.trades = deque(maxlen = 1000)
            self.last_trade = None
            self.quotes = {"Bid": None,"Bid Size": None, "Ask": None,"Ask Size": None, "Mid": None, "Spread": None}
            self._initialized = True

    def update_trade(self, price, size, timestamp):
        """
        Updates recent trades deque
        """
        dic = {"Price": price, "Size": size, "Timestamp": timestamp}
        self.trades.append(dic)
        self.last_trade = price

    def update_quote(self, bp, bsz, ap, asksz):
        """
        Updates quotes to top-of-book
        """
        self.quotes["Bid"] = bp
        self.quotes["Bid Size"] = bsz
        self.quotes["Ask"] = ap
        self.quotes["Ask Size"] = asksz
        self.quotes["Mid"] = (bp + ap) / 2
        self.quotes["Spread"] = (ap - bp)

    def get_prices(self,window = 10):
        """
        Grabs prices for signal generation
        """
        if len(self.trades) < window:
            return None
        return np.array([t["Price"] for t in list(self.trades)])
    
    def mean_price(self, window=10):
        """
        Compute rolling mean price
        """
        prices = self.get_prices(window)
        if prices is None:
            return None
        return float(np.mean(prices))

    def std_price(self, window=20):
        """
        Compute rolling std of prices
        """
        prices = self.get_prices(window)
        if prices is None:
            return None
        return float(np.std(prices))
    
    def __repr__(self):
        bid = self.quotes["Bid"]
        ask = self.quotes["Ask"]
        mid = self.quotes["Mid"]
        return f"{self.symbol}: Bid @ {bid}, Ask @ {ask}, Mid @ {mid}"