import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from time import perf_counter
from pprint import pprint

from modules.decorate import async_session

class Load_data:
    def __init__(self, cookies=None):
        self.cookies = {item["name"]: item["value"] for item in cookies} if cookies else None

    def search(self, s="", types="", cat="", is_pay="", page=(1, 2), sort="", klass="", title_only="", proxy=None, qt_logs=None) -> list:
        @async_session(self.cookies)
        async def async_search(session: aiohttp.ClientSession, page=1):
            async with session.get(f"https://vseosvita.ua/test?s={s}&type={types}&cat={cat}&is_pay={is_pay}&page={page}&sort={sort}&class={klass}&title_only={title_only}&=", proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            if qt_logs: qt_logs.emit("info", f"Vseosvita", f" [{req.status}] [{str(req.url)}]")
            
            return [obj.find("a").get("href") for obj in soup.find_all(class_="lib-item")]
        
        async def run():
            task = [async_search(page=item) for item in range(*page)]
            return await asyncio.gather(*task)
        
        return set(item2 for item in asyncio.run(run()) for item2 in item)

    def processing_data(self, url: list, proxy=None, qt_logs=None) -> list[dict]:
        @async_session(self.cookies)
        async def async_processing_data(session: aiohttp.ClientSession, url):
            async with session.get(url, proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")
                
            if qt_logs: qt_logs.emit("info", f"Vseosvita", f" [{req.status}] [{str(req.url)}]")

            return {
                "platform": "vseosvita",
                "type_data": "test",
                "url": str(req.url),
                "name_test": soup.find(class_="lib-inside-title").find("h1").text.strip(),
                "object": soup.find_all(class_="lib-inside-text")[0].text.strip(),
                "klass": soup.find_all(class_="lib-inside-text")[1].text.strip(),

                "answers": [{
                    "type": None,
                    "text": obj.find(class_="v-test-questions-title").text.strip() if obj.find(class_="v-test-questions-title") else None,
                    "img": obj.find("img").get("src") if obj.find("img") else None,
                    "value": [{
                        "text": obj.find("p").text.strip()  if obj.find("p") else None,
                        "img": obj.find("img").get("src") if obj.find("img") else None,
                        "correctness": None
                        } for obj in soup.find(class_="list-view").find_all("vr-quest")[1:]]
                } for obj in soup.find(class_="list-view").find_all(class_="question-block_body")]
            }
        #lib-inside__question-block
        
        async def run():
            task = [async_processing_data(url) for url in url if url if url[:26] == "https://vseosvita.ua/test/"]
            return await asyncio.gather(*task)

        return asyncio.run(run())
    

def main():
    start = perf_counter()
     
    vseosvita = Load_data()
     
    a = vseosvita.processing_data(["https://vseosvita.ua/test/mitoz-meioz-3898072.html"])
    pprint(a)

    print(perf_counter()-start)
    
if __name__ == "__main__":
    main()