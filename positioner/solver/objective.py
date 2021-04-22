import numpy as np
from scipy import stats

from positioner.orderbook import Option
from positioner.pandl import value, cost
from .problem import State


class GaussianObjective:
    def __init__(self, center, delta, space, base_pandl=None, scale=None):
        if scale:
            raise DeprecationWarning("use delta instead")

        scale = delta/stats.norm.ppf(0.99)
        self.weights = stats.norm.pdf(space, center, scale)
        self.space = space

        self.base_pandl = np.sum((base_pandl or 0.0) * self.weights)

    def weighted_pandl(self, option: Option):
        pandl = value(option, self.space) - cost(option, self.space)
        return np.sum(pandl * self.weights)

    def __call__(self, state: State):
        wpandl = self.base_pandl
        for option, amount in state.vars.all().items():
            quantity = amount * (1/option.price)
            wpandl += quantity * self.weighted_pandl(option)
        state.objective(wpandl)
