import asyncio
import sys

from positioner import compute_strategy
from positioner.collection.index_price import a_collect_index_price
from positioner.collection.orderbook import a_collect_traded_options
from positioner.collection.traded_symbols import a_collect_traded_option_symbols
from positioner.orderbook import read_order_book_from_dict, Symbol
from utils import config
from watcher.notifier import Notifier

api_key = config.default("binance", "api_key")
api_secret = config.default("binance", "api_secret")
UNDERLYING = "BTCUSDT"


def filter_expiry_dates(symbols: list[str]) -> list[str]:
    symbols = set(
        Symbol(symbol).expiry
        for symbol in
        symbols
    )

    return list(symbols)


async def main():
    notifier = Notifier()
    while True:
        try:
            print('fetching all available symbols and filtering expiry dates')
            all_symbols = await a_collect_traded_option_symbols()
            expiry_dates = filter_expiry_dates(all_symbols)

            for expiry_date in expiry_dates:
                print("Expiry date", expiry_date)
                current_order_book = await a_collect_traded_options(expiry_date=expiry_date)
                order_book = read_order_book_from_dict(current_order_book)
                # todo save order book to file
                index_price = await a_collect_index_price(underlying=UNDERLYING)

                print("Order book", order_book, "index price", index_price)
                solution = compute_strategy(
                    order_book=order_book,
                    index_price=index_price,
                    budget=20,
                    maximal_relative_loss=-0.1,  # maximal allowed loss is -100*BUDGET in USD,
                    volatility=5_000
                )

                print("VAL:", solution.value)
                print("ORD:", solution.orders)

                threshold = float(config.default("telegram", "alert_threshold"))
                if solution.value > threshold:
                    # send notification
                    notifier.send_message("!Found profitable solution! Value: {0}\nOrders: {1}".format(solution.value, solution.orders))
        except:
            print("Unexpected error:", sys.exc_info()[0])

        # pause the loop for N mins
        await asyncio.sleep(60 * 5)

# https://tutorialedge.net/python/concurrency/asyncio-event-loops-tutorial/
loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(main())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    print("Closing Loop")
    loop.close()
