class Trader:

    def __init__(self, balance, ccy,  name='harvir', btc=0, log=False):
        self.name = name
        self.balance = balance
        self.btc = btc
        self.ccy = ccy
        self.log = log

    def buy(self, price, date, quantity=0, max=False):
        if max:
            quantity = self.balance / price
            future_balance = 0
        else:
            future_balance = self.balance - (price*quantity)

        if future_balance < 0:
            if self.log:
                print('Not enough dollars')
            return False

        if future_balance >= 0:
            self.balance = future_balance
            self.btc += quantity

        return self.balance, price, quantity, 'Bought {}{} at {} on {}'.format(quantity, self.ccy, price, date)

    def sell(self, price, date, quantity=0, max=False):
        if quantity > self.btc:
            if self.log:
                print('Not enough BTC')
            return False

        quantity = self.btc if max else quantity
        self.balance += price*quantity
        self.btc -= quantity

        return self.balance, price, quantity, 'Sold {}{} at {} on {}'.format(quantity, self.ccy, price, date)
