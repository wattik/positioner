from dataclasses import dataclass
from functools import cached_property
from operator import attrgetter

from positioner.components.order import Order
from positioner.functional.order import aggregate_orders, divide_orders_by_side, remove_below_quantity
from positioner.pandl import immediate_expenses, revenue
from positioner.utils.functools import groupby


def match_order_sides(buys, sells):
    q_buys = sum(o.quantity for o in buys)
    q_sells = sum(o.quantity for o in sells)

    if q_buys > q_sells:
        return remove_below_quantity(buys, q_sells)
    elif q_sells > q_buys:
        return remove_below_quantity(sells, q_buys)
    else:
        return []


def match_orders(orders: list[Order]) -> list[Order]:
    unique = []
    for ord_group in groupby(attrgetter("symbol"), orders):
        buys, sells = divide_orders_by_side(ord_group)
        if not buys or not sells:
            unique += ord_group

        else:
            unique += match_order_sides(buys, sells)

    return unique


@dataclass
class Strategy:
    value: float
    initial_position: list[Order]
    trade_orders: list[Order]
    optimal: bool
    solver_status: str
    index_price: float
    budget: float

    @cached_property
    def position(self):
        return aggregate_orders(match_orders(self.initial_position + self.trade_orders))

    @cached_property
    def sell_profit(self):
        return float(revenue(self.trade_orders, self.index_price))

    @cached_property
    def expenses(self):
        return float(immediate_expenses(self.trade_orders, self.index_price))

    @cached_property
    def account(self):
        return float(self.budget + self.sell_profit - self.expenses)
