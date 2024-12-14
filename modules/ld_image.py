import asyncio
import aiohttp
import aiofiles

from modules.decorate import async_session

from time import perf_counter

def load(url_list: list, proxy=None):
    @async_session(None)
    async def dowload(session: aiohttp.ClientSession, url, image_name):
        async with session.get(url, proxy=proxy) as req:
            async with aiofiles.open(file=f"temp_data/imgs/{image_name}.png", mode="wb") as file:
                async for chunk in req.content.iter_chunked(65536):
                    await file.write(chunk)

    async def run():
        task = [dowload(url, index) for index, url in enumerate(url_list)]
        return await asyncio.gather(*task)
    
    return asyncio.run(run())

start = perf_counter()
load(["https://naurok-test2.nyc3.digitaloceanspaces.com/112070/images/576215_1604903414.jpg"]*50)

print(perf_counter()-start)