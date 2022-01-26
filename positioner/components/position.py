from dataclasses import dataclass

from .order import Order


@dataclass
class Position:
    orders: list[Order]
    balance: float
