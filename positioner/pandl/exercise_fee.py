from positioner.pandl.dispatcher import EvaluationFuncDispatcher

EXER_FEE_RATE = 0.015 / 100


# NOTE: the Binance documentation says only the buyer pays an exercise transaction_fee but
#   the actual transaction history suggests that exercise fees are withdrawn
#   on both sides of the trade.


def exercise_fee_option_buy_call(d, xs):
    exercise_idx = xs >= d.strike_price
    return EXER_FEE_RATE * xs * exercise_idx


def exercise_fee_option_sell_call(d, xs):
    exercise_idx = xs >= d.strike_price
    return EXER_FEE_RATE * xs * exercise_idx


def exercise_fee_option_buy_put(d, xs):
    exercise_idx = xs <= d.strike_price
    return EXER_FEE_RATE * xs * exercise_idx


def exercise_fee_option_sell_put(d, xs):
    exercise_idx = xs <= d.strike_price
    return EXER_FEE_RATE * xs * exercise_idx


exercise_fee = EvaluationFuncDispatcher(dict(
    buy_call=exercise_fee_option_buy_call,
    sell_call=exercise_fee_option_sell_call,
    buy_put=exercise_fee_option_buy_put,
    sell_put=exercise_fee_option_sell_put,
))
