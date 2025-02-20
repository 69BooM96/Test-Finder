import asyncio
import aiohttp
import aiofiles
from modules.decorate import async_session
from time import perf_counter


def load_img(url_list: list, queue, proxy=None):
    @async_session(None)
    async def dowload(session: aiohttp.ClientSession, url, image_name):
        async with session.get(url, proxy=proxy) as req:
            async with aiofiles.open(file=f"temp_data/imgs/{image_name}", mode="wb") as file:
                async for chunk in req.content.iter_chunked(65536):
                    await file.write(chunk)

            queue.put({"level": "info", "source": "Img_load", "data": f" [{req.status}] [{url}]"})
    
    async def run():
        task = [dowload(url, (url.split("/")[-1])) for index, url in enumerate(url_list)]
        return await asyncio.gather(*task)
    
    return asyncio.run(run())