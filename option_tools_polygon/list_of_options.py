import time
from polygon import RESTClient
import pandas as pd 
from logins import api_key

polygon = RESTClient(api_key)

response = polygon.list_tickers(ticker='AAPL')
#read the Generator
for i in response:
    print(i)

import pandas as pd

# Assuming 'response' is a list of dictionaries
df = pd.DataFrame(response)
print(df)