import pandas as pd
import requests

class MktData:

    def __init__(self):
        print('Created a MktData object')

    def get_data_from_csv(self, file_location):
        df = pd.read_csv(file_location)
        df = self._fix_dates(df)
        df= df.drop(['Currency'], axis=1) # All currency fields are 'BTC'
        return df

    #TODO: Fix url and use parameters in query
    def get_data_from_yahoo(self, start, end):
        save_to = 'resources/data.csv'
        url = 'https://query1.finance.yahoo.com/v7/finance/download/BTC-USD?period1=1531496320&period2=1563032320&interval=1d&events=history&crumb=4/1RJ140bst'
        data_file = requests.get(url)
        open(save_to, 'wb').write(data_file.content)

    def _fix_dates(self, df):
        """
        Removes time from date fields so date is in the yyyy-mm-dd
        format for market data from CoinDesk
        """
        df['Date'] = df['Date'].apply(lambda x: x[0:10])
        return df