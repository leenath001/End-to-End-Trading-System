# Backtester using data collected from YF_endpoint

import systems.strategy as strat

class BACKTESTING_ENGINE:

    def __init__(self,symbols, strategies, data_endpoint, initial_cash = 100000):
        self.symbols = symbols
        self.strategies = strategies
        self.data_endpoint = data_endpoint
        self.initial_cash = initial_cash
        self.positions = {}
        self.equity_curve = []
        self.logs = []

    def run_backtest(self):
        for ts, bars in self.data_endpoint.stream():
            for strat in self.strategies:   # make faster?
                price = bars[strat.symbol]['close']
                signal = strat.compute_signal(self)
        

