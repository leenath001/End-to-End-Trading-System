import time
from datetime import datetime
from dotenv import load_dotenv
import os 
from systems.equity import Equity
from systems.strategy import MeanReversion
from systems.gateway_in import ALPACA_ENDPOINT
from systems.order_manager import OrderManager

# CONFIGURATION
load_dotenv()
KEY = os.getenv('ALPACA_API_KEY')
SECRET = os.getenv('ALPACA_SECRET')
SYMBOLS = ["AAPL", "NVDA", "MSFT"]
LOOP_DELAY = 25   
TRADE_QTY = 75    

# CREATE OBJECTS
alpaca_feed = ALPACA_ENDPOINT(KEY, SECRET, SYMBOLS)
strategies = {sym: MeanReversion(sym, window=10, z_thresh=1.3) for sym in SYMBOLS}
order_manager = OrderManager(KEY, SECRET)

# HANDLER FUNC: UPDATE EQUITY CLASS WITH QUOTES
def update_equity_handler(symbol, q):
    """
    Incoming quote from Alpaca, store in Equity singleton
    """
    e = Equity(symbol)
    e.update_quote(
        bp=q["bid"],
        bsz=q["bid_size"],
        ap=q["ask"],
        asksz=q["ask_size"])
    mid_price = (q["bid"] + q["ask"]) / 2
    e.update_trade(price=mid_price, size=1, timestamp=q["timestamp"])

alpaca_feed.register_handler(update_equity_handler)

# MAIN TRADING LOOP
def main():
    print("Live Trading System Started.")

    while True:
        try:
            alpaca_feed.grab_quotes()

            for sym in SYMBOLS:
                strat = strategies[sym]
                signal = strat.compute_signal()

                if signal is None:
                    continue

                print(f"[{sym}] SIGNAL: {signal}")

                order_manager.place_order(sym, signal, TRADE_QTY)

            time.sleep(LOOP_DELAY)

        except KeyboardInterrupt:
            print("Keyboard Interrupt — stopping system.")
            break

        except Exception as e:
            print(f"System Error @ {datetime.now()}: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()