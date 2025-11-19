# Backtester using data collected from YF_endpoint
# YF_ENDPOINT -> equity.data_dict -> strategy -> 

import systems.strategy as strat
from systems.equity import Equity

class BACKTESTING_ENGINE:
    
    def __init__(self, symbols, strategy, data_endpoint, initial_cash=100000):
        self.symbols = symbols
        self.strategy = strategy                # singular
        self.data_endpoint_cls = data_endpoint
        self.cash = initial_cash
        self.positions = {sym: 0 for sym in self.symbols}
        self.last_trade = {sym: 0 for sym in self.symbols}  # 0 = no trade yet
        self.eq = {sym: Equity(sym) for sym in self.symbols}
        self.equity_curve = []
        self.logs = []

        # set up endpoint & stream
        self.endpoint = self.data_endpoint_cls(self.symbols, '7d', '1m')
        self.endpoint.data_grabber()
        self._stream_iter = self.endpoint.stream()

    def load_next_tick(self):
        """
        Advance the backtest by one bar (one timestamp).
        Returns (ts, bars) or None when data is exhausted.
        """
        try:
            ts, bars = next(self._stream_iter)
        except StopIteration:
            return None

        for sym in self.symbols:
            bar = bars[sym]
            self.eq[sym].update_trade(
                price=bar["close"],
                size=bar["volume"],
                timestamp=ts,
            )

        return ts, bars

    def run(self):
        SHARES = 10

        while True:
            tick = self.load_next_tick()   # or load_data() if you kept that name
            if tick is None:
                break

            ts, bars = tick
            ticker = self.strategy.symbol
            signal = self.strategy.compute_signal()

            price = bars[ticker]["close"]
            trade_value = SHARES * price

            if signal == "BUY":
                if self.last_trade[ticker] == 1:
                    print(f"{ts} | Already long {ticker}, skipping BUY")
                    continue

                if self.cash >= trade_value:
                    self.cash -= trade_value
                    self.positions[ticker] += SHARES
                    self.last_trade[ticker] = 1
                else:
                    print(f"Not enough cash: cash=${self.cash}, tradeValue=${trade_value}")

            elif signal == "SELL":
                if self.last_trade[ticker] == -1:
                    print(f"{ts} | Already just sold {ticker}, skipping SELL")
                    continue

                if self.positions[ticker] >= SHARES:
                    self.cash += trade_value      
                    self.positions[ticker] -= SHARES
                    self.last_trade[ticker] = -1 
                else:
                    print(f"Not enough position to sell {SHARES} shares of {ticker}")


                portfolio_value = self.cash + sum(self.positions[s] * bars[s]["close"] for s in self.symbols)
                self.equity_curve.append((ts, portfolio_value))


