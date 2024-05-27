import pandas as pd
from polygon import RESTClient
from logins import api_key

polygon = RESTClient(api_key)

def list_tickers():
    # Start with the previous day
    day = pd.Timestamp.today() - pd.Timedelta(days=1)

    while True:
        day_str = day.strftime('%Y-%m-%d')

        # Try to get the market data for the day
        try:
            mktData = pd.DataFrame(polygon.get_grouped_daily_aggs(date=day_str))
            tickerList = list(mktData.ticker)
            return tickerList
        except Exception as e:
            print(f"No data available for {day_str}")

        # If no data was available, move to the previous day
        day -= pd.Timedelta(days=1)

#print(list_tickers())