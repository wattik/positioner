from dataclasses import dataclass
from enum import Enum

import pandas as pd


class Side(Enum):
    BID = "BID"
    ASK = "ASK"

    def __repr__(self):
        return self.value


class OptionType(Enum):
    CALL = "C"
    PUT = "P"

    def __repr__(self):
        return self.value


@dataclass
class Symbol:
    symbol: str

    @property
    def asset(self):
        return self.symbol.split("-")[0]

    @property
    def expiry(self):
        return self.symbol.split("-")[1]

    @property
    def strike_price(self):
        return int(self.symbol.split("-")[2])

    @property
    def option_type(self):
        return OptionType(self.symbol.split("-")[3])

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.symbol == other.symbol

    def __hash__(self):
        return hash(self.symbol)

    def __repr__(self):
        return self.symbol

@dataclass
class Option:
    price: float
    quantity: float
    side: Side
    symbol: Symbol

    @property
    def asset(self): return self.symbol.asset

    @property
    def expiry(self): return self.symbol.expiry

    @property
    def strike_price(self): return self.symbol.strike_price

    @property
    def option_type(self): return self.symbol.option_type

    def __eq__(self, other):
        return (
                isinstance(other, Option) and
                other.price == self.price and
                other.quantity == self.quantity and
                other.side == self.side and
                other.symbol == self.symbol
        )

    def __hash__(self):
        return hash((self.symbol, self.price, self.quantity, self.side))

    def __repr__(self):
        return f"{self.symbol}-{self.side}"

    @classmethod
    def make(cls, price, quantity, side, symbol):
        return cls(
            float(price),
            float(quantity),
            Side(side),
            Symbol(symbol)
        )

def read_order_book_from_csv(filename):
    df = pd.read_csv(filename)

    order_book = []
    for i, row in df.iterrows():
        order_book += [Option.make(row.price, row.qnty, row.side, row.symbol)]

    return order_book


def read_order_book_from_dict(data):
    order_book = []
    for option in data:
        order_book += [Option.make(option["price"], option["qnty"], option["side"], option["symbol"])]

    return order_book
