## strategy signal generation

# imports 
from systems.equity import Equity
import numpy as np
import time
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

# child class inherets from Strategy
class MeanReversion(Strategy):
    """
    Simple Z-score mrev intraday strategy
    BUY: price score is below z_thresh 
    SELL: price score is above z_thresh
    """

    def __init__(self, symbol, window = 20, z_thresh = 1.5):
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
            
class ORBstrategy(Strategy):
    """
    Opening Range Breakout (ORB) intraday strategy.

    openRange: number of initial bars that define the opening range.
    Logic:
        - Use first `openRange` prices to define [low, high].
        - After that:
            BUY  if current price > opening_range_high
            SELL if current price < opening_range_low
        - Otherwise: no signal.
    """

    def __init__(self, symbol, openRange=15):
        super().__init__(symbol)
        self.openRange = openRange
        self.or_high = None
        self.or_low = None
        self.last_signal = None

    def compute_signal(self):
        try:
            prices = self.equity.get_prices(self.openRange + 1)

            if prices is None or len(prices) < self.openRange:
                print(f"{self.symbol}: waiting for opening range to complete")
                return None

            if self.or_high is None or self.or_low is None:
                opening_slice = prices[:self.openRange]
                self.or_high = float(np.max(opening_slice))
                self.or_low = float(np.min(opening_slice))
                print(f"{self.symbol}: Opening range set. High={self.or_high}, Low={self.or_low}")

                if len(prices) == self.openRange:
                    return None

            last_price = float(prices[-1])

            signal = None
            # Breakout above
            if last_price > self.or_high:
                signal = "BUY"
            # Breakout below
            elif last_price < self.or_low:
                signal = "SELL"

            if signal is not None and signal != self.last_signal:
                self.last_signal = signal
                return signal

            return None

        except Exception as e:
            msg = f"Strategy Error @ {datetime.now()}: {e}"
            self.strategy_errors.append(msg)
            print(msg)
            return None