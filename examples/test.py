from positioner import compute_strategy
from positioner.index_price import read_index_price_from_order_book
from positioner.orderbook import read_order_book

orderbook_csv = "examples/orderbook_snapshot_210409.csv"

order_book = read_order_book(orderbook_csv)
index_price = read_index_price_from_order_book(orderbook_csv)


solution = compute_strategy(
    order_book=order_book,
    index_price=index_price,
    budget=20,
    maximal_relative_loss=-100,  # maximal allowed loss is -100*BUDGET in USD
)

print("VAL:", solution.value)
print("ORD:", solution.orders)
