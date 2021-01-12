import os
from datetime import datetime
from backtesting.market.marketdata import get_historical_from_coinbase


def test_get_historical_from_coinbase():
    interval = '1hr'
    ticker = 'BTC'
    start = datetime(2018, 1, 1, 00, 00)
    end = datetime(2021, 1, 10, 00, 00)

    start_str = start.strftime('%Y%m%d')
    end_str = end.strftime('%Y%m%d')

    res = get_historical_from_coinbase(f'{ticker}-GBP', start, end, interval)
    res.to_csv(os.path.join(os.environ['ROOTDIR'],
                            f'resources/COINBASE-{ticker}GBP-{start_str}-{end_str}-{interval}.csv'),
               index=False)
    return True
