import subprocess

from mktData.mktData import MktData

def main():
    md = MktData()
    # data = md.get_data_from_yahoo(None, None)
    # df = md.get_data_from_csv(data)
    df = md.get_data_from_csv('resources\BTC_USD_2018-07-14_2019-07-13-CoinDesk.csv')
    print(df)

main()