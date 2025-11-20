## strategy signal generation

# imports 
from equity import Equity
import numpy as np
import time
from datetime import datetime

# base class
class Strategy:
    def __init__(self,symbol):
        self.symbol = symbol.upper()
        self.equity = Equity(symbol)
        self.strategy_errors = []

    def compute_signal(self):
        raise NotImplementedError('Must compute signal!')

# child class inherets from Strategy
class MeanReversion(Strategy):
    """
    Simple Z-score mrev intraday strategy
    BUY: price score is below z_thresh 
    SELL: price score is above z_thresh
    """

    def __init__(self, symbol, window = 20, z_thresh = 0.1):
        super().__init__(symbol)
        self.window = window
        self.z_thresh = z_thresh

    def compute_signal(self):
        try:
            prices = self.equity.get_prices(self.window)
            if prices is None or len(prices) < self.window:
                print(f"{self.symbol}: waiting for enough data")
                return None

            mean = np.mean(prices)
            std = np.std(prices)
            last = prices[-1]

            if std == 0:
                return None

            z = (last - mean) / std
            if z < -self.z_thresh:
                return "BUY"
            elif z > self.z_thresh:
                return "SELL"
            return None

        except Exception as e:
            self.strategy_errors.append(f"Strategty Error @ {datetime.now()}: {e}")
            print(f"Strategty Error @ {datetime.now()}: {e}")
            
        
class RandomStrategy(Strategy):

    def __init__(self, symbol, window = 20, z_thresh = 2.0):
        super().__init__(symbol)
        self.window = ["BUY", 'SELL',None]
        self.index = 0
    
    def compute_signal(self):
        self.index+=1
        return self.window[(self.index-1)%3]
