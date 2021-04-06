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


def symbol_asset(symbol): return symbol.split("-")[0]


def symbol_expiry(symbol): return int(symbol.split("-")[1])


def symbol_strike_price(symbol): return int(symbol.split("-")[2])


def symbol_option_type(symbol): return OptionType(symbol.split("-")[3])


@dataclass
class Option:
    price: float
    quantity: float
    side: Side
    symbol: str

    @property
    def asset(self): return symbol_asset(self.symbol)

    @property
    def expiry(self): return symbol_expiry(self.symbol)

    @property
    def strike_price(self): return symbol_strike_price(self.symbol)

    @property
    def option_type(self): return symbol_option_type(self.symbol)

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


def read_order_book(filename):
    df = pd.read_csv(filename)

    order_book = []
    for i, row in df.iterrows():
        order_book += [Option(float(row.price), float(row.qnty), Side(row.side), row.symbol)]

    return order_book
