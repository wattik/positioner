import numpy as np

from .problem import State
from positioner.pandl import value, cost


class MaxRelativeLossPolicy:
    def __init__(self, max_relative_loss, space: np.ndarray):
        self.max_relative_loss = max_relative_loss
        self.space = space

    def __call__(self, state: State):
        pandls = {
            option: value(option, self.space) - cost(option, self.space)
            for option in state.vars.all().keys()
        }

        expenses = 0.0
        for amount in state.vars.buy.values():
            expenses += amount

        # Constrain so that all p&l over points in space >= maximal relative loss * expenses
        for i in range(len(self.space)):
            net_pandl_i = 0.0
            for option, amount in state.vars.all().items():
                pandl = amount * pandls[option][i] / option.price
                net_pandl_i += pandl

            state.constrain(net_pandl_i >= self.max_relative_loss * expenses)
