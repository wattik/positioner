from os import listdir
from os.path import isfile, join

from positioner import compute_strategy
from positioner.orderbook import group_trading_options_by_expiry_date, read_options_from_csv, read_order_book_from_dict
from utils import config

if __name__ == '__main__':
    outputs_path = "./outputs"
    files = [f for f in listdir(outputs_path) if isfile(join(outputs_path, f))]

    for csv_file in files:
        options = read_options_from_csv(join(outputs_path, csv_file))
        grouped_options = group_trading_options_by_expiry_date(options)

        # todo get index price by timestamp from API?

        for expiry_date, options in grouped_options.items():
            order_book = read_order_book_from_dict(options)
            solution = compute_strategy(
                order_book=order_book,
                index_price=index_price,
                budget=20,
                maximal_relative_loss=-0.1,  # maximal allowed loss is -100*BUDGET in USD,
                volatility=5_000
            )

        threshold = float(config.default("telegram", "alert_threshold"))
        if solution.value > threshold:
            print("Saving profitable solution to Mongo")

