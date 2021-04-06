import numpy as np

from positioner.orderbook import Option, OptionType, Side


def cost_option_buy_call(d, xs):
    return np.ones_like(xs) * d.price


def cost_option_sell_call(d, xs):
    return np.zeros_like(xs)


def cost_option_buy_put(d, xs):
    return np.ones_like(xs) * d.price


def cost_option_sell_put(d, xs):
    return np.zeros_like(xs)


def cost(option: Option, space: np.ndarray):
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
