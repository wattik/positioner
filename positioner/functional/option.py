from operator import attrgetter

from positioner.components.option import Option, Side
from positioner.components.order import Order, PositionQuantities
from positioner.utils.functools import groupby
from positioner.utils.itertools import collector


@collector(list)
def remove_above_amount(order_book: list[Option], max_amount: float):
    """Removes options that are strictly above the amount (budget)."""
    order_book = sorted(order_book, key=distance_to_fair_price)
    amount = 0.0
    for o in order_book:
        yield o
        amount += o.amount
        if amount > max_amount:
            break


def distance_to_fair_price(option: Option, fair_price=0.0):
    if option.side == Side.ASK:
        return option.price - fair_price
    else:
        return fair_price - option.price


def partition_option_by_quantity(option: Option, q: float):
    if option.quantity > q > 0:
        return (
            Option(option.price, q, option.side, option.symbol),
            Option(option.price, option.quantity - q, option.side, option.symbol)
        )
    else:
        raise ValueError(f"{option} {option.quantity} {q}")


@collector(list)
def clean_order_book_from_costly_trades(order_book: list[Option], budget: float) -> list[Option]:
    for options in groupby(attrgetter("symbol", "side"), order_book):
        yield from remove_above_amount(options, budget)


@collector(list)
def clean_order_book_from_position(order_book: list[Option], position: list[Order]) -> list[Option]:
    position_quantities = PositionQuantities(position, attrgetter("symbol", "side", "price"))

    for option in order_book:
        q = position_quantities[option]

        if q >= option.quantity:
            position_quantities[option] -= option.quantity

        elif option.quantity > q > 0:
            position_quantities[option] -= option.quantity
            yield Option(
                price=option.price,
                quantity=option.quantity - q,
                side=option.side,
                symbol=option.symbol
            )

        elif q <= 0:
            yield option
