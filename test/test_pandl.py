
from positioner.pandl import transaction_fee, cost, order_margin, value
from positioner.components.order import Order
from positioner.components.option import Option

op = Option.make(3000.0, 1.0, "BID", "BTC-210409-90000-C")
order = Order.make(100.0, "SELL", op)

print(order)
print(op)

print(value(order, 80000.0))
print(cost(order, 80000))
print(transaction_fee(order, 80000))
print(order_margin(order, 80000))
