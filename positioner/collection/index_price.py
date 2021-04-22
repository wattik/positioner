import asyncio

import aiohttp

from positioner.collection.api import get_index_price


async def a_collect_index_price(underlying=None):
    async with aiohttp.ClientSession() as session:
        return float(await get_index_price(session, underlying=underlying))


def collect_index_price(underlying=None):
    return asyncio.run(a_collect_index_price(underlying=underlying))
