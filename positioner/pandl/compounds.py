from typing import Union

from positioner.components.option import Option
from positioner.components.order import Order
from .cost import cost
from .exercise_fee import exercise_fee
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


def future_transactions(to_be_valued: Union[Option, Order, list], space: ArrayOrNumber):
    return (
        value(to_be_valued, space)
        - future_expenses(to_be_valued, space)
    )
