from collections import namedtuple

TradeTuple = namedtuple('Trade', ['type', 'new_balance', 'price', 'quantity', 'date', 'string'])


class Trader:

    def __init__(self, balance, ccy, name='harvir', btc=0, fees=0.0025):
        self.balance = balance
        self.ccy = ccy
        self.name = name
        self.btc = btc
        self.fees = fees
        self.open_long = None
        self.open_short = None

    def long(self, price, date, quantity=0, max=False):
        quantity = (self.balance / (price + self.fees*price)) if max else quantity
        quantity = round(quantity, 8)  # upto 8dp for BTC

        future_balance = self.balance - (price*quantity) - (price*quantity*self.fees)
        if future_balance < -0.1:
            raise Exception(f'Future balance is {future_balance}. Something has gone wrong')
        else:
            self.balance = round(future_balance, 2)
            self.btc += quantity

        self.open_long = TradeTuple('long', self.balance, price, quantity, date,
                                    f'Long {quantity}{self.ccy} at {price} on {date}')
        return self.open_long

    def close_long(self, price, date, quantity=0, max=False):
        quantity = self.open_long.quantity if max else quantity
        quantity = round(quantity, 8)  # upto 8dp for BTC

        if quantity > self.open_long.quantity:
            raise Exception(f'Current long position is smaller than {quantity}')

        if quantity <= self.open_long.quantity:
            self.open_long = self.open_long._replace(quantity=(self.open_long.quantity - quantity))

        future_btc = self.btc - quantity
        if future_btc < 0:
            raise Exception(f'Future crypto balance is {future_btc}. Something has gone wrong')

        self.balance += round((price*quantity - price*quantity*self.fees), 2)
        self.btc = future_btc

        if self.open_long.quantity == 0:
            self.open_long = None

        return TradeTuple('close long', self.balance, price, quantity, date,
                          f'Closed Long {quantity}{self.ccy} at {price} on {date}')

    def short(self, price, date, quantity=0, max=False):
        quantity = (self.balance / (price + self.fees*price))/2 if max else quantity  # half for now
        if quantity > (self.balance / price) / 2:
            raise Exception('Quantity is larger than 50% equity.')
        quantity = round(quantity, 8)  # upto 8dp for BTC

        self.balance -= price*quantity*self.fees

        self.open_short = TradeTuple('short', self.balance, price, quantity, date,
                                     f'Short {quantity}{self.ccy} at {price} on {date}')
        return self.open_short

    def close_short(self, price, date, quantity=0, max=False):
        quantity = self.open_short.quantity if max else quantity
        if quantity > self.open_short.quantity:
            raise Exception(f'Current short position is smaller than {quantity}')
        quantity = round(quantity, 8)  # upto 8dp for BTC

        future_balance = self.balance + ((self.open_short.price - price) * quantity)
        if future_balance < 0:
            raise Exception(f'Closing short has taken balance to {future_balance}')
        self.balance = round(future_balance, 2)

        if quantity <= self.open_short.quantity:
            self.open_short = self.open_short._replace(quantity=(self.open_short.quantity - quantity))

        if round(self.open_short.quantity, 1) == 0:
            self.open_short = None

        return TradeTuple('close short', self.balance, price, quantity, date,
                          f'Closed Short {quantity}{self.ccy} at {price} on {date}')
