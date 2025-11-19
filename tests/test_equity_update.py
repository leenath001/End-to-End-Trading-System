from systems.equity import Equity
from systems.gateway_in import ALPACA_ENDPOINT
from dotenv import load_dotenv
import os
from main import update_equity_handler

load_dotenv()
KEY = os.getenv('ALPACA_API_KEY')
SECRET = os.getenv('ALPACA_SECRET')
SYMBOLS = ["AAPL"]

connection = ALPACA_ENDPOINT(KEY,SECRET,SYMBOLS)
e = Equity(SYMBOLS[0])

connection.register_handler(update_equity_handler)
connection._fetch_single(SYMBOLS[0])


