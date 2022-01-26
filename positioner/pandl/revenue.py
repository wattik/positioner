import numpy as np

from positioner.components.option import Option
from positioner.pandl.dispatcher import EvaluationFuncDispatcher


def revenue_option_buy_call(d: Option, xs):
    return np.zeros_like(xs)


def revenue_option_sell_call(d, xs):
    return np.zeros_like(xs) + d.price


def revenue_option_buy_put(d, xs):
    return np.zeros_like(xs)


def revenue_option_sell_put(d, xs):
    return np.zeros_like(xs) + d.price


revenue = EvaluationFuncDispatcher(dict(
    buy_call=revenue_option_buy_call,
    sell_call=revenue_option_sell_call,
    buy_put=revenue_option_buy_put,
    sell_put=revenue_option_sell_put,
))
