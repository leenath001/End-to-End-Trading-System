## strategy signal generation

# imports 
from systems.equity import Equity # DO NOT delete 'systems.', needed for upstream imports
import numpy as np
import time
import statsmodels.api as sm
from datetime import datetime
from abc import ABC, abstractmethod

# base class
class Strategy(ABC):
    def __init__(self,symbol):
        self.symbol = symbol.upper()
        self.equity = Equity(symbol)
        self.strategy_errors = []
    
    @abstractmethod
    def compute_signal(self):
        pass

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
            self.strategy_errors.append(f"[MR] Strategty Error @ {datetime.now()}: {e}")
            print(f"[MR] Strategty Error @ {datetime.now()}: {e}")
            
class RandomStrategy(Strategy):
    ## is this acc random
    def __init__(self, symbol, window = 20, z_thresh = 2.0):
        super().__init__(symbol)
        self.window = ["BUY", 'SELL',None]
        self.index = 0
    
    def compute_signal(self):
        self.index+=1
        return self.window[(self.index-1)%3]  
    
class AutoRegresion(Strategy):
    ## AR1 strategy based on previous bars

    def __init__(self, symbol):
        super().__init__(symbol)

    def _regression(self):
        ## Runs AR(1) model on historical quotes in equity class 
        y = self.equity.get_prices()
        model = sm.tsa.AutoReg(y,lags = 1, trend='n')
        fitted = model.fit()
        next_period_pred = fitted.forecast(steps=1)
        return next_period_pred[0]  

    def compute_signal(self):
        try:
            pred = self._regression()
            if pred >= self.equity.last_trade:
                return "BUY"
            else:
                return "SELL"
            
        except Exception as e:
            self.strategy_errors.append(f"[AR] Strategy Error @ {datetime.now()}: {e}")
            print(f"[AR] Strategy Error @ {datetime.now()}: {e}")