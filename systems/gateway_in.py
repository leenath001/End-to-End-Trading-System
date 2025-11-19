## Functions to access yfinance, alphavantage (AV), and alpaca API endpoints for equities

# yf imports
import yfinance as yf

# AV imports 
from dotenv import load_dotenv
from time import time
from datetime import datetime
import threading
import pandas as pd

# alpaca imports 
import alpaca_trade_api as tradeapi

#-----------------------------------------------------------------------------------#
# Use YF_ENDPOINT to grab historical data for backtests. See parameter specs below.
#
# Use ALPACA_ENDPOINT for 15m delayed quotes and to send orders. 
#-----------------------------------------------------------------------------------#

# yf data function (STRICTLY FOR BACKTESTS)
class YF_ENDPOINT:
    _instance = None

    def __new__(cls, symbols, period, interval):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self,symbols: list, period: str, interval: str):
        """
        Parameters for period & interval:
            "1m" Max 7 days, only for recent data
            "2m" Max 60 days 
            "5m" Max 60 days
            "15m" Max 60 days
            "30m" Max 60 days 
            "60m" Max 730 days (~2 years)
            "90m" Max 60 days
            "1d" No Max
        """
        self.symbols = symbols
        self.period = period
        self.interval = interval
        self.errors = []
        self.handlers = []
        self.data_dict = {}

    def register_handler(self,func):
        """
        Registers handler functions for our data. Ideally for backtest 
        """
        self.handlers.append(func)

    def _fetch_single(self,ticker: str):
        """
        Grabs YF data for one ticker
        """    
        try:
            data = yf.download(ticker, period= self.period, interval= self.interval)
            self.data_dict[ticker] = data
        except Exception as e:
            self.errors.append(f"Error @ {datetime.now()}: {e}")
            print(f"Datastream Error @ {datetime.now()}: {e}")
        
    def data_grabber(self):
        """
        Downloads all ticker data using multithreading
        """
        threads = []

        for ticker in self.symbols:
            t = threading.Thread(target = self._fetch_single, args = (ticker,))
            t.daemon = True
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

    def get_timestamps(self):
        """
        Returns master timestamp index
        """
        sample = self.symbols[0]
        return self.data_dict[sample].index
    
    def stream(self):
        """
        Uses lazy execution for vectorized backtesting
        Returns (timestamp, quotes for all symbols)
        Price size timestamp
        """
        timestamps = self.get_timestamps()

        for ts in timestamps:
            bars = {}
            for sym in self.symbols:
                row = self.data_dict[sym].loc[ts]
                bars[sym] = {
                    "close": row["Close"],
                    "volume": row["Volume"],
                    "timestamp": ts
                }

            yield ts, bars

# Alpaca API endpoint for 15m delayed quotes
class ALPACA_ENDPOINT:
    _instance = None

    def __new__(cls, key, secret, symbols):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self,key,secret,symbols: list):
        self.api = tradeapi.REST(
            key, 
            secret, 
            base_url= "https://data.alpaca.markets"
        )
        self.symbols = symbols
        self.data_dict = {}
        self.errors = []
        self.handlers = []

    def register_handler(self,func):
        """
        Registers handler functions for our data
        """
        self.handlers.append(func)

    def _fetch_single(self, symbol):
        """
        Fetches delayed latest quote
        """
        try:
            quote = self.api.get_latest_quote(symbol,feed = "delayed_sip")
            self.data_dict[symbol] = {
                "ask": quote.ask_price,
                "ask_size": quote.ask_size,
                "bid": quote.bid_price,
                "bid_size": quote.bid_size,
                "timestamp": quote.timestamp
                }
            
            for h in self.handlers:
                h(symbol, self.data_dict[symbol])

        except Exception as e:
            self.errors.append(f"Datastream Error @ {datetime.now()}: {e}")
            print(f"Datastream Error @ {datetime.now()}: {e}")
        
    def grab_quotes(self):
        """
        Launches quote grabbing threads
        """
        threads = []

        for symbol in self.symbols:
            t = threading.Thread(target=self._fetch_single, args=(symbol,))
            t.daemon = True
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
            