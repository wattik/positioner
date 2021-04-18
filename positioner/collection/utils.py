from typing import Union, AsyncGenerator, Iterator

async def a_collect(ait: Union[AsyncGenerator, Iterator]):
    r = []
    async for i in ait:
        r.append(i)
    return r
