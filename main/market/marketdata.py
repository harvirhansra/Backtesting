import pandas as pd
import requests


def get_data_from_csv(file_location):
    rename_mapping = {'24h High (USD)': 'High', '24h Low (USD)': 'Low',
                      '24h Open (USD)': 'Open', 'Closing Price (USD)': 'Close'}

    df = pd.read_csv(file_location)
    df = _fix_dates(df)
    df = df.rename(columns=rename_mapping)

    df['High'].astype(float)
    df['Low'].astype(float)
    df['Date'] = pd.to_datetime(df['Date'])

    return df


# TODO: Fix url and use parameters in query
def get_data_from_yahoo(start, end):
    save_to = 'resources/data.csv'
    url = 'https://query1.finance.yahoo.com/v7/finance/download/BTC-USD?period1=1531496320&period2=1563032320&interval=1d&events=history&crumb=4/1RJ140bst'
    data_file = requests.get(url)
    open(save_to, 'wb').write(data_file.content)


def _fix_dates(df):
    """
    Removes time from date fields so date is in the yyyy-mm-dd
    format for market data from CoinDesk
    """
    df['Date'] = df['Date'].apply(lambda x: x[0:10])
    return df
