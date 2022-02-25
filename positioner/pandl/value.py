from positioner.components.option import Option
from positioner.pandl.dispatcher import EvaluationFuncDispatcher


def value_option_buy_call(d: Option, xs):
    y = xs - d.strike_price
    y[y <= 0] = 0
    return y


def value_option_sell_call(d: Option, xs):
    y = xs - d.strike_price
    y[y <= 0] = 0
    return -y


def value_option_buy_put(d, xs):
    y = -(xs - d.strike_price)
    y[y <= 0] = 0
    return y


def value_option_sell_put(d, xs):
    y = -(xs - d.strike_price)
    y[y <= 0] = 0
    return -y


value = EvaluationFuncDispatcher(dict(
    buy_call=value_option_buy_call,
    sell_call=value_option_sell_call,
    buy_put=value_option_buy_put,
    sell_put=value_option_sell_put,
))
