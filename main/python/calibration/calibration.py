import threading
import numpy as np

from trade.simple_strats import above_under_ma_std


def calibrate_std(df):
    stds = list(np.arange(0, 4, 1))
    results = {}

    for std in stds:
        results[std] = above_under_ma_std(df, std)

    pnls = list(results.values())
    best_std = stds[pnls.index(max(pnls))]
    print('best_std is {} which returned {}%'.format(best_std, results[best_std]))
    return best_std
