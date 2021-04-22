from positioner import compute_strategy
from positioner.orderbook import read_order_book_from_dict

from positioner.collection.orderbook import collect_traded_options
from positioner.collection.index_price import collect_index_price

EXPIRY_DATE = "210528"
UNDERLYING = "BTCUSDT"

current_orderbook = collect_traded_options(expiry_date=EXPIRY_DATE)
order_book = read_order_book_from_dict(current_orderbook)
index_price = collect_index_price(underlying=UNDERLYING)

solution = compute_strategy(
    order_book=order_book,
    index_price=index_price,
    budget=20,
    maximal_relative_loss=-0.1,  # maximal allowed loss is -100*BUDGET in USD,
    max_shift=10_000  # profits are maximized in [index_price - max_shift, index_price + max_shift]
)

print("VAL:", solution.value)
print("ORD:", solution.orders)
