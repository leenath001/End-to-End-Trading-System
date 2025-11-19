from systems.gateway_in import YF_ENDPOINT
import pandas as pd

## options
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

symbols = ['NVDA', "AAPL"]

endpoint = YF_ENDPOINT(symbols, "7d", "1m")
endpoint.data_grabber()
data = endpoint.data_dict['NVDA']

for _ in range(len(data)):
    print(endpoint.stream())

