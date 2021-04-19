import asyncio

import aiohttp

from positioner.collection.api import get_symbol_orderbook
from positioner.collection.traded_symbols import a_collect_traded_option_symbols
from positioner.collection.utils import a_collect


async def a_orderbook_to_options(order_book):
    for price, quantity in order_book["asks"]:
        yield {
            "side": "ASK",
            "price": price,
            "qnty": quantity,
            "symbol": order_book["symbol"]
        }

    for price, quantity in order_book["bids"]:
        yield {
            "side": "BID",
            "price": price,
            "qnty": quantity,
            "symbol": order_book["symbol"]
        }


async def a_collect_traded_options(expiry_date=None, symbols=None):
    if not symbols:
        symbols = await a_collect_traded_option_symbols(expiry_date=expiry_date)

    async with aiohttp.ClientSession() as session:
        # collect futures on the order books, for each symbol
        order_books = [
            get_symbol_orderbook(session, symbol)
            for symbol in symbols
        ]

        # as the futures get completed, extract trading offers from order books
        options = []
        for order_book in asyncio.as_completed(order_books):
            options += await a_collect(
                option
                async for option in a_orderbook_to_options(await order_book)
            )

    return options


def collect_traded_options(expiry_date=None, symbols=None):
    return asyncio.run(a_collect_traded_options(expiry_date=expiry_date, symbols=symbols))


if __name__ == '__main__':
    print(collect_traded_options(expiry_date="210416"))
