# start of patch
# handle jupyter notebook issue with nested async loops
import nest_asyncio
import asyncio
if asyncio.get_event_loop().is_running():
    nest_asyncio.apply()
# end of patch
