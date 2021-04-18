from typing import Union

import numpy as np

from positioner.orderbook import Option, OptionType, Side
from positioner.position import Order


def cost_option_buy_call(d, xs):
    return np.ones_like(xs) * d.price


def cost_option_sell_call(d, xs):
    return np.zeros_like(xs)


def cost_option_buy_put(d, xs):
    return np.ones_like(xs) * d.price


def cost_option_sell_put(d, xs):
    return np.zeros_like(xs)


def cost_order(order: Order, space: np.ndarray):
    return order.quantity * cost(order.option, space)


def cost_orders(orders: list[Order], space: np.ndarray):
    v = 0
    for order in orders:
        v += cost(order, space)
    return v


def cost(option: Union[Option, list], space: np.ndarray):
    # orders
    if isinstance(option, list) and isinstance(option[0], Order):
        return cost_orders(option, space)
    if isinstance(option, Order):
        return cost_order(option, space)

    # options
    if option.option_type == OptionType.CALL and option.side == Side.ASK:
        return cost_option_buy_call(option, space)
    elif option.option_type == OptionType.CALL and option.side == Side.BID:
        return cost_option_sell_call(option, space)
    elif option.option_type == OptionType.PUT and option.side == Side.ASK:
        return cost_option_buy_put(option, space)
    elif option.option_type == OptionType.PUT and option.side == Side.BID:
        return cost_option_sell_put(option, space)
    else:
        raise ValueError(option)
