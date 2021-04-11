import aiohttp

URL_BASE = "https://vapi.binance.com"


async def fetch(session: aiohttp.ClientSession, url, params=None):
    async with session.get(url, params=params, ssl=False) as response:
        assert response.status == 200
        return await response.json()


async def get_symbol_orderbook(session, symbol):
    data = await fetch(session, URL_BASE + "/vapi/v1/depth", params={"symbol": symbol, "limit": 1000})
    data = data.get("data", {})
    return {
        "asks": data.get("asks", []),
        "bids": data.get("bids", []),
        "symbol": symbol
    }


async def get_options_info(session):
    data = await fetch(session, URL_BASE + "/vapi/v1/optionInfo")
    return data.get("data", {})


async def get_index_price(session, underlying=None):
    underlying = underlying or "BTCUSDT"

    data = await fetch(session, URL_BASE + "/vapi/v1/index", params={"underlying": underlying})
    index_price = data.get("data", {})
    return index_price["indexPrice"]
