import asyncio

import aiohttp

from positioner.collection.api import get_index_price


async def a_collect_index_price(underlying=None):
    async with aiohttp.ClientSession() as session:
        return await get_index_price(session, underlying=underlying)


def collect_index_price(underlying=None):
    return float(asyncio.run(a_collect_index_price(underlying=underlying)))
