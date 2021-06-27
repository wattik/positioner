from positioner.position import Order
from .problem import State


class MaxCostPolicy:
    def __init__(self, budget, initial_position: list[Order] = None):
        self.budget = budget
        self.initial_position = initial_position or []

    def __call__(self, state: State):
        costs = 0.0

        for order in self.initial_position:
            costs += order.amount

        for amount in state.vars.buy.values():
            costs += amount

        state.constrain(costs <= self.budget)
