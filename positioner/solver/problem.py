from functools import cached_property
from operator import attrgetter
from typing import Callable

import modelling as ml
from positioner.components.option import Option, Side
from positioner.components.order import MatchingQuantity, Order, OrderType
from positioner.functional.option import distance_to_fair_price, partition_option_by_quantity
from positioner.solver.solution import Strategy


class Variables:
    def __init__(self, var_maker: Callable):
        self.var_maker = var_maker

        self.buy_to_open: dict[Option, ml.atoms.Variable] = dict()
        self.sell_to_open: dict[Option, ml.atoms.Variable] = dict()

        self.buy_to_close: dict[Option, ml.atoms.Variable] = dict()
        self.sell_to_close: dict[Option, ml.atoms.Variable] = dict()

    def __repr__(self):
        return f"{self.all_to_close}\n{self.all_to_open}"

    @property
    def buy(self):
        return self.buy_to_open | self.buy_to_close

    @property
    def sell(self):
        return self.sell_to_open | self.sell_to_close

    @cached_property
    def all_to_close(self):
        return self.buy_to_close | self.sell_to_close

    @cached_property
    def all_to_open(self):
        return self.sell_to_open | self.buy_to_open

    @cached_property
    def all(self):
        return self.all_to_open | self.all_to_close

    def add_to_close(self, option: Option):
        if option.side == Side.ASK:
            self.buy_to_close |= self.var_from_option(option)
        else:
            self.sell_to_close |= self.var_from_option(option)

    def add_to_open(self, option: Option):
        if option.side == Side.ASK:
            self.buy_to_open |= self.var_from_option(option)
        else:
            self.sell_to_open |= self.var_from_option(option)

    def var_from_option(self, option: Option):
        amount = self.var_maker(
            name=f"{option.symbol}-{option.side}-p{option.price}USD-q{option.quantity}",
            lower_bound=0,
            upper_bound=option.quantity * option.price
        )
        return {option: amount}


class State:
    def __init__(self, context: ml.LPContext, vars: Variables):
        self.lp_context = context
        self.vars = vars

    def constrain(self, left, right):
        self.lp_context.constrain(left, right)

    def objective(self, obj):
        self.lp_context.objective(obj)


class StrategyComputer:
    def __init__(self, order_book: list[Option], initial_position: list[Order], index_price: float, budget: float):
        self.budget = budget
        self.index_price = index_price
        self.initial_position = initial_position

        context = ml.LPContext()
        variables = Variables(var_maker=context.new_variable)

        position_quants = MatchingQuantity(initial_position)
        order_book = sorted(order_book, key=distance_to_fair_price)
        order_book = sorted(order_book, key=attrgetter("symbol"))

        for option in order_book:
            if option.quantity <= position_quants[option]:
                variables.add_to_close(option)
                position_quants[option] -= option.quantity

            elif option.quantity > position_quants[option] > 0:
                op_to_close, op_to_open = partition_option_by_quantity(option, position_quants[option])
                variables.add_to_close(op_to_close)
                variables.add_to_open(op_to_open)
                position_quants[option] = 0

            else:
                variables.add_to_open(option)

        self.state = State(context=context, vars=variables)

    def specify(self, specify: Callable):
        specify(self.state)

    def compute(self) -> Strategy:
        solution = ml.solve_cvxpy(self.state.lp_context)

        status_str = solution.message
        optimality = solution.optimality
        optimal_value = solution.value

        orders = []

        if optimality:
            for option, var in self.state.vars.sell.items():
                amount = var.value
                if amount > 1e-14:
                    orders += [Order(amount, OrderType.SELL, option)]

            for option, var in self.state.vars.buy.items():
                amount = var.value
                if amount > 1e-14:
                    orders += [Order(amount, OrderType.BUY, option)]

        return Strategy(
            value=optimal_value,
            initial_position=self.initial_position,
            trade_orders=orders,
            optimal=optimality,
            solver_status=status_str,
            index_price=self.index_price,
            budget=self.budget
        )
