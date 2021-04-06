import numpy as np

from positioner.orderbook import Option, OptionType, Side


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


def value(option: Option, space: np.ndarray):
    if option.option_type == OptionType.CALL and option.side == Side.ASK:
        return value_option_buy_call(option, space)
    elif option.option_type == OptionType.CALL and option.side == Side.BID:
        return value_option_sell_call(option, space)
    elif option.option_type == OptionType.PUT and option.side == Side.ASK:
        return value_option_buy_put(option, space)
    elif option.option_type == OptionType.PUT and option.side == Side.BID:
        return value_option_sell_put(option, space)
    else:
        raise ValueError(option)
