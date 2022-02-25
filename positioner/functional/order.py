from operator import attrgetter

from positioner.components.option import Option, Side
from positioner.components.order import Order, OrderType
from positioner.utils.functools import groupby

MIN_VALUE = 1e-14


def remove_below_quantity(orders: list[Order], q: float):
    final_orders = []
    for o in orders:
        # Solve Numeric Instability
        if abs(q - o.quantity) < MIN_VALUE:
            q = 0
            continue

        # Order fully matched, thus remove
        if o.quantity <= q:
            q -= o.quantity
            continue

        # Portion of the order matched, the rest remains
        if o.quantity > q > MIN_VALUE:
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
            price=amount / quantity,
            side=orders[0].option.side
        ))

    return options


def aggregate_orders(orders_redundant: list[Order]) -> list[Order]:
    orders_squeezed = []
    for (symbol, order_type), orders in groupby(attrgetter("symbol", "order_type"), orders_redundant, with_keys=True):
        amount = sum(o.amount for o in orders)
        quantity = sum(o.quantity for o in orders)

        orders_squeezed.append(Order(
            order_type=order_type,
            amount=amount,
            option=Option(
                price=amount / quantity,
                symbol=symbol,
                quantity=quantity,
                side=Side.ASK if order_type == OrderType.BUY else Side.BID
            )
        ))

    return orders_squeezed


def divide_orders_by_side(orders: list[Order]):
    buys = [o for o in orders if o.order_type == OrderType.BUY]
    sells = [o for o in orders if o.order_type == OrderType.SELL]
    return buys, sells
