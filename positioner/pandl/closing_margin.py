from positioner.components.option import Option
from positioner.pandl import position_margin_option_buy_put, position_margin_option_sell_put
from positioner.pandl.dispatcher import EvaluationFuncDispatcher
from .position_margin import position_margin_option_buy_call, position_margin_option_sell_call


def closing_margin_option_buy_call(d: Option, xs):
    return position_margin_option_sell_call(d, xs)


def closing_margin_option_sell_call(d: Option, xs):
    return position_margin_option_buy_call(d, xs)


def closing_margin_option_buy_put(d, xs):
    return position_margin_option_sell_put(d, xs)


def closing_margin_option_sell_put(d, xs):
    return position_margin_option_buy_put(d, xs)

closing_margin = EvaluationFuncDispatcher(dict(
    buy_call=closing_margin_option_buy_call,
    sell_call=closing_margin_option_sell_call,
    buy_put=closing_margin_option_buy_put,
    sell_put=closing_margin_option_sell_put,
))
