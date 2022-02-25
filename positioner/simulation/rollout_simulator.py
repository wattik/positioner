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

    def step(self, *args, **kwargs):
        if self.recorder.empty():
            self.init_step(*args, **kwargs)
        else:
            self.next_step(*args, **kwargs)

    def init_step(self, order_book: list[Option], index_price: float, additional_budget: float, timestamp,
                  **strategy_setup):
        total_budget = additional_budget
        available = additional_budget
        position = []

        strategy = self.single_strategy(
            order_book,
            index_price,
            budget=available,
            total_budget=total_budget,
            initial_position=position,
            historical_orders=[],
            **strategy_setup
        )

        if not strategy.optimal:
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
            trade_orders=strategy.trade_orders,
            total_budget=total_budget,
            sell_profit=sell_profit,
            step_budget=additional_budget,
            expenses=expenses,
            index_price=index_price,
            timestamp=timestamp,
            is_optimal=strategy.optimal,
            objective_value=strategy.value,
            available=available,
        )

    def next_step(self, order_book: list[Option], index_price: float, additional_budget: float, timestamp,
                  **strategy_setup):
        available = self.recorder.last.account + additional_budget
        position = self.recorder.last.position
        total_budget = self.recorder.last.total_budget + additional_budget
        historical_orders = reduce(add, self.recorder["trade_orders"], [])

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
            sell_profit = 0.0
            expenses = 0.0
            account = available
            objective_value = self.recorder.last.objective_value
            trade_orders = []
        else:
            position = strategy.position
            sell_profit = strategy.sell_profit
            expenses = strategy.expenses
            account = strategy.account
            objective_value = strategy.value
            trade_orders = strategy.trade_orders

        self.recorder.add_result(
            account=account,
            position=position,
            trade_orders=trade_orders,
            total_budget=total_budget,
            sell_profit=sell_profit,
            step_budget=additional_budget,
            expenses=expenses,
            index_price=index_price,
            timestamp=timestamp,
            is_optimal=strategy.optimal,
            objective_value=objective_value,
            available=available,
        )

    def finalize(self, final_index_price):
        self.recorder.apply(StatsComputer(final_index_price))
        return SimulationResult.from_history(self.recorder)


@dataclass
class SimulationResult:
    history: Recorder
    total_budget: float
    final_account: float
    pandl: float
    profitability: float
    fail_rate: float

    def to_df(self):
        return self.history.to_df()

    @classmethod
    def from_history(cls, history: Recorder):
        return cls(
            history,
            history.last.total_budget,
            history.last.account,
            history.last.final_pandl,
            1 + history.last.final_pandl / history.last.total_budget,
            1 - sum(history["is_optimal"]) / len(history)
        )
