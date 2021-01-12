import numpy as np

from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor, as_completed
from trade.simple_strats import above_under_ma_std

calib_result = namedtuple('calib_result', ['best_std', 'best_pnl'])


def calibrate_std(df, prev_trade, multi=False):
    results = {}
    stds = list(np.arange(0, 3.25, 0.25))
    slice = df.copy().reset_index(drop=True)

    if multi:
        with ProcessPoolExecutor(2) as ex:
            ps = {ex.submit(above_under_ma_std, slice, std, lookback=14, log=False, draw=False, calib=True, prev_trade=prev_trade): std for std in stds}
            for p in as_completed(ps):
                try:
                    k, v = ps.result()
                except Exception:
                    pass
                    # print(f"{futures[]} throws {e}")
                else:
                    results[k] += v
    else:
        for std in stds:
            results[std] = above_under_ma_std(slice, std, lookback=14, log=False, draw=False, calib=True, prev_trade=prev_trade)

    date = str(slice.iloc[-1].Date).split()[0]

    pnls = [result[0] for result in results.values()]
    ntrds = [result[1] for result in results.values()]
    stds = [result[2] for result in results.values()]
    
    best_pnl = max(pnls)
    best_index = pnls.index(best_pnl)
    best_ntrds = ntrds[best_index]
    best_std = stds[best_index]

    print('best std value for {} is {} which returned {}%'.format(date, best_std, best_pnl))

    return calib_result(best_std, best_pnl)


def _store_in_dict(dict, key, func, *args):
    dict[key] = func(*args)