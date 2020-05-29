import pandas as pd
import requests


def get_data_from_csv(file_location):
    df = pd.read_csv(file_location)
    # df = df.rename(columns=rename_mapping)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Open'] = df['Open'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df['Date'] = pd.to_datetime(df['Date'])

    return df
