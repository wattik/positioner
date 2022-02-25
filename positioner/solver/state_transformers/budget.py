from itertools import chain

import numpy as np

from positioner.components.order import Order
from positioner.pandl import closing_margin, future_expenses, immediate_transactions, order_margin, position_margin
from positioner.pandl.cache import PandLCache
from positioner.solver.problem import State


class MaxExpensesPolicy:
    """
    Ensure that for prices in `ins`:
        budget >= margin + cost + transaction fee + exercise fee
    """

    def __init__(self, budget, initial_position: list[Order], space: np.ndarray, current_price: float):
        self.current_price = current_price
        self.initial_position = initial_position
        self.space = space
        self.budget = budget

    def __call__(self, state: State):
        cache = PandLCache()
        position_margin_c = cache.precompute(position_margin, self.initial_position, self.space)
        future_expenses_c = cache.precompute(future_expenses, chain(self.initial_position, state.vars.all), self.space)
        closing_margin_c = cache.precompute(closing_margin, state.vars.all_to_close, self.space)
        order_margin_c = cache.precompute(order_margin, state.vars.all_to_open, self.space)

        expenses_base = state.lp_context.new_linear_combination()
        for option, amount in state.vars.all_to_close.items():
            expenses_base.add(amount, (-immediate_transactions(option, self.current_price) / option.price))

        for option, amount in state.vars.buy_to_open.items():
            expenses_base.add(amount, (-immediate_transactions(option, self.current_price) / option.price))


        # TODO: make the expressions more compact to speed the problem setup
        for future_price in self.space:
            expenses = expenses_base.fork()
            expenses.offset = sum(position_margin_c(order, future_price) for order in self.initial_position)
            expenses.offset += sum(future_expenses_c(order, future_price) for order in self.initial_position)

            for option, amount in state.vars.sell_to_open.items():
                # order margin already takes into account cost and transaction fee
                expenses.add(amount, order_margin_c(option, future_price) / option.price)

            for option, amount in state.vars.all_to_open.items():
                expenses.add(amount, future_expenses_c(option, future_price) / option.price)

            for option, amount in state.vars.all_to_close.items():
                expenses.add(amount, -closing_margin_c(option, future_price) / option.price)
                # This here signals expenses are decreased by closing an option since no exercise fee is payed
                expenses.add(amount, -future_expenses_c(option, future_price) / option.price)

            state.constrain(expenses, self.budget)
