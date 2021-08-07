import asyncio
import sys
import csv
from datetime import datetime
from positioner import compute_strategy
from positioner.collection.index_price import a_collect_index_price
from positioner.collection.orderbook import a_collect_traded_options
from positioner.collection.traded_symbols import a_collect_traded_option_symbols
from positioner.orderbook import read_order_book_from_dict, Symbol, group_trading_options_by_expiry_date
from utils import config
from watcher.notifier import Notifier

# api_key = config.default("binance", "api_key")
# api_secret = config.default("binance", "api_secret")
UNDERLYING = "BTCUSDT"


def write_csv(options: dict, index_price: float):
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
    path = "./outputs/" + dt_string + ".csv"
    with open(path, 'w', encoding='utf8', newline='') as csv_file:
        # write headers first (read it from first row)
        writer = csv.DictWriter(csv_file, fieldnames=[*options[0].keys(), 'index price'])
        writer.writeheader()

        # write all options
        for option in options:
            writer.writerow({**option, 'index price': index_price})


async def main():
    notifier = Notifier()
    while True:
        try:
            print('fetching all symbols...')
            symbols = await a_collect_traded_option_symbols()

            print('fetching trading options for all symbols...')
            options = await a_collect_traded_options(expiry_date=None, symbols=symbols)
            grouped_options = group_trading_options_by_expiry_date(options)

            # todo read this from the option and inside the for loop below? That depends if all options are within the one api call on Binance, but now they only offer BTCUSDT
            print('fetching index price for asset:', UNDERLYING)
            index_price = await a_collect_index_price(underlying=UNDERLYING)

            print('writing options to file...')
            write_csv(options, index_price)

            for expiry_date, options in grouped_options.items():
                print("Computing strategy for", expiry_date)
                # create order book from options
                order_book = read_order_book_from_dict(options)

                # compute strategy
                solution = compute_strategy(
                    order_book=order_book,
                    index_price=index_price,
                    budget=20,
                    maximal_relative_loss=-0.1,  # maximal allowed loss is -100*BUDGET in USD,
                    volatility=5_000
                )

                print("VAL:", solution.value)
                print("ORD:", solution.orders)

                # toggle bot listening
                alert_enabled = int(config.default("telegram", "alert_enabled")) > 0
                if alert_enabled:
                    if not notifier.is_running:
                        notifier.start_listening()
                else:
                    if notifier.is_running:
                        notifier.stop_listening()

                # if we found strategy average value above given threshold and alerts are enabled, send notification
                threshold = float(config.default("telegram", "alert_threshold"))
                if alert_enabled and solution.value > threshold:
                    print("Sending alert notification")
                    notifier.send_message("!Found profitable solution! Value: {0}\nOrders: {1}".format(solution.value, solution.orders))

            # pause the loop for 10 mins
            await asyncio.sleep(60 * 10)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            # pause the loop for 1 min and retry
            await asyncio.sleep(60)


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
