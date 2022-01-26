import numpy as np
import modelling as ml

from positioner.components.order import Order
from positioner.pandl import future_expenses, immediate_allocations, position_margin, total_allocations
from positioner.pandl.cache import PandLCache
from positioner.solver.problem import State


class MaxExpensesPolicy:
    """
    Ensure that for prices in `ins`:
        budget >= margin + cost + transaction fee + exercise fee
    """

    def __init__(self, budget, initial_position: list[Order], space: np.ndarray, current_price: float):
        self.current_price = current_price
        self.initial_position = initial_position
        self.space = space
        self.budget = budget

    def __call__(self, state: State):
        cache = PandLCache()
        position_margin_c = cache.precompute(position_margin, self.initial_position, self.space)
        future_expenses_c = cache.precompute(future_expenses, state.vars.all_to_close(), self.space)

        expenses_base = ml.LinearCombination()
        for option, amount in state.vars.all_to_open().items():
            expenses_base.add(amount, (total_allocations(option, self.current_price) / option.price))

        for option, amount in state.vars.all_to_close().items():
            expenses_base.add(amount, (immediate_allocations(option, self.current_price) / option.price))

        for x in self.space:
            expenses = ml.LinearCombination(expenses_base.variables[:], expenses_base.constants[:])
            expenses.offset = sum(
                position_margin_c(order, x) for order in self.initial_position
            )

            for option, amount in state.vars.all_to_close().items():
                # This here signals expenses are decreased by closing an option since no exercise fee is payed
                expenses.add(amount, (-future_expenses_c(option, x) / option.price))

            state.constrain(expenses, self.budget)
