import requests
import polygon
import pandas as pd
import datetime
import logins
import matplotlib.pyplot as plt
import mplfinance as mpf
import requests
import json
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
api_key = logins.api_key
polygon_client = polygon.RESTClient(api_key)


def get_options_tickers():
    endpoint = "https://api.polygon.io/v3/reference/options/contracts"
    params = {  
        'underlying_ticker' : 'AAPL',
        'expired': 'false',
        'sort': 'strike_price',
        "apiKey": api_key
    }
    try:
        response = requests.get(endpoint, params=params)
        data = response.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        logging.error(f'An error occurred: {e}')
        return None

    if data['status'] == 'OK':
        logging.info('Request was successful')
        results = data['results']
        data = pd.DataFrame(results)
        return data['ticker']
    else:
        logging.error('Request failed')
        return None

def get_historical_prices(ticker):
    end_date = datetime.date.today() - datetime.timedelta(days=1)
    start_date = end_date - datetime.timedelta(days=2*365)
    endpoint = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}'
    params = {  
        'adjusted': 'true',
        "apiKey": api_key
    }
    try:
        response = requests.get(endpoint, params=params)
        data = response.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        logging.error(f'An error occurred: {e}')
        return None

    if data['status'] == 'OK':
        logging.info('Request was successful')
        df = pd.DataFrame(data['results'])
        df = df.rename(columns={
            'c': 'Close',
            'h': 'High',
            'l': 'Low',
            'n': 'Number of Transactions',
            'o': 'Open',
            't': 'Timestamp',
            'v': 'Volume',
            'vw': 'Volume Weighted Average Price'
        })
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        return df
    else:
        logging.error('Request failed')
        return None

def plot_candlestick_chart(df):
    df.index = pd.to_datetime(df['Timestamp'])
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

    mpf.plot(df, type='candle', style='charles',
             title='Option Candlestick Chart',
             ylabel='Price',
             volume=True)
    plt.show()

def plot_vwap_change(df):
    plt.figure(figsize=(14, 7))
    plt.plot(df['Timestamp'], df['Option VWAP Change'], label='Option VWAP Change')
    plt.plot(df['Timestamp'], df['Stock VWAP Change'], label='Stock VWAP Change')
    plt.title('VWAP Change')
    plt.xlabel('Date')
    plt.ylabel('VWAP Change')
    plt.legend()
    plt.grid(True)  
    plt.show()

def plot_vwap(df):
    plt.figure(figsize=(14, 7))
    plt.plot(df['Timestamp'], df['Volume Weighted Average Price_Option'], label='Option VWAP')
    plt.plot(df['Timestamp'], df['Volume Weighted Average Price_Stock'], label='Stock VWAP')
    plt.title('VWAP')
    plt.xlabel('Date')
    plt.ylabel('VWAP')
    plt.legend()
    plt.grid(True)  
    plt.show()

def plot_option_vwap(df):
    try:
        plt.figure(figsize=(14, 7))
        plt.plot(df['Timestamp'], df['Volume Weighted Average Price'], label='Option VWAP', marker='o')
        plt.grid(True)
        max_price = df['Volume Weighted Average Price'].max()
        min_price = df['Volume Weighted Average Price'].min()
        max_date = df['Timestamp'][df['Volume Weighted Average Price'].idxmax()]
        min_date = df['Timestamp'][df['Volume Weighted Average Price'].idxmin()]
        plt.annotate(f'Max: {max_price}', xy=(max_date, max_price), xytext=(max_date, max_price+5),
                     arrowprops=dict(facecolor='red', shrink=0.05))
        plt.annotate(f'Min: {min_price}', xy=(min_date, min_price), xytext=(min_date, min_price+5),
                     arrowprops=dict(facecolor='blue', shrink=0.05))
        plt.title('Option VWAP Over Time with Max and Min Prices')
        plt.xlabel('Date')
        plt.ylabel('VWAP')
        plt.legend()
        plt.show()
    except Exception as e:
        logging.error(f'An error occurred: {e}')

def main():
    try:
        ticker_option = 'O:NVDA240301P00735000'
        df_option = get_historical_prices(ticker_option)
        if df_option is None:
            raise Exception('Failed to get historical prices for option')
        df_option['Option VWAP Change'] = df_option['Volume Weighted Average Price'].pct_change()

        ticker_stock = 'NVDA'
        df_stock = get_historical_prices(ticker_stock)
        if df_stock is None:
            raise Exception('Failed to get historical prices for stock')
        df_stock['Stock VWAP Change'] = df_stock['Volume Weighted Average Price'].pct_change()

        df_merged = pd.merge(df_option[['Timestamp', 'Option VWAP Change', 'Volume Weighted Average Price']], df_stock[['Timestamp', 'Stock VWAP Change', 'Volume Weighted Average Price']], on='Timestamp', suffixes=('_Option', '_Stock'))

        plot_vwap_change(df_merged)
        plot_vwap(df_merged)
        plot_option_vwap(df_option)
        plot_candlestick_chart(df_option)
    except Exception as e:
        logging.error(f'An error occurred: {e}')

if __name__ == "__main__":
    main()

