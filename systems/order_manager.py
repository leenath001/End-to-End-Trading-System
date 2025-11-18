# builds orders using Alpaca and IBKR, checks risk-limits 

# alpaca imports
import alpaca_trade_api as tradeapi
from time import time

class ALPACA_ORDER_MANAGER:
    """
    Tracks exposures, calls alpaca to execute orders based on conditions
    """

    def __init__(self, key, secret, paper = True):
        self.base = "https://paper-api.alpaca.markets"
        self.api = tradeapi.REST(key,secret,self.base)

    def get_positions(self):
        """
        List of (symbol, qty) tuples
        """
        pos = self.api.list_positions()
        out = []
        for p in pos:
            try:
                qty = float(p.qty)
            except:
                qty = int(qty)
            out.append((p.symbol, qty))
        return out

    def send_order(self, symbol, side, qty, order_type="market", tif="day"):
        """
        Places market order
        side: "buy" or "sell"
        """
        return self.api.submit_order(
            symbol=symbol,
            side=side.lower(),       
            qty=qty,
            type=order_type,
            time_in_force=tif,
        )

class OrderManager:
    """
    Keeps track of exposures, executes orders via Alpaca.
    Behaves like IBKR-order manager.
    """

    def __init__(self, key, secret, gateway=None):
        self.gateway = ALPACA_ORDER_MANAGER(key, secret)
        self.local_positions = {}
        self.last_trade_time = {}

    def sync_positions(self):
        """
        Sync positions to local storage from Alpaca API
        """
        positions = self.gateway.get_positions()  
        self.local_positions = {sym: qty for sym, qty in positions}

    def get_position(self, symbol):
        return self.local_positions.get(symbol, 0)

    def place_order(self, symbol, action, qty):
        """
        action: "BUY" or "SELL" (upper-case)
        qty: the intended trade size
        """
        self.sync_positions()
        current_pos = self.get_position(symbol)

        now = time.time()

        if action == "BUY":
            if current_pos <= 0:
                order_qty = abs(current_pos) + qty
                print(f"BUY {order_qty} {symbol}")
                self.gateway.send_order(symbol, "buy", order_qty)
                self.last_trade_time[symbol] = now
            else:
                print("Already long!")

        elif action == "SELL":
            if current_pos >= 0:
                order_qty = abs(current_pos) + qty
                print(f"SELL {order_qty} {symbol}")
                self.gateway.send_order(symbol, "sell", order_qty)
                self.last_trade_time[symbol] = now
            else:
                print("Already short!")