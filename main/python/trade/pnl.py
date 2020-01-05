def win_or_loss(s0, s1, quantity, buy_or_sell):
    diff = abs(s0-s1)
    percent = (diff/s0)*100
    pnl = quantity*diff
    if buy_or_sell == 'buy':
        if quantity > 0:
            if s1 > s0:
                return 'loss', -round(pnl, 3), -round(percent, 3)
            else:
                return 'win', round(pnl, 3), round(percent, 3)
        else:
            return ''
    if buy_or_sell == 'sell':
        if quantity > 0:
            if s0 > s1:
                return 'loss', -round(pnl, 3), -round(percent, 3)
            else:
                return 'win', round(pnl, 3), round(percent, 3)
        else:
            return ''
