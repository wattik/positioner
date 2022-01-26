import logging
from dataclasses import dataclass
from functools import reduce
from operator import add
from typing import Callable

from positioner.components.option import Option
from .stats import Recorder, StatsComputer


class RolloutSimulator:
    def __init__(self, single_strategy: Callable):
        self.single_strategy = single_strategy
        self.recorder = Recorder()

    def step(self, order_book: list[Option], index_price: float, additional_budget: float, timestamp, **strategy_setup):
        available, position, total_budget, historical_orders = self.init_step()

        total_budget += additional_budget
        available += additional_budget

        strategy = self.single_strategy(
            order_book,
            index_price,
            budget=available,
            total_budget=total_budget,
            initial_position=position,
            historical_orders=historical_orders,
            **strategy_setup
        )

        if not strategy.optimal:
            logging.warning(f"Not optimal: {strategy.solver_status}")
            sell_profit = 0.0
            expenses = 0.0
            account = available
        else:
            position = strategy.position
            sell_profit = strategy.sell_profit
            expenses = strategy.expenses
            account = strategy.account

        self.recorder.add_result(
            account=account,
            position=position,
            new_orders=strategy.trade_orders,
            total_budget=total_budget,
            sell_profit=sell_profit,
            step_budget=additional_budget,
            expenses=expenses,
            index_price=index_price,
            timestamp=timestamp,
            is_optimal=strategy.optimal,
            available=available,
        )

    def init_step(self):
        if self.recorder.empty():
            available = 0.0
            position = []
            total_budget = 0.0
            historical_orders = []
        else:
            available = self.recorder.last.account
            position = self.recorder.last.position
            total_budget = self.recorder.last.total_budget
            historical_orders = reduce(add, self.recorder["new_orders"], [])

        return available, position, total_budget, historical_orders

    def finalize(self, final_index_price):
        self.recorder.apply(StatsComputer(final_index_price))
        return SimulationResult.from_history(self.recorder)


@dataclass
class SimulationResult:
    history: Recorder
    total_budget: float
    final_account: float
    pandl: float

    @classmethod
    def from_history(cls, history: Recorder):
        return cls(
            history,
            history.last.total_budget,
            history.last.account,
            history.last.final_pandl,
        )
