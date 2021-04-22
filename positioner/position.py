from dataclasses import dataclass
from enum import Enum

from positioner.orderbook import Option


class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class Order:
    amount: float
    order_type: OrderType
    option: Option

    @property
    def price(self):
        return self.option.price

    @property
    def strike_price(self):
        return self.option.strike_price

    @property
    def symbol(self):
        return self.option.symbol

    @property
    def quantity(self):
        return self.amount / self.price

    def __repr__(self):
        return f"{self.order_type} {self.amount:1.3f}USD {self.option} at {self.price:1.3f}USD"

    @classmethod
    def make(cls, amount, order_type, option: Option):
        return cls(float(amount), OrderType(order_type), option)

    @classmethod
    def parse(cls, string: str):
        order_type, amount, option, _, price = string.split(" ")
        order_type = order_type.split(".")[1]
        amount = float(amount.replace("USD", ""))
        price = float(price.replace("USD", ""))

        if "BID" in option:
            symbol = option.replace("-Side.BID", "")
            side = "BID"
        else:
            symbol = option.replace("-Side.ASK", "")
            side = "ASK"

        option = Option.make(price, amount/price, side, symbol)
        return cls.make(amount, order_type, option)


def parse_orders(string: str):
    orders_str = string.strip().replace("[", "").replace("]", "").split(",")
    orders = []
    for order in orders_str:
        orders += [Order.parse(order)]

    return orders