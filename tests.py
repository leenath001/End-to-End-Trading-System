from systems.gateway_in import YF_ENDPOINT

x = ["AAPL", "NVDA"]

y = YF_ENDPOINT(x,'60d', '2m')
y.data_grabber()
print(y.data_dict)