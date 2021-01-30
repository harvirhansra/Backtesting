from backtesting.analytics.pnl import win_or_loss


def test_win_or_loss_long_gain():
    wl = win_or_loss(100, 120, 10, 'close long')
    assert wl.winloss == 'win'
    assert wl.pnl == 200
    assert wl.pnlpct == 20
    assert wl.colour == 'green'


def test_win_or_loss_long_loss():
    wl = win_or_loss(100, 80, 10, 'close long')
    assert wl.winloss == 'loss'
    assert wl.pnl == -200
    assert wl.pnlpct == -20
    assert wl.colour == 'red'


def test_win_or_loss_short_gain():
    wl = win_or_loss(100, 80, 10, 'close short')
    assert wl.winloss == 'win'
    assert wl.pnl == 200
    assert wl.pnlpct == 20
    assert wl.colour == 'green'


def test_win_or_loss_short_loss():
    wl = win_or_loss(100, 120, 10, 'close short')
    assert wl.winloss == 'loss'
    assert wl.pnl == -200
    assert wl.pnlpct == -20
    assert wl.colour == 'red'
