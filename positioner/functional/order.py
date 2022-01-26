from operator import attrgetter

from positioner.components.option import Option
from positioner.components.order import Order
from positioner.utils.functools import groupby


def remove_below_quantity(orders: list[Order], q: float):
    final_orders = []
    for o in orders:
        # Order fully matched, thus remove
        if o.quantity <= q:
            q -= o.quantity
            continue

        # Portion of the order matched, the rest remains
        if o.quantity > q > 0:
            amount = (o.quantity - q) * o.price
            q = 0
            new_o = Order(amount, o.order_type, o.option)
            final_orders.append(new_o)

        # All matching completed, keep remaining position
        else:
            final_orders.append(o)

    return final_orders


def squeeze_orders_to_options(orders: list[Order]) -> list[Option]:
    options = []
    for orders in groupby(attrgetter("symbol", "order_type"), orders):
        amount = sum(o.amount for o in orders)
        quantity = sum(o.quantity for o in orders)

        options.append(Option(
            quantity=quantity,
            symbol=orders[0].symbol,
            price=amount/quantity,
            side=orders[0].option.side
        ))

    return options
