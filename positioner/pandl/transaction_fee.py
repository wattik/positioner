from positioner.pandl.dispatcher import EvaluationFuncDispatcher

TRANS_FEE_RATE = 0.03 / 100


def transaction_fee_option_buy_call(d, xs):
    return TRANS_FEE_RATE * xs


def transaction_fee_option_sell_call(d, xs):
    return TRANS_FEE_RATE * xs


def transaction_fee_option_buy_put(d, xs):
    return TRANS_FEE_RATE * xs


def transaction_fee_option_sell_put(d, xs):
    return TRANS_FEE_RATE * xs


transaction_fee = EvaluationFuncDispatcher(dict(
    buy_call=transaction_fee_option_buy_call,
    sell_call=transaction_fee_option_sell_call,
    buy_put=transaction_fee_option_buy_put,
    sell_put=transaction_fee_option_sell_put,
))
