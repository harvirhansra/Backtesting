class Trader:

    def __init__(self, balance, ccy, name='harvir', btc=0):
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
            # print('Not enough dollars')
            return False
        if future_balance >= 0:
            self.balance = future_balance
            self.btc += quantity
        if quantity > 0:
            pass
            # print('Bought {}{} at {} on {}'.format(quantity, self.ccy, price, date))
        return self.balance, price, quantity

    def sell(self, price, date, quantity=0, max=False):
        if quantity > self.btc:
            # print('Not enough BTC')
            return False
        quantity = self.btc if max else quantity

        self.balance += price*quantity
        self.btc -= quantity
        if quantity > 0:
            pass
            # print('Sold {}{} at {} on {}'.format(quantity, self.ccy, price, date))
        return self.balance, price, quantity
