from collections import namedtuple

buytuple = namedtuple('BuyTuple', ['new_balance', 'buy_price', 'quantity', 'string'])
selltuple = namedtuple('SellTuple', ['new_balance', 'sell_price', 'quantity', 'string'])

class Trader:

    def __init__(self, balance, ccy,  name='harvir', btc=0):
        self.name = name
        self.balance = balance
        self.btc = btc
        self.ccy = ccy

    def buy(self, price, date, quantity=0, max=False):
        if max:
            quantity = self.balance / price
            future_balance = 0
        else:
            future_balance = self.balance - (price*quantity)

        if future_balance < 0:
            return False

        if future_balance >= 0:
            self.balance = future_balance
            self.btc += quantity

        return buytuple(self.balance, price, quantity, 'Bought {}{} at {} on {}'.format(quantity, self.ccy, price, date))

    def sell(self, price, date, quantity=0, max=False):
        if quantity > self.btc:
            return False

        quantity = self.btc if max else quantity
        self.balance += price*quantity
        self.btc -= quantity

        return selltuple(self.balance, price, quantity, 'Sold {}{} at {} on {}'.format(quantity, self.ccy, price, date))
