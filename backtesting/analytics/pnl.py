from collections import namedtuple

wl_tuple = namedtuple('WinOrLoss', ['winloss', 'pnl', 'pnlpct', 'colour'])


def win_or_loss(s0, s1, quantity, long_short):
    pnl = s1 - s0
    pnl_pct = (pnl / s0) * 100

    if long_short == 'close long':
        if pnl < 0:  # loss
            return wl_tuple('loss', round(pnl*quantity, 3), round(pnl_pct, 3), 'red')
        else:  # gain
            return wl_tuple('win', round(pnl*quantity, 3), round(pnl_pct, 3), 'green')

    elif long_short == 'close short':
        if pnl < 0:
            return wl_tuple('win', -round(pnl*quantity, 3), -round(pnl_pct, 3), 'green')
        else:
            return wl_tuple('loss', -round(pnl*quantity, 3), -round(pnl_pct, 3), 'red')
    else:
        raise Exception(f'Trade type was {long_short}. Must be close long or close short')


def report_final_pnl(start_fiat, start_ccy, balance, ccy, fiat, log=True):
    final_is_fiat = balance > 0
    final = balance if final_is_fiat else ccy
    start = start_fiat if final_is_fiat else start_ccy
    final_ccy = '£' if final_is_fiat else fiat
    pnl = round(((final - start) / start) * 100, 2)
    if log:
        print('')
        print('Starting balance: {}{}'.format(final_ccy, start))
        print('Final balance: {}{}'.format(final_ccy, round(final, 2)))
        print('PnL: '+str(pnl)+'%')
    return pnl


def report_plays_stats(plays):
    longs = [play for play in plays if play.type == 'close long']
    long_wins = len([play for play in longs if play.pnl >= 0])
    long_losses = len([play for play in longs if play.pnl < 0])

    shorts = [play for play in plays if play.type == 'close short']
    short_wins = len([play for play in shorts if play.pnl >= 0])
    short_losses = len([play for play in shorts if play.pnl < 0])

    long_plays = len(longs)
    short_plays = len(shorts)
    total_plays = long_plays + short_plays

    long_wins_pct = round((long_wins / long_plays) * 100, 2) if long_plays > 0 else 0
    long_losses_pct = round((long_losses / long_plays) * 100, 2) if long_plays > 0 else 0
    short_wins_pct = round((short_wins / short_plays) * 100, 2) if short_plays > 0 else 0
    short_losses_pct = round((short_losses / short_plays) * 100, 2) if short_plays > 0 else 0

    print('')
    print(f'Total trades: {total_plays}')
    print(f'Total long trades: {long_plays}')
    print(f'Total short trades: {short_plays}')

    print('')
    print(f'Losing long trades: {long_losses} - {long_losses_pct}%')
    print(f'Winning long trades: {long_wins} - {long_wins_pct}%')

    print('')
    print(f'Losing short trades: {short_losses} - {short_losses_pct}%')
    print(f'Winning short trades: {short_wins} - {short_wins_pct}%')
