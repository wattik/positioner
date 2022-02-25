import datetime
from itertools import chain
from pathlib import Path
from time import sleep
from progressbar import progressbar

import pytz
from positioner.collection.index_price import collect_historical_index_prices


def chunkate(l, n):
    while l:
        yield l[:n]
        if n < len(l):
            l = l[n:]
        else:
            break


def main():
    path = Path("/Users/Wattik/Projekty/binance/data/options")
    symbol = "BTCUSDT"

    dts = []
    for csv_file in sorted(path.rglob("*.csv")):
        dt_str = csv_file.stem
        dt = datetime.datetime.strptime(dt_str, "%d-%m-%Y-%H-%M-%S")
        dt = dt.astimezone(pytz.timezone("Europe/Vienna"))
        dts += [dt]

    prices_chunks = []
    for dts_chunk in progressbar(list(chunkate(dts, 50))):
        prices = chain(collect_historical_index_prices(dts_chunk, symbol=symbol))
        sleep(1)
        prices_chunks += [prices]

    prices = list(chain.from_iterable(prices_chunks))

    with open("../data/options/prices.d", "w") as file:
        file.write(f"datetime,price\n")
        for price in prices:
            d_str = price["dt"].strftime("%d-%m-%Y-%H-%M-%S")
            p = price["index_price"]
            file.write(f"{d_str},{p}\n")

if __name__ == '__main__':
    main()
