# Backtester using data collected from YF_endpoint
# YF_ENDPOINT -> equity.data_dict -> strategy -> 


from systems.equity import Equity
from systems.gateway_in import YF_ENDPOINT   # adjust import as needed
import systems.strategy as strat
import matplotlib.pyplot as plt

class BACKTESTING_ENGINE:
    
    def __init__(self, symbols, strategy, data_endpoint, initial_cash=100000):
        self.symbols = symbols
        self.strategy = strategy                
        self.data_endpoint_cls = data_endpoint
        self.cash = initial_cash
        self.positions = {sym: 0 for sym in self.symbols}
        self.last_trade = {sym: 0 for sym in self.symbols}  # 0 = no trade yet
        self.eq = {sym: Equity(sym) for sym in self.symbols}
        self.equity_curve = []
        self.logs = []

        # set up endpoint & stream
        self.endpoint = self.data_endpoint_cls(self.symbols, '730d','60m')
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
                price=bar["close"].iloc[0],
                size=bar["volume"],
                timestamp=ts,
            )

        return ts, bars

    def run(self):
        SHARES = 100

        while True:
            tick = self.load_next_tick()
            if tick is None:
                break

            ts, bars = tick
            ticker = self.strategy.symbol
            signal = self.strategy.compute_signal()

            

            price = bars[ticker]["close"]
            
            trade_value = SHARES * price.values[0]
            if signal is None:
                print('Strategy is inside Threshold so no signal')
                continue
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

            print(self.positions)
            portfolio_value = self.cash + sum(self.positions[s] * bars[s]["close"] for s in self.symbols)
            self.equity_curve.append((ts, portfolio_value.values[0]))


def plot_equity_curve(dates, equity_values, title="Trading System Equity Curve", strategy_name="Strategy"):

    fig, ax = plt.subplots(figsize=(12, 6)) # Larger figure size for better detail

   
    ax.plot(
        dates, 
        equity_values, 
        label=strategy_name, 
        color='mediumblue', # A nice, professional blue
        linewidth=2,
        alpha=0.8 # Slight transparency
    )

    # 3. Add Labels and Title
    ax.set_title(title, fontsize=16, fontweight='bold', color='darkslategray')
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Equity Value ($)", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    fig.autofmt_xdate(rotation=45)     
    ax.legend(loc='best', fontsize=10)    
    plt.tight_layout()
    
    # 9. Show the plot
    plt.show()

if __name__ == "__main__":
    

    # ---------------------------------------------------------
    # USER CONFIG
    # ---------------------------------------------------------
    SYMBOLS = ["AAPL","NVDA"] #ISSUES WHEN PASSING TWO SYMBOLS 
    STRATEGY = strat.AutoRegresion(symbol="AAPL")   
    DATA_ENDPOINT = YF_ENDPOINT
    INITIAL_CASH = 80_000

    # ---------------------------------------------------------
    # INIT BACKTEST ENGINE
    # ---------------------------------------------------------
    engine = BACKTESTING_ENGINE(
        symbols=SYMBOLS,
        strategy=STRATEGY,
        data_endpoint=DATA_ENDPOINT,
        initial_cash=INITIAL_CASH,
    )

    print("Starting backtest...")
    engine.run()
    print("Backtest complete.")

    # ---------------------------------------------------------
    # OPTIONAL: DISPLAY RESULTS
    # ---------------------------------------------------------
    print("\n=== FINAL RESULTS ===")
    print(f"Final cash: {engine.cash:,.2f}")
    print("Final positions:")
    for sym, qty in engine.positions.items():
        print(f"  {sym}: {qty} shares")

    if engine.equity_curve:
        final_ts, final_val = engine.equity_curve[-1]
        eqty = [i[1] for i in engine.equity_curve]
        dates = [i[0] for i in engine.equity_curve]
        print(f"Final portfolio value at {final_ts}: {final_val:,.2f}")
        print(len(eqty))
        plot_equity_curve(dates,eqty)
    else:
        print("No equity curve data recorded.")
