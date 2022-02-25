from dataclasses import dataclass
from enum import Enum
from functools import cached_property, total_ordering
from operator import attrgetter

from positioner.utils.functools import groupby


class Side(Enum):
    BID = "BID"
    ASK = "ASK"

    def __str__(self):
        return self.name


class OptionType(Enum):
    CALL = "C"
    PUT = "P"

    def __str__(self):
        return self.name


@dataclass(order=True)
class Symbol:
    symbol: str

    @cached_property
    def asset(self):
        return self.symbol.split("-")[0]

    @cached_property
    def expiry(self):
        return self.symbol.split("-")[1]

    @cached_property
    def strike_price(self):
        return int(self.symbol.split("-")[2])

    @cached_property
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

    @property
    def amount(self): return self.price * self.quantity

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
        return f"<Option {self.quantity}BTC {self.symbol}-{self.side} at {self.price:1.3f}USD>"

    def __str__(self):
        return f"{self.symbol}-{self.side}"

    @classmethod
    def make(cls, price, quantity, side, symbol):
        return cls(
            float(price),
            float(quantity),
            Side(side),
            Symbol(symbol)
        )


def read_order_book_from_csv(filename) -> list[Option]:
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


def read_options_from_csv(filename):
    df = pd.read_csv(filename)

    options = []
    for i, row in df.iterrows():
        options.append(row.to_dict())

    return options


def group_trading_options_by_expiry_date(trading_options: list[dict]) -> dict:
    grouped = {}
    for opt in trading_options:
        # extract expiration date from option
        expiry_date = Symbol(opt["symbol"]).expiry

        # append to array or create array where key is the expiry_date
        if expiry_date in grouped:
            grouped[expiry_date].append(opt)
        else:
            grouped[expiry_date] = [opt]
    return grouped

class OptionSelector:
    def __init__(self, options: list[Option]):
        self.by_symbol = dict(groupby(attrgetter("symbol"), options, with_keys=True))
        self.by_side = dict(groupby(attrgetter("side"), options, with_keys=True))
        self.by_symbol_side = dict(groupby(attrgetter("symbol", "side"), options, with_keys=True))
