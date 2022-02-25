import aiohttp
from datetime import datetime

OPTION_URL_BASE = "https://vapi.binance.com"
SPOT_URL_BASE = "https://api.binance.com"


async def fetch(session: aiohttp.ClientSession, url, params=None):
    async with session.get(url, params=params, ssl=False) as response:
        assert response.status == 200, response.status
        return await response.json()


async def get_symbol_orderbook(session, symbol):
    data = await fetch(session, OPTION_URL_BASE + "/vapi/v1/depth", params={"symbol": symbol, "limit": 1000})
    data = data.get("args", {})
    return {
        "asks": data.get("asks", []),
        "bids": data.get("bids", []),
        "symbol": symbol
    }


async def get_options_info(session):
    data = await fetch(session, OPTION_URL_BASE + "/vapi/v1/optionInfo")
    return data.get("args", {})


async def get_current_index_price(session, underlying=None):
    underlying = underlying or "BTCUSDT"

    data = await fetch(session, OPTION_URL_BASE + "/vapi/v1/index", params={"underlying": underlying})
    return data["data"]["indexPrice"]
    # print("INDEX PRICE", data["data"]["indexPrice"])
    # index_price = data.get("args", {})
    # return index_price["indexPrice"]


"""
With precision to 1 minute, computes approximate historical symbol price at `time`. 
"""


async def get_historical_index_price(session, dt: datetime, symbol=None):
    params = dict(
        symbol=symbol or "BTCUSDT",
        interval="1m",
        startTime=int(dt.timestamp() * 1000),
        limit=1
    )
    data = await fetch(session, SPOT_URL_BASE + "/api/v3/klines", params=params)
    index_price = data[0][1]
    return {"dt": dt, "index_price": float(index_price)}
