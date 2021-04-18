from typing import Union

import numpy as np

from positioner.orderbook import Option, OptionType, Side
from positioner.position import Order


def value_option_buy_call(d: Option, xs):
    y = xs - d.strike_price
    y[y <= 0] = 0
    return y


def value_option_sell_call(d, xs):
    y = xs - d.strike_price
    y[y <= 0] = 0
    y -= d.price
    return -y


def value_option_buy_put(d, xs):
    y = -(xs - d.strike_price)
    y[y <= 0] = 0
    return y


def value_option_sell_put(d, xs):
    y = -(xs - d.strike_price)
    y[y <= 0] = 0
    y -= d.price
    return -y


def value_order(order: Order, space: np.ndarray):
    return order.quantity * value(order.option, space)


def value_orders(orders: list[Order], space: np.ndarray):
    v = 0
    for order in orders:
        v += value(order, space)
    return v


def value(to_be_valued: Union[Option, Order, list], space: np.ndarray):
    # orders
    if isinstance(to_be_valued, list) and isinstance(to_be_valued[0], Order):
        return value_orders(to_be_valued, space)
    if isinstance(to_be_valued, Order):
        return value_order(to_be_valued, space)

    # options
    if to_be_valued.option_type == OptionType.CALL and to_be_valued.side == Side.ASK:
        return value_option_buy_call(to_be_valued, space)
    elif to_be_valued.option_type == OptionType.CALL and to_be_valued.side == Side.BID:
        return value_option_sell_call(to_be_valued, space)
    elif to_be_valued.option_type == OptionType.PUT and to_be_valued.side == Side.ASK:
        return value_option_buy_put(to_be_valued, space)
    elif to_be_valued.option_type == OptionType.PUT and to_be_valued.side == Side.BID:
        return value_option_sell_put(to_be_valued, space)
    else:
        raise ValueError(to_be_valued)
