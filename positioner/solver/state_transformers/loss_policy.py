import numpy as np
import pulp

from positioner.components.order import Order
from positioner.pandl import future_expenses, immediate_pandl, total_pandl, value
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


class MaxRelativeLossPolicy:
    def __init__(self, max_relative_loss: float, total_budget: float, budget: float, current_price: float,
                 space: np.ndarray, initial_position: list[Order]):
        self.current_price = current_price
        self.budget = budget
        self.max_relative_loss = max_relative_loss
        self.space = space
        self.total_budget = total_budget
        self.initial_position = initial_position

    def __call__(self, state: State):
        cache = PandLCache()
        value_c = cache.precompute(value, self.initial_position, self.space)
        total_pandl_c = cache.precompute(total_pandl, state.vars.all_to_open(), self.space)
        immediate_pandl_c = cache.precompute(immediate_pandl, state.vars.all_to_close(), self.space)
        future_expenses_c = cache.precompute(future_expenses, state.vars.all_to_close(), self.space)

        # Constrain so that all p&l over points in ins >= maximal relative loss * expenses
        for future_price in self.space:
            pandl_base = (
                self.budget - self.total_budget
                + sum(value_c(order, future_price) for order in self.initial_position)
            )

            terms = []
            for option, amount in state.vars.all_to_open().items():
                terms += [(amount, (total_pandl_c(option, future_price) / option.price))]

            for option, amount in state.vars.all_to_close().items():
                terms += [(amount, (immediate_pandl_c(option, future_price) / option.price))]

                # correcting the exercise fee for position options that has not been matched
                terms += [(amount, (future_expenses_c(option, future_price) / option.price))]

            pandl = pulp.LpAffineExpression(terms) + pandl_base

            #   -a * expenses(s) <= value(s, p) - total_budget
            state.constrain(self.max_relative_loss * self.total_budget <= pandl)
