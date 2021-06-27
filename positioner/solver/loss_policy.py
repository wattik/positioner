import numpy as np

from positioner.pandl import value, cost
from .problem import State
from positioner.position import Order


class MaxRelativeLossPolicy:
    def __init__(self, max_relative_loss, space: np.ndarray, initial_position: list[Order] = None):
        self.max_relative_loss = max_relative_loss
        self.space = space
        self.initial_position = initial_position or []

    def __call__(self, state: State):
        # precompute p&l values
        pandls = {
            option: value(option, self.space) - cost(option, self.space)
            for option in state.vars.all().keys()
        }

        # compute base p&l from the initial position
        base_pandl = np.zeros_like(self.space)
        for order in self.initial_position:
            option = order.option
            pandl = value(option, self.space) - cost(option, self.space)
            quantity = order.amount / option.price
            base_pandl += quantity * pandl

        # Expenses
        expenses = 0.0
        for order in self.initial_position:
            expenses += order.amount

        for amount in state.vars.buy.values():
            expenses += amount

        # Constrain so that all p&l over points in space >= maximal relative loss * expenses
        for i in range(len(self.space)):
            net_pandl_i = base_pandl[i]

            for option, amount in state.vars.all().items():
                pandl = amount * pandls[option][i] / option.price
                net_pandl_i += pandl

            state.constrain(net_pandl_i >= self.max_relative_loss * expenses)
