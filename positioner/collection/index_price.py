import asyncio
from collections.abc import Iterable
from datetime import datetime

import aiohttp

from positioner.collection.api import get_current_index_price, get_historical_index_price


async def a_collect_index_price(underlying=None):
    async with aiohttp.ClientSession() as session:
        return float(await get_current_index_price(session, underlying=underlying))


def collect_index_price(underlying=None):
    return asyncio.run(a_collect_index_price(underlying=underlying))


async def a_collect_historical_index_prices(dts: Iterable[datetime], symbol=None):
    async with aiohttp.ClientSession() as session:
        futures = [get_historical_index_price(session, dt, symbol=symbol) for dt in dts]

        prices = []
        for price in asyncio.as_completed(futures):
            price = await price
            prices += [price]

    return prices


def collect_historical_index_prices(datetimes: Iterable[datetime], symbol=None):
    return asyncio.run(a_collect_historical_index_prices(datetimes, symbol=symbol))


if __name__ == '__main__':
    dts = [datetime(2021, 5, 10), datetime(2021, 5, 11)]
    symbol = "BTCUSDT"
    print(collect_historical_index_prices(dts, symbol))