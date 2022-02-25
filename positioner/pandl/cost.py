import numpy as np

from positioner.pandl.dispatcher import EvaluationFuncDispatcher


def unit(x): return x / x


def zero(x): return 0 * x


def cost_option_buy_call(d, xs):
    return unit(xs) * d.price


def cost_option_sell_call(d, xs):
    return zero(xs)


def cost_option_buy_put(d, xs):
    return unit(xs) * d.price


def cost_option_sell_put(d, xs):
    return zero(xs)


cost = EvaluationFuncDispatcher(dict(
    buy_call=cost_option_buy_call,
    sell_call=cost_option_sell_call,
    buy_put=cost_option_buy_put,
    sell_put=cost_option_sell_put,
))
