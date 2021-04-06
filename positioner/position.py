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

    def __repr__(self):
        return f"{self.order_type} {self.amount:1.3f}USD {self.option} at {self.price:1.3f}USD"