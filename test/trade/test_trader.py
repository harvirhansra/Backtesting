import pytest
import pandas as pd

from backtesting.trade.trader import Trader


@pytest.fixture()
def trader():
    return Trader(1000, 'BTC', 'harvir', 0, 0)


def test_long_max(trader):
    trade = trader.long(100, pd.Timestamp('2020-01-01 00:00:00'), max=True)
    assert trade.type == 'long'
    assert trade.new_balance == 0
    assert trade.price == 100
    assert trade.quantity == 10
    assert trade.date == pd.Timestamp('2020-01-01 00:00:00')


@pytest.mark.skip(reason='TODO')
def test_long_max_with_fees(trader):
    trader.fees = 1  # 1%
    trade = trader.long(100, pd.Timestamp('2020-01-01 00:00:00'), max=True)
    assert trade.type == 'long'
    assert trade.new_balance == 0
    assert trade.price == 100
    assert trade.quantity == 10
    assert trade.date == pd.Timestamp('2020-01-01 00:00:00')


def test_long_too_much(trader):
    try:
        trader.long(100, pd.Timestamp('2020-01-01 00:00:00'), 1000)
    except Exception as e:
        assert 'Future balance is -99000' in str(e)


def test_long_quantity(trader):
    trade = trader.long(100, pd.Timestamp('2020-01-01 00:00:00'), 5)
    assert trade.type == 'long'
    assert trade.new_balance == 500
    assert trade.price == 100
    assert trade.quantity == 5
    assert trade.date == pd.Timestamp('2020-01-01 00:00:00')


def test_long_and_close_max_win(trader):
    trader.long(100, pd.Timestamp('2020-01-01 00:00:00'), max=True)
    trade = trader.close_long(120, pd.Timestamp('2020-02-01 00:00:00'), max=True)
    assert trade.type == 'close long'
    assert trade.new_balance == 1200
    assert trade.price == 120
    assert trade.quantity == 10
    assert trade.date == pd.Timestamp('2020-02-01 00:00:00')
    assert trader.open_long is None


def test_long_and_close_max_loss(trader):
    trader.long(100, pd.Timestamp('2020-01-01 00:00:00'), max=True)
    trade = trader.close_long(80, pd.Timestamp('2020-02-01 00:00:00'), max=True)
    assert trade.type == 'close long'
    assert trade.new_balance == 800
    assert trade.price == 80
    assert trade.quantity == 10
    assert trade.date == pd.Timestamp('2020-02-01 00:00:00')
    assert trader.open_long is None


def test_long_and_close_most_then_max(trader):
    trader.long(100, pd.Timestamp('2020-01-01 00:00:00'), max=True)
    trade1 = trader.close_long(120, pd.Timestamp('2020-02-01 00:00:00'), quantity=6)
    trade2 = trader.close_long(110, pd.Timestamp('2020-03-01 00:00:00'), max=True)
    assert trade1.type == 'close long'
    assert trade1.new_balance == 720
    assert trade1.price == 120
    assert trade1.quantity == 6
    assert trade1.date == pd.Timestamp('2020-02-01 00:00:00')
    assert trade2.type == 'close long'
    assert trade2.new_balance == 1160
    assert trade2.price == 110
    assert trade2.quantity == 4
    assert trade2.date == pd.Timestamp('2020-03-01 00:00:00')


def test_short_max(trader):
    trade = trader.short(100, pd.Timestamp('2020-01-01 00:00:00'), max=True)
    assert trade.type == 'short'
    assert trade.new_balance == 1500
    assert trade.price == 100
    assert trade.quantity == 5
    assert trade.date == pd.Timestamp('2020-01-01 00:00:00')


def test_short_too_much(trader):
    try:
        trader.short(100, pd.Timestamp('2020-01-01 00:00:00'), quantity=8)
    except Exception as e:
        assert 'Quantity is larger than' in str(e)


def test_short_quantity(trader):
    trade = trader.short(100, pd.Timestamp('2020-01-01 00:00:00'), quantity=3)
    assert trade.type == 'short'
    assert trade.new_balance == 1300
    assert trade.price == 100
    assert trade.quantity == 3
    assert trade.date == pd.Timestamp('2020-01-01 00:00:00')


def test_short_and_close_gain(trader):
    trader.short(100, pd.Timestamp('2020-01-01 00:00:00'), max=True)
    trade = trader.close_short(80, pd.Timestamp('2020-02-01 00:00:00'), max=True)
    assert trade.type == 'close short'
    assert trade.new_balance == 1100
    assert trade.price == 80
    assert trade.quantity == 5
    assert trade.date == pd.Timestamp('2020-02-01 00:00:00')


def test_short_and_close_loss(trader):
    trader.short(100, pd.Timestamp('2020-01-01 00:00:00'), max=True)
    trade = trader.close_short(120, pd.Timestamp('2020-02-01 00:00:00'), max=True)
    assert trade.type == 'close short'
    assert trade.new_balance == 900
    assert trade.price == 120
    assert trade.quantity == 5
    assert trade.date == pd.Timestamp('2020-02-01 00:00:00')


def test_short_and_close_most_then_max(trader):
    trader.short(100, pd.Timestamp('2020-01-01 00:00:00'), max=True)
    trade1 = trader.close_short(90, pd.Timestamp('2020-02-01 00:00:00'), quantity=3)
    trade2 = trader.close_short(80, pd.Timestamp('2020-03-01 00:00:00'), max=True)
    assert trade1.type == 'close short'
    assert trade1.new_balance == 1230
    assert trade1.price == 90
    assert trade1.quantity == 3
    assert trade1.date == pd.Timestamp('2020-02-01 00:00:00')
    assert trade2.type == 'close short'
    assert trade2.new_balance == 1070
    assert trade2.price == 80
    assert trade2.quantity == 2
    assert trade2.date == pd.Timestamp('2020-03-01 00:00:00')
