from collections import namedtuple

wl_tuple = namedtuple('WinOrLoss', ['winloss', 'pnl', 'pnlpct', 'colour'])  # all strings

def win_or_loss(s0, s1, quantity, buy_or_sell):
    diff = abs(s0-s1)
    percent = (diff/s0)*100
    pnl = quantity*diff

    if buy_or_sell == 1:
        if quantity > 0:
            if s1 > s0:
                return wl_tuple('loss', str(-round(pnl, 3)), round(percent, 3), 'red')
            else:
                return wl_tuple('win', str(round(pnl, 3)), round(percent, 3), 'green')
        else:
            return

    if buy_or_sell == -1:
        if quantity > 0:
            if s0 > s1:
                return wl_tuple('loss', str(-round(pnl, 3)), -round(percent, 3), 'red')
            else:
                return wl_tuple('win', str(round(pnl, 3)), round(percent, 3), 'green')
        else:
            return


def report_final_pnl(start_balance, start_btc, balance, btc, ccy, log=True):
    final_is_usd = balance > 0
    final = balance if final_is_usd else btc
    start = start_balance if final_is_usd else start_btc
    final_ccy = '$' if final_is_usd else ccy
    pnl = int((final/start)*100 - 100)
    if log:
        print('')
        print('Starting balance: {}{}'.format(final_ccy, start))
        print('Final balance: {}{}'.format(final_ccy, round(final, 2)))
        print('PnL: '+str(pnl)+'%')
        print('')
    return pnl

