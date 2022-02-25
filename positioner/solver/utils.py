from positioner.components.order import Order, OrderType


def divide_orders_by_side(orders: list[Order]):
    buys = [o for o in orders if o.order_type == OrderType.BUY]
    sells = [o for o in orders if o.order_type == OrderType.SELL]
    return buys, sells
