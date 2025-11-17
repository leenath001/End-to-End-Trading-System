# builds orders using Alpaca and IBKR, checks risk-limits 

# alpaca imports
import alpaca_trade_api as tradeapi

# IBKR imports
#from IBKR_engine import IBKRExecutionEngine

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

class IBKR_ORDER_MANAGER:
    """
    Tracks exposures, calls IBKR to execute orders
    """