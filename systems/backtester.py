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
        endpoint = self.data_endpoint(self.symbols, '7d', '1m')
        endpoint.data_grabber()
        sample = endpoint.data_dict[self.symbols[0]]

        for _ in range(len(sample)):        
            ts, bars = endpoint.stream()
            for sym in self.symbols:
                self.eq[sym].update_trade(bars[sym]['close'],bars[sym]['volume'],ts)
                
    def run(self):

if __name__ == "__main__":
    pass
