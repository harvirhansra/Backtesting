import os
import requests
import pandas as pd

from datetime import timedelta
from backtesting.market.coinbase import CoinbaseExchangeAuth


def get_data_from_csv(file_location):
    df = pd.read_csv(file_location)
    for col in ['Low', 'High', 'Open', 'Close', 'Volume']:
        df[col] = df[col].astype(float)

    df['Time'] = pd.to_datetime(df['Time'])
    df = df.set_index('Time')
    df.drop_duplicates(inplace=True)
    return df


def get_historical_from_coinbase(ticker, start_date, end_date, interval='1hr'):
    API_KEY = ''
    API_SECRET = ''
    API_PASS = ''
    api_url = 'https://api.pro.coinbase.com/'

    auth = CoinbaseExchangeAuth(API_KEY, API_SECRET, API_PASS)

    if interval == '1hr':
        granularity = 3600
    elif interval == '15mins':
        granularity = 900

    columns = ['Time', 'Low', 'High', 'Open', 'Close', 'Volume']
    big_df = pd.DataFrame(columns=columns)

    dates = [dt for dt in daterange(start_date, end_date, interval)]
    # breakpoint()
    for i in range(len(dates)):
        if i == len(dates)-1:
            break
        r = requests.get(api_url + f'products/{ticker}/candles', auth=auth,
                         params={'granularity': granularity,
                                 'start': dates[i].isoformat(),
                                 'end': dates[i+1].isoformat()})
        df = pd.DataFrame.from_records(r.json(), columns=columns)[::-1]
        big_df = big_df.append(df)

    big_df.Time = pd.to_datetime(big_df.Time, unit='s')
    return big_df


def daterange(start_date, end_date, interval):
    if interval == '1hr':
        delta = timedelta(hours=300)
    elif interval == '15mins':
        delta = timedelta(hours=75)

    while start_date < end_date:
        yield start_date
        start_date += delta
    yield end_date
