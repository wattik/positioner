from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from positioner.components.option import Option, Side


class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"

    def __str__(self):
        return self.name


@dataclass
class Order:
    amount: float
    order_type: OrderType
    option: Option

    __hash_mem__ = None

    @property
    def price(self):
        return self.option.price

    @property
    def strike_price(self):
        return self.option.strike_price

    @property
    def side(self):
        return self.option.side

    @property
    def symbol(self):
        return self.option.symbol

    @property
    def quantity(self):
        return self.amount / self.price

    def __hash__(self):
        if self.__hash_mem__ is None:
            self.__hash_mem__ = hash((self.amount, self.order_type, self.option))
        return self.__hash_mem__

    def __repr__(self):
        return f"{self.order_type} {self.quantity:1.3f} ({self.amount:1.3f}USD) {self.option}"

    @classmethod
    def make(cls, amount, order_type, option: Option):
        return cls(float(amount), OrderType(order_type), option)

    @classmethod
    def parse(cls, string: str):
        order_type, amount, option, _, price = string.split(" ")
        amount = float(amount.replace("USD", ""))
        price = float(price.replace("USD", ""))

        if "BID" in option:
            symbol = option.replace("-BID", "")
            side = "BID"
        else:
            symbol = option.replace("-ASK", "")
            side = "ASK"

        option = Option.make(price, amount / price, side, symbol)
        return cls.make(amount, order_type, option)


def parse_orders(string: str):
    orders_str = string.strip().replace("[", "").replace("]", "").split(",")
    orders = []
    for order in orders_str:
        orders += [Order.parse(order)]

    return orders


class PositionQuantities:
    def __init__(self, orders: list[Order], key_func: Callable):
        self.key_func = key_func
        self.quantities = defaultdict(float)
        for order in orders:
            self.quantities[self.key_func(order)] += order.quantity

    def __getitem__(self, option: Option):
        return self.quantities[self.key_func(option)]

    def __setitem__(self, option: Option, value):
        self.quantities[self.key_func(option)] = value


class MatchingQuantity:
    def __init__(self, orders: list[Order]):
        self.quantities = defaultdict(float)
        for order in orders:
            symbol = order.symbol
            matching_side = Side.ASK if order.side == Side.BID else Side.BID
            self.quantities[(symbol, matching_side)] += order.quantity

    def __getitem__(self, option: Option):
        return self.quantities[(option.symbol, option.side)]

    def __setitem__(self, option: Option, value):
        self.quantities[(option.symbol, option.side)] = value
