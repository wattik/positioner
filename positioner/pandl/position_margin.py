import numpy as np

from positioner.components.option import Option
from positioner.pandl.dispatcher import EvaluationFuncDispatcher

# to estimate the mark price we use 120% of the traded price
MARKPRICE_DELTA_COEF = 1.2


def position_margin_option_buy_call(d: Option, xs):
    return np.zeros_like(xs)


def position_margin_option_sell_call(d: Option, xs):
    otm_amount = np.minimum(xs - d.strike_price, 0)
    markprice = MARKPRICE_DELTA_COEF * d.price
    return np.maximum(xs * 0.1, xs * 0.15 + otm_amount) + markprice


def position_margin_option_buy_put(d, xs):
    return np.zeros_like(xs)


def position_margin_option_sell_put(d, xs):
    otm_amount = np.minimum(d.strike_price - xs, 0)
    markprice = MARKPRICE_DELTA_COEF * d.price
    return np.maximum(xs * 0.1, xs * 0.15 + otm_amount) + markprice


position_margin = EvaluationFuncDispatcher(dict(
    buy_call=position_margin_option_buy_call,
    sell_call=position_margin_option_sell_call,
    buy_put=position_margin_option_buy_put,
    sell_put=position_margin_option_sell_put,
))
