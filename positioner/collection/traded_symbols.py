import asyncio

import aiohttp

from positioner.collection.api import get_options_info
from positioner.orderbook import Symbol


async def a_collect_traded_option_symbols(expiry_date=None):
    async with aiohttp.ClientSession() as session:
        symbols = list(
            mi.get("symbol", "")
            for mi in await get_options_info(session)
        )

    # keep only symbols with expiry_date == date
    if expiry_date:
        symbols = [
            symbol
            for symbol in symbols
            if Symbol(symbol).expiry == expiry_date
        ]

    return symbols

def collect_traded_option_symbols(expiry_date=None):
    return asyncio.run(a_collect_traded_option_symbols(expiry_date=expiry_date))

def collect_traded_expiry_dates():
    symbols = set(
        Symbol(symbol).expiry
        for symbol in
        asyncio.run(a_collect_traded_option_symbols())
    )

    return list(symbols)
