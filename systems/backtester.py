# Backtester using data collected from YF_endpoint
# YF_ENDPOINT -> equity.data_dict -> strategy -> 

import systems.strategy as strat
from systems.equity import Equity

class BACKTESTING_ENGINE:

    def __init__(self,symbols, strategies, data_endpoint, initial_cash = 100000):
        self.symbols = symbols
        self.strategies = strategies
        self.data_endpoint = data_endpoint
        self.initial_cash = initial_cash
        self.positions = {}
        self.eq = {}
        self.equity_curve = []
        self.logs = []
        for sym in self.symbols:
            self.eq[sym] = Equity(sym)

    def load_data(self):
        """
        Loads data sourced from YF into equity class
        """
        endpoint = self.data_endpoint(self.symbols, '7d', '1m')
        endpoint.data_grabber()

        for ts, bars in endpoint.stream():
            for sym in self.symbols:
                bar = bars[sym]
                self.eq[sym].update_trade(price = bar["close"], size  = bar["volume"],timestamp = ts)
                
    def run(self):
        """
        Runs simulation backtest using pre-loaded YF data.
        load_data() must be called before this.
        """
        pass 
