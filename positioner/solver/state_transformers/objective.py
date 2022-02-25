from itertools import chain

import numpy as np
from scipy import stats

from positioner.pandl import Order, future_expenses, future_transactions, immediate_transactions, value
from positioner.pandl.cache import PandLCache
from positioner.solver.problem import State
from positioner.solver.spaces import clamp_by_bounds, clamp_by_rel_bounds


class GaussianWeights:
    def __init__(self, center, delta, space):
        scale = delta / stats.norm.ppf(0.99)
        step = (space[1] - space[0]) / 2

        starts = space - step
        starts[0] = -np.inf

        ends = space + step
        ends[-1] = np.inf

        self.weights = stats.norm.cdf((ends - center) / scale) - stats.norm.cdf((starts - center) / scale)

    def __call__(self, xs):
        return 1000 * np.sum(xs * self.weights)


class GaussianPAndLObjective:
    def __init__(self, delta: float, space: np.ndarray, budget: float, total_budget: float,
                 current_price: float, initial_position: list[Order], expected_price: float):
        self.initial_position = initial_position
        self.budget = budget
        self.current_price = current_price
        self.total_budget = total_budget
        self.weigh = GaussianWeights(expected_price, delta, space)
        self.space = space

    def __call__(self, state: State):
        """
        Estimate FINAL P&L.
        """
        pandl_offset = self.weigh(
            np.ones_like(self.space) * (self.budget - self.total_budget)
            + sum(future_transactions(order, self.space) for order in self.initial_position)
        )

        wpandls = state.lp_context.new_linear_combination()
        wpandls.offset = pandl_offset

        for option, amount in state.vars.all.items():
            wpandls.add(amount, self.weigh(immediate_transactions(option, self.current_price) / option.price))

        for option, amount in state.vars.all_to_open.items():
            wpandls.add(amount, self.weigh(future_transactions(option, self.space) / option.price))

        for option, amount in state.vars.all_to_close.items():
            wpandls.add(amount, self.weigh(value(option, self.space) / option.price))
            # `future_expenses` here signals P&L is increased by closing an option since no exercise fee will be payed
            wpandls.add(amount, self.weigh(future_expenses(option, self.space) / option.price))

        state.objective(wpandls)


class MinPandLObjetive:
    def __init__(self, space: np.ndarray, budget: float, total_budget: float, current_price: float,
                 initial_position: list[Order], expected_price: float, relative_bounds=None, absolute_bounds=None):
        self.expected_price = expected_price
        self.current_price = current_price

        self.initial_position = initial_position
        self.budget = budget
        self.total_budget = total_budget

        if absolute_bounds:
            self.space = clamp_by_bounds(space, absolute_bounds)
        elif relative_bounds:
            self.space = clamp_by_rel_bounds(space, expected_price, relative_bounds)
        else:
            raise ValueError(f"{relative_bounds}, {absolute_bounds}")

    def __call__(self, state: State):
        """
        Maximize the minimum of the P&L within the values of `self.space`.
        """
        min_pandl = state.lp_context.new_variable("minpandl")
        lc = state.lp_context.new_linear_combination()
        lc.add(min_pandl, 1)
        state.objective(lc)

        cache = PandLCache()
        future_transactions_c = cache.precompute(
            future_transactions,
            chain(self.initial_position, state.vars.all_to_open),
            self.space
        )
        value_c = cache.precompute(value, state.vars.all_to_close, self.space)
        future_expenses_c = cache.precompute(future_expenses, state.vars.all_to_close, self.space)

        pandl_base = state.lp_context.new_linear_combination()
        for option, amount in state.vars.all.items():
            pandl_base.add(amount, (immediate_transactions(option, self.current_price) / option.price))

        for future_price in self.space:
            pandl = pandl_base.fork()
            pandl.offset = (
                self.budget - self.total_budget
                + sum(future_transactions_c(order, future_price) for order in self.initial_position)
            )

            for option, amount in state.vars.all_to_open.items():
                pandl.add(amount, (future_transactions_c(option, future_price) / option.price))

            for option, amount in state.vars.all_to_close.items():
                pandl.add(amount, (value_c(option, future_price) / option.price))
                # correcting the exercise fee for position options that has not been matched
                pandl.add(amount, (future_expenses_c(option, future_price) / option.price))

            pandl.add(min_pandl, -1.0)
            state.constrain(0, pandl)
