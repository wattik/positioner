from positioner.components.option import Option
from positioner.components.order import Order
from positioner.functional.order import squeeze_orders_to_options


def test_squeeze_orders_to_options():
    orders = [
        Order.parse("BUY 2000USD BTC-210528-75000-P-ASK at 1000.000USD"),
        Order.parse("BUY 200USD BTC-210528-75000-P-ASK at 100.000USD"),
        Order.parse("BUY 1000USD BTC-210528-75000-P-ASK at 1000.000USD"),
        Order.parse("BUY 100USD BTC-210528-75000-P-ASK at 100.000USD"),
        Order.parse("BUY 2000USD BTC-210528-75000-C-ASK at 1000.000USD"),
        Order.parse("BUY 200USD BTC-210528-75000-C-ASK at 100.000USD"),
        Order.parse("BUY 1000USD BTC-210528-75000-C-ASK at 1000.000USD"),
        Order.parse("BUY 100USD BTC-210528-75000-C-ASK at 100.000USD"),
    ]

    options = squeeze_orders_to_options(orders)

    expected = [
        Option.make(550, 6, "ASK", "BTC-210528-75000-P"),
        Option.make(550, 6, "ASK", "BTC-210528-75000-C")
    ]

    assert expected == options
