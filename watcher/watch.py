import asyncio
from utils import config

api_key = config.default("binance", "api_key")
api_secret = config.default("binance", "api_secret")


async def main():
    print('hello')
    await asyncio.sleep(5)
    await main()


asyncio.run(main())
