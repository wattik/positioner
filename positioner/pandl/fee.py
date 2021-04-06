import numpy as np

from positioner.orderbook import Option, OptionType, Side
from . import value_option_buy_call, value_option_buy_put

TRANS_FEE_RATE = 0.03 / 100
EXER_FEE_RATE = 0.015 / 100


def fee_option_buy_call(d, xs):
    return d.indexPrice * TRANS_FEE_RATE + value_option_buy_call(d, xs) * EXER_FEE_RATE


def fee_option_sell_call(d, xs):
    return d.indexPrice * TRANS_FEE_RATE


def fee_option_buy_put(d, xs):
    return d.indexPrice * TRANS_FEE_RATE + value_option_buy_put(d, xs) * EXER_FEE_RATE


def fee_option_sell_put(d, xs):
    return d.indexPrice * TRANS_FEE_RATE


def fee(option: Option, space: np.ndarray):
    if option.option_type == OptionType.CALL and option.side == Side.ASK:
        return fee_option_buy_call(option, space)
    elif option.option_type == OptionType.CALL and option.side == Side.BID:
        return fee_option_sell_call(option, space)
    elif option.option_type == OptionType.PUT and option.side == Side.ASK:
        return fee_option_buy_put(option, space)
    elif option.option_type == OptionType.PUT and option.side == Side.BID:
        return fee_option_sell_put(option, space)
    else:
        raise ValueError(option)
