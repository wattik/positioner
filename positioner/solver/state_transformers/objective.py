import numpy as np
import pulp
from scipy import stats

from positioner.pandl import future_expenses, immediate_pandl, total_pandl
from positioner.solver.problem import State


class GaussianWeights:
    def __init__(self, center, delta, space):
        scale = delta / stats.norm.ppf(0.99)
        self.weights = stats.norm.pdf(space, center, scale)

    def __call__(self, xs):
        return np.sum(xs * self.weights)


class GaussianPAndLObjective:
    def __init__(self, center: float, delta: float, space: np.ndarray, available: float, total_budget: float,
                 current_price: float):
        self.current_price = current_price
        self.available = available
        self.total_budget = total_budget
        self.weigh = GaussianWeights(center, delta, space)
        self.space = space

    def __call__(self, state: State):
        """
        Estimate FINAL P&L without offset, hence margin and previous earnings not taken into budget.
        """
        wpandls = []

        for option, amount in state.vars.all_to_open().items():
            wpandls.append(amount * self.weigh(total_pandl(option, self.space) / option.price))

        for option, amount in state.vars.all_to_close().items():
            wpandls.append(amount * self.weigh(immediate_pandl(option, self.space) / option.price))

            # This here signals P&L is increased by closing an option since no exercise fee will be payed
            wpandls.append(amount * self.weigh(future_expenses(option, self.space) / option.price))

        state.objective(pulp.lpSum(wpandls))
