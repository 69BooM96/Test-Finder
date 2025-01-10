import asyncio
from token import AWAIT

import aiohttp
import json

from time import perf_counter

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from modules.decorate import async_session


class Load_data:
    def __init__(self):
        self.cookies = {
            "_EDGE_S": "F=1&SID=2A670F1EEE03698531411A70EF78685B&mkt=uk-ua&ui=ru-ru",
            "_EDGE_V": "1",
            "_HPVN": "CS=eyJQbiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiUCJ9LCJTYyI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiSCJ9LCJReiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiVCJ9LCJBcCI6dHJ1ZSwiTXV0ZSI6dHJ1ZSwiTGFkIjoiMjAyNS0wMS0wOVQwMDowMDowMFoiLCJJb3RkIjowLCJHd2IiOjAsIlRucyI6MCwiRGZ0IjpudWxsLCJNdnMiOjAsIkZsdCI6MCwiSW1wIjo2LCJUb2JuIjowfQ==",
            "_RwBf": "r=0&ilt=93&ihpd=0&ispd=10&rc=200&rb=0&gb=0&rg=200&pc=200&mtu=0&rbb=0&g=0&cid=&clo=0&v=10&l=2025-01-10T08:00:00.0000000Z&lft=2025-01-09T00:00:00.0000000-08:00&aof=0&ard=0001-01-01T00:00:00.0000000&rwdbt=0&rwflt=0&rwaul2=0&o=2&p=&c=&t=0&s=0001-01-01T00:00:00.0000000+00:00&ts=2025-01-10T10:01:30.4370673+00:00&rwred=0&wls=&wlb=&wle=&ccp=&cpt=&lka=0&lkt=0&aad=0&TH=",
            "_Rwho": "u=d&ts=2025-01-08",
            "_SS": "SID=2A670F1EEE03698531411A70EF78685B&R=200&RB=0&GB=0&RG=200&RP=200",
            "_UR": "QS=0&TQS=0&Pn=0",
            "ak_bmsc": "E60BF38B7230B10884227C4F10B35122~000000000000000000000000000000~YAAQZb17XEOf0EqUAQAAEDCmTxr7gKxtaRyhMSK8Lp5P867uUpaaftkMPRQYHRqpPsY4rx/qDJ4TRU7buI51DvRe9D/M0LeGWWYgFgXg/Su08nTW0Tja1j0047nBmkBDm1TOIgSGgNkSQn3YVcwdVTgGSatgnugKU0pT5tQFalxUkwR2UXU1rtjZ4kGpxuo7g3bzmDWxpeS/fsJM09611IxRynDjPLD4UwGV5wDeWTTh/GydiZfT9lsOVinGwqKc04mK+FqdPMFyibqsidrd8GifAP7K4dno6z6El+CDRfPpjBuSrBfOyUkJv+QcJD4UUEjVIShv6SvTV+ScGyjCW4J0axOr2jeltIXGYhkX1TMDKNXLpRlBRrbUKw64Bi64gdWlecqF9w==",
            "BFPRResults": "FirstPageUrls=84981E774AF2EA60C64B701DC94B3023,C12A08993BE8CB59B306B2C5DACFFB2A,D70C1DBCF9FAEC58E90BF21BB128AD1C,0AA9CB0BA678090420513A0A847990C6,3DAD99D0C4663AD86FE50734D6B08060,AF50338485AD8C02B68B8F823F94CB5D,49F99DA366BCDB96337A3AAA758F8903,C9BA756A05E6E69B73B41F503097049A,9F2D1C6AFC6C2D75E6B3C03DA3CB18E2,0E75A5B5954498ED82ADE52D9021C251&FPIG=B5B43E89D4DA4CF3935358E84387DA7D",
            "ipv6": "hit=1736506685226&t=4",
            "MMCASM": "ID=D66FE3B4F5A94EC89600CC8CEC1003A4",
            "MSPTC": "4Y0YeqUyXYrlJR2tzKpG1nrMSH398dLu1hfNoQhC3C4",
            "MUID": "3FA0F61A89EF693A1905E374889468EF",
            "MUIDB": "3FA0F61A89EF693A1905E374889468EF",
            "SRCHD": "AF=NOFORM",
            "SRCHHPGUSR": "SRCHLANG=ru&IG=31215D1920C84FE0813ACB14E35E959B&DM=1&BRW=XW&BRH=S&CW=1920&CH=428&SCW=1903&SCH=2630&DPR=1.0&UTC=120&EXLTT=32&HV=1736503292&WTS=63872099878&PRVCW=958&PRVCH=964&WEBTHEME=1",
            "SRCHUID": "V=2&GUID=F099B42A90B04FE989D1B0A2EEFC560B&dmnchg=1",
            "SRCHUSR": "DOB=20250108&T=1736503078000",
            "USRLOC": "HS=1&ELOC=LAT=48.52425765991211|LON=34.98271560668945|N=ÐÐ½ÐµÐ¿Ñ, ÐÐ½ÐµÐ¿ÑÐ¾Ð¿ÐµÑÑÐ¾Ð²ÑÐºÐ°Ñ Ð¾Ð±Ð»Ð°ÑÑÑ|ELT=4|"
        }

        @async_session(self.cookies)
        async def _(session):
            async with session.get("https://www.bing.com/search") as req: await req.text()
        asyncio.run(_())

    def search(self, q="", site="", storinka=(1, 2), proxy=None, qt_logs=None) -> list:
        @async_session(self.cookies)
        async def async_search(session: aiohttp.ClientSession, storinka=1):
            data = {
                "q": f"{q} site: {site}",
                "first": "21"
            }
            print()

            async with session.get("https://www.bing.com/search", params=data, proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            if qt_logs: qt_logs.emit("info", "Bing", f" [{req.status}] [{str(req.url)}]")

            return [obj.find("a").get("href") for obj in soup.find("ol", id="b_results").find_all("li", class_="b_algo")]

        async def run():
            tasks = [async_search(storinka=item) for item in range(*storinka)]
            return await asyncio.gather(*tasks)

        return [item2 for item in asyncio.run(run()) for item2 in item]


if __name__ == "__main__":
    bing = Load_data()
    results = bing.search("вулканизм", "https://naurok.com.ua/test/", storinka=(1,5))
    print(json.dumps(results, indent=4))




















































