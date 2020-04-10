from collections import namedtuple

wl_tuple = namedtuple('WinOrLoss', ['winloss', 'pnl', 'pnlpct', 'colour'])  # all strings

def win_or_loss(s0, s1, quantity, buy_or_sell):
    diff = abs(s0-s1)
    percent = (diff/s0)*100
    pnl = quantity*diff

    if buy_or_sell == 1:
        if quantity > 0:
            if s1 > s0:
                return wl_tuple('loss', str(-round(pnl, 3)), str(-round(percent, 3))+'%', 'red')
                # return colored(','.join(['loss', str(-round(pnl, 3)), str(-round(percent, 3))+'%']), 'red')
            else:
                return wl_tuple('win', str(round(pnl, 3)), str(round(percent, 3))+'%', 'green')
                # return 
        else:
            return

    if buy_or_sell == -1:
        if quantity > 0:
            if s0 > s1:
                return wl_tuple('loss', str(-round(pnl, 3)), str(-round(percent, 3))+'%', 'red')
                # return colored(','.join(['loss', str(-round(pnl, 3)), str(-round(percent, 3))+'%']), 'red')
            else:
                return wl_tuple('win', str(round(pnl, 3)), str(round(percent, 3))+'%', 'green')
                # return colored(','.join(['win', str(round(pnl, 3)), str(round(percent, 3))+'%']), 'green')
        else:
            return
