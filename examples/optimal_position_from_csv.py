from positioner import compute_strategy
from positioner.readers import read_order_book_from_csv, read_index_price_from_order_book

orderbook_csv = "args/orderbook_snapshot_210326.csv"
order_book = read_order_book_from_csv(orderbook_csv)
index_price = read_index_price_from_order_book(orderbook_csv)

solution = compute_strategy(
    order_book=order_book,
    index_price=index_price,
    budget=20,
    maximal_relative_loss=-0.1,  # maximal allowed loss is -100*BUDGET in USD,
    max_shift=1_000,  # profits are maximized in [index_price - max_shift, index_price + max_shift]
    loss_space_delta=0.5,
)

print("VAL:", solution.value)
print("ORD:", solution.orders)
