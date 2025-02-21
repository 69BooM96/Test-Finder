import asyncio
import urllib.parse

import aiohttp

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from modules.decorate import async_session
from modules.plugin_param import *

class Load_data:
    def __init__(self, logs=None, cookies=None):
        self.header = {
            "Host": "html.duckduckgo.com",
            "User-Agent": UserAgent().random,
            "Accept-Encoding": "gzip, deflate, zstd",
            "DNT": "1",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "Priority": "u=0, i",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }
        self.logs = logs

    def search(self, search_query, site, pagination=(1,11), proxy=None):
        async def asearch(session: aiohttp.ClientSession, p):
            # async with session.get(f"https://duckduckgo.com/?t=ffab&q={search_query}") as req: await req.text()
            async with session.get(f"https://html.duckduckgo.com/html?q={search_query}+site:{site}&s={p}", proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            if self.logs: self.logs.emit("info", f"duckduckgo", f" [{req.status}] [{str(req.url)}]")

            # with open("f.html", "w", encoding="utf-8") as file:
            #     file.write(str(soup))

            res = soup.find_all("a", class_="result__a")
            res_list = []
            for item in res:
                if item.get("href").startswith("//duckduckgo.com/l/?"):
                    res_list.append(urllib.parse.unquote(item.get("href")[25:].split("&rut=")[0]))

                else:
                    res_list.append(item.get("href"))

            return res_list

        @async_session(headers=self.header)
        async def run(session):
            task = [asearch(session, p=p) for p in range(*pagination)]
            return await asyncio.gather(*task)

        return [item2 for item in asyncio.run(run()) for item2 in item]

class Main(Searcher):
    def __init__(self, interface, logs=None, cookies=None):
        super().__init__(interface=interface, logs=logs, cookies=cookies)
        self.duckduckgo = Load_data(logs=logs, cookies=cookies)

    def search(self, search_query, site, pagination=(1,3), proxy=None):
        return self.duckduckgo.search(
            search_query=search_query,
            site=site,
            proxy=proxy
        )


if __name__ == '__main__':
    d = Main(None)

    print(d.search("тарас", "https://naurok.com.ua/test/", pagination=(1,2)))