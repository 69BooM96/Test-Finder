import asyncio
import aiohttp
import aiofiles

from modules.decorate import async_session
from time import perf_counter
from pathlib import Path


def load_img(url_list: list, queue, replace_img=False, proxy=None):
    @async_session(None)
    async def dowload(session: aiohttp.ClientSession, url, image_name):
        req_status = 304
        if replace_img or not Path(f"temp_data/imgs/{image_name}").is_file():
            async with session.get(url, proxy=proxy) as req:
                async with aiofiles.open(file=f"temp_data/imgs/{image_name}", mode="wb") as file:
                    async for chunk in req.content.iter_chunked(65536):
                        await file.write(chunk)
            req_status = req.status

        queue.put({"level": "info", "source": "Img_load", "data": f" [{req_status}] [{url}]"})
    
    async def run():
        task = [dowload(url, (url.split("/")[-1])) for index, url in enumerate(url_list)]
        return await asyncio.gather(*task)
    
    return asyncio.run(run())