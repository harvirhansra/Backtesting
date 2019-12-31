def win_or_loss(s0, s1, quantity):
    diff = abs(s0-s1)
    percent = (diff/s0)*100
    pnl = quantity*diff
    if quantity > 0:
        if s0 > s1:
            return 'loss', pnl, -percent
        else:
            return 'win', pnl, percent
    else:
        return 'did nothing'
