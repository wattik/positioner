from typing import Union

from positioner.components.option import Option
from positioner.components.order import Order
from .closing_margin import closing_margin
from .cost import cost
from .exercise_fee import exercise_fee
from .position_margin import position_margin
from .revenue import revenue
from .transaction_fee import transaction_fee
from .utils import ArrayOrNumber
from .value import value


def immediate_expenses(to_be_valued: Union[Option, Order, list], space: ArrayOrNumber):
    return (
        cost(to_be_valued, space)
        + transaction_fee(to_be_valued, space)
    )


def future_expenses(to_be_valued: Union[Option, Order, list], space: ArrayOrNumber):
    return exercise_fee(to_be_valued, space)


def total_expenses(to_be_valued: Union[Option, Order, list], space: ArrayOrNumber):
    return (
        immediate_expenses(to_be_valued, space)
        + future_expenses(to_be_valued, space)
    )


###


def immediate_transactions(to_be_valued: Union[Option, Order, list], space: ArrayOrNumber):
    return (
        revenue(to_be_valued, space)
        - immediate_expenses(to_be_valued, space)
    )


def total_transactions(to_be_valued: Union[Option, Order, list], space: ArrayOrNumber):
    return (
        revenue(to_be_valued, space)
        - total_expenses(to_be_valued, space)
    )


def total_allocations(to_be_valued: Union[Option, Order, list], space: ArrayOrNumber):
    return (
        - total_transactions(to_be_valued, space)
        + position_margin(to_be_valued, space)
    )


def immediate_allocations(to_be_valued: Union[Option, Order, list], space: ArrayOrNumber):
    return (
        - immediate_transactions(to_be_valued, space)
        - closing_margin(to_be_valued, space)
    )


###


def total_pandl(to_be_valued: Union[Option, Order, list], space: ArrayOrNumber):
    return (
        value(to_be_valued, space)
        + total_transactions(to_be_valued, space)
    )


def immediate_pandl(to_be_valued: Union[Option, Order, list], space: ArrayOrNumber):
    return (
        value(to_be_valued, space)
        + immediate_transactions(to_be_valued, space)
    )
