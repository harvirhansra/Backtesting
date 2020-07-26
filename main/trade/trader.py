from collections import namedtuple

TradeTuple = namedtuple('Trade', ['action', 'new_balance', 'price', 'quantity', 'date', 'string'])


class Trader:

    def __init__(self, balance, ccy,  name='harvir', btc=0, fees=0.001):
        self.name = name
        self.balance = balance
        self.btc = btc
        self.ccy = ccy
        self.fees = fees

    def buy(self, price, date, quantity=0, max=False):
        if max:
            quantity = self.balance / price
            future_balance = 0
        else:
            future_balance = self.balance - ((price*quantity) - (price*quantity)*self.fees)

        if future_balance < 0:
            return False

        if future_balance >= 0:
            self.balance = future_balance
            self.btc += quantity

        return TradeTuple('buy', self.balance, price, quantity, date, 'Bought {}{} at {} on {}'.format(quantity, self.ccy, price, date))

    def sell(self, price, date, quantity=0, max=False):
        if quantity > self.btc:
            return False

        quantity = self.btc if max else quantity
        self.balance += ((price*quantity) - (price*quantity)*0.001)
        self.btc -= quantity

        return TradeTuple('sell', self.balance, price, quantity, date, 'Sold {}{} at {} on {}'.format(quantity, self.ccy, price, date))
