from collections import Callable
from itertools import chain

import numpy as np

from positioner.components.order import Order
from positioner.pandl import future_expenses, future_transactions, immediate_transactions, value
from positioner.pandl.cache import PandLCache
from positioner.solver.problem import State

"""
The idea of this policy is to constrain the total expenses to
maintain a given ratio to P&L.

For instance, total expenses are expected to be lower than 20% of P&L. This
would be expressed by:
    for all prices p:
        -0.2 * expenses(s) <= p_and_l(p)


The above inequality is equivalent to the following:
    (1 - 0.2) * expenses(s) <= value(s, p)

Considering optimisation is performed, for each given expenses
there is a corresponding maximal value. Hence, we can describe the
situation with a function of expenses.
    max_value(expenses) = max value given the expenses

The max profit curve is a set of points in a value-expenses plane
that is described by the max_value function.

The Max relative loss policy and its corresponding inequality
ensure that only those expenses (and the corresponding max values)
that are located above the line (1-alpha) * expenses = value
are admissible.

This becomes important in situations when the max profit curve



Or alternatively:
    for all prices p:
        -0.2 <= profitability(p)

NOTE: The negative sign corresponds to the fact we limit losses that are captured in P&L
in negative values while expenses, i.e. additional_budget, is a positive value. To relate losses
to expenses, we must use a sign.
"""


class MaxLossPolicy:
    def __init__(self, total_budget: float, budget: float, current_price: float, space: np.ndarray,
                 initial_position: list[Order], max_relative_loss: float = None, max_absolute_loss: float = None):
        self.current_price = current_price
        self.budget = budget
        self.max_absolute_loss = max_absolute_loss or max_relative_loss * total_budget
        self.space = space
        self.total_budget = total_budget
        self.initial_position = initial_position

    def __call__(self, state: State):
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

        # Constrain so that all p&l over points in ins >= maximal relative loss * expenses
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

            #   -a * expenses(s) <= value(s, p) - total_budget
            state.constrain(self.max_absolute_loss, pandl)


class LowerBoundLossPolicy:
    def __init__(self, total_budget: float, budget: float, current_price: float, space: np.ndarray,
                 initial_position: list[Order], lower_bound_func: Callable[[np.ndarray, float], np.ndarray]):
        self.current_price = current_price
        self.budget = budget
        self.lower_bound = lower_bound_func(space, current_price)
        self.space = space
        self.total_budget = total_budget
        self.initial_position = initial_position

    def __call__(self, state: State):
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

        # Constrain so that all p&l over points in ins >= maximal relative loss * expenses
        for lb, future_price in zip(self.lower_bound, self.space):
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

            #   lb(p) <= value(s, p) - total_budget
            state.constrain(lb, pandl)


class ImprovingPandlPolicy:
    def __init__(self, total_budget: float, budget: float, current_price: float, space: np.ndarray,
                 initial_position: list[Order], maximal_absolute_loss: float, discount_rate: float = None):
        self.discount_rate = discount_rate or 0.9
        self.maximal_absolute_loss = maximal_absolute_loss
        self.current_price = current_price
        self.budget = budget
        self.space = space
        self.total_budget = total_budget
        self.initial_position = initial_position

    def __call__(self, state: State):
        hard_stop = np.ones_like(self.space) * self.maximal_absolute_loss

        if not self.initial_position:
            lower_bound = hard_stop
        else:
            lower_bound = (
                np.ones_like(self.space) * (self.budget - self.total_budget)
                + sum(future_transactions(order, self.space) for order in self.initial_position)
            )
            discounted = (lower_bound - hard_stop) * self.discount_rate + hard_stop
            lower_bound = np.maximum(discounted, hard_stop)

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

        for lb, future_price in zip(lower_bound, self.space):
            pandl = pandl_base.fork()
            pandl.offset = (
                self.budget - self.total_budget
                + sum(future_transactions_c(order, future_price) for order in self.initial_position)
            )

            for option, amount in state.vars.all_to_open.items():
                pandl.add(amount, (future_transactions_c(option, future_price) / option.price))

            for option, amount in state.vars.all_to_close.items():
                pandl.add(amount, (value_c(option, future_price) / option.price))
                pandl.add(amount, (future_expenses_c(option, future_price) / option.price))

            #   lb(p) <= value(s, p) - total_budget
            state.constrain(lb, pandl)
