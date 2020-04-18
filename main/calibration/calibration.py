import numpy as np

from threading import Thread
from trade.simple_strats import above_under_ma_std


def calibrate_std(df, threaded=False, test=0):
    results = {}
    stds = list(np.arange(0, 3, 0.25))
    """ if test == 102:
        import pdb
        pdb.set_trace() """
    df = df.copy().reset_index(drop=True)
        

    if threaded:
        threads = []
        for std in stds:
            thread = Thread(target=_store_in_dict, args=(results, std, above_under_ma_std, df, std, 14, False))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
    else:
        for std in stds:
            results[std] = above_under_ma_std(df, std, lookback=14, log=False, draw=False, calib=True)

    date = str(df.iloc[-1].Date).split()[0]
    pnls = list(results.values())
    best_std = stds[pnls.index(max(pnls))]
    print('best std value for {} is {} which returned {}%'.format(date, best_std, results[best_std]))
    return best_std


def _store_in_dict(dict, key, func, *args):
    dict[key] = func(*args)
