import numpy as np
from scipy import stats

from positioner.orderbook import Option
from positioner.pandl import value, cost, Order
from .problem import State


class GaussianObjective:
    def __init__(self, center, delta, space, initial_position: list[Order] = None, scale=None):
        if scale:
            raise DeprecationWarning("use delta instead")

        scale = delta / stats.norm.ppf(0.99)
        self.weights = stats.norm.pdf(space, center, scale)
        self.space = space

        if initial_position:
            self.base_pandl = self.get_base_pandl(initial_position)
        else:
            self.base_pandl = 0.0

    def get_base_pandl(self, position: list[Order]):
        base_pandl = 0.0

        for order in position:
            quantity = order.amount / order.price
            base_pandl += quantity * self.weighted_pandl(order.option)

        return base_pandl

    def weighted_pandl(self, option: Option):
        pandl = value(option, self.space) - cost(option, self.space)
        return np.sum(pandl * self.weights)

    def __call__(self, state: State):
        wpandl = self.base_pandl

        for option, amount in state.vars.all().items():
            quantity = amount * (1 / option.price)
            wpandl += quantity * self.weighted_pandl(option)

        state.objective(wpandl)
