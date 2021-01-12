from collections import namedtuple

TradeTuple = namedtuple('Trade', ['action', 'new_balance', 'price', 'quantity', 'date', 'string'])


class Trader:

    def __init__(self, balance, ccy,  name='harvir', btc=0, fees=0.0015):
        self.name = name
        self.balance = balance
        self.btc = btc
        self.ccy = ccy
        self.fees = fees

    def long(self, price, date, quantity=0, max=False):
        quantity = self.balance / price if max else quantity
        future_balance = self.balance - ((price*quantity) - (price*quantity)*self.fees)

        if future_balance < 0:
            raise Exception('Future balance is 0. Something has gone wrong')

        if future_balance >= 0:
            self.balance = future_balance
            self.btc += quantity

        return TradeTuple('buy', self.balance, price, quantity, date,
                          'Bought {}{} at {} on {}'.format(quantity, self.ccy, price, date))

    def close_long(self, price, date, quantity=0, max=False):
        quantity = self.btc if max else quantity
        self.balance += ((price*quantity) - (price*quantity)*self.fees)
        self.btc -= quantity

        return TradeTuple('sell', self.balance, price, quantity, date,
                          'Sold {}{} at {} on {}'.format(quantity, self.ccy, price, date))

    def short(self, price, date, quantity=0, max=False):
        quantity = self.balance / price if max else quantity
        return NotImplementedError

    def close_short(self, price, date, quantity=0, max=False):
        quantity = self.btc if max else quantity
        return NotImplementedError
