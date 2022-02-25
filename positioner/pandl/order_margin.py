import numpy as np

from positioner.components.option import Option
from .dispatcher import EvaluationFuncDispatcher
from .position_margin import position_margin_option_sell_call, position_margin_option_sell_put
from .transaction_fee import transaction_fee_option_sell_call, transaction_fee_option_sell_put


def order_margin_option_buy_call(d: Option, xs):
    return np.zeros_like(xs)


def order_margin_option_sell_call(d: Option, xs):
    return (
        np.maximum(
            xs * 0.1,
            position_margin_option_sell_call(d, xs) - d.price
        )
        + transaction_fee_option_sell_call(d, xs)
    )


def order_margin_option_buy_put(d, xs):
    return np.zeros_like(xs)


def order_margin_option_sell_put(d, xs):
    return (
        np.maximum(
            xs * 0.1,
            position_margin_option_sell_put(d, xs) - d.price
        )
        + transaction_fee_option_sell_put(d, xs)
    )


order_margin = EvaluationFuncDispatcher(dict(
    buy_call=order_margin_option_buy_call,
    sell_call=order_margin_option_sell_call,
    buy_put=order_margin_option_buy_put,
    sell_put=order_margin_option_sell_put,
))
