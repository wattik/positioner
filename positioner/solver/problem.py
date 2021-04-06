from dataclasses import dataclass
from typing import Callable, Iterator

import pulp as pl

from positioner import config
from positioner.orderbook import Option, Side
from positioner.position import Order, OrderType


@dataclass
class Variables:
    buy: dict[Option, pl.LpVariable]
    sell: dict[Option, pl.LpVariable]

    def all(self):
        return self.buy | self.sell

@dataclass
class State:
    model: pl.LpProblem
    vars: Variables

    def constrain(self, expr):
        self.model += expr

    def objective(self, obj):
        self.model += obj


def make_order_book_vars(model: pl.LpProblem, order_book: Iterator[Option]):
    variables = {}
    for option in order_book:
        amount = pl.LpVariable(
            name=f"{option.symbol}-{option.side}-PRC{option.price}-QNTY{option.quantity}",
            lowBound=0.0
        )
        model += amount <= option.quantity * option.price
        variables[option] = amount
    return variables

@dataclass
class Strategy:
    value: float
    orders: list[Order]

class StrategyComputer:
    def __init__(self, order_book: list[Option], solver_path=None):
        solver_path = solver_path or config.default("solver", "glpk_path")

        self.model = pl.LpProblem("OptionTradingStrategy", pl.LpMaximize)
        self.solver = pl.GLPK_CMD(path=solver_path)
        self.state = State(
            model=self.model,
            vars=Variables(
                buy=make_order_book_vars(self.model, filter(lambda e: e.side == Side.ASK, order_book)),
                sell=make_order_book_vars(self.model, filter(lambda e: e.side == Side.BID, order_book)),
            )
        )

    def specify(self, specify: Callable):
        specify(self.state)

    def compute(self) -> Strategy:
        status = self.solver.solve(self.model)
        status_str = pl.LpStatus[status]
        assert status_str == "Optimal", status_str
        optimal_value = self.model.objective.value()

        orders = []
        for option, var in self.state.vars.sell.items():
            amount = var.value()
            if amount > 0.0:
                orders += [Order(amount, OrderType.SELL, option)]

        for option, var in self.state.vars.buy.items():
            amount = var.value()
            if amount > 0.0:
                orders += [Order(amount, OrderType.BUY, option)]

        return Strategy(optimal_value, orders)