import asyncio
from token import AWAIT

import aiohttp

import requests
from bs4 import BeautifulSoup

from fake_useragent import UserAgent

from modules.decorate import async_session


class Load_data:
    def __init__(self, cookies=None, qt_logs=None):
        self.qt_logs = qt_logs
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

        self.cookies = {item["name"]: item["value"] for item in cookies} if cookies else None

    def search(self, search_query, site, pagination=(1,11)):
        async def asearch(session: aiohttp.ClientSession, p):
            async with session.get(f"https://duckduckgo.com/?t=ffab&q=wtf", headers=self.header) as req: await req.text()

            data = {
                "q": "sho+site:https://naurok.com.ua/test",
                "s": "10",
                "nextParams": "",
                "v": "l",
                "o": "json",
                "dc": "11",
                "api": "d.js",
                "vqd": "4-244855595795416178407529030125838278229",
                "kl": "wt-wt"
            }

            print(data["q"])

            async with session.get("https://html.duckduckgo.com/html/", data=data) as req:
                soup = BeautifulSoup(await req.text(), "lxml")


        @async_session(headers=self.header)
        async def run(session):
            task = [asearch(session, p=p) for p in range(*pagination)]
            return await asyncio.gather(*task)

        return asyncio.run(run())


if __name__ == '__main__':
    d = Load_data()
    d.search("тарас", "https://naurok.com.ua/test/", pagination=(1,2))