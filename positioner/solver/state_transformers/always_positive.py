import numpy as np
from positioner.components.order import Order
from positioner.pandl import future_expenses, future_transactions, immediate_transactions, value
from positioner.solver.problem import State


class AlwaysPositivePolicy:
    def __init__(self, total_budget: float, budget: float, current_price: float, initial_position: list[Order]):
        self.current_price = current_price
        self.budget = budget
        self.total_budget = total_budget
        self.initial_position = initial_position

    def __call__(self, state: State):
        pandl = state.lp_context.new_linear_combination()
        pandl.offset = (
            self.budget - self.total_budget
            + sum(future_transactions(order, self.current_price) for order in self.initial_position)
        )

        for option, amount in state.vars.all.items():
            pandl.add(amount, (immediate_transactions(option, self.current_price) / option.price))

        for option, amount in state.vars.all_to_open.items():
            pandl.add(amount, (future_transactions(option, self.current_price) / option.price))

        for option, amount in state.vars.all_to_close.items():
            pandl.add(amount, (value(option, self.current_price) / option.price))
            # correcting the exercise fee for position options that has not been matched
            pandl.add(amount, (future_expenses(option, self.current_price) / option.price))

        state.constrain(0, pandl)
