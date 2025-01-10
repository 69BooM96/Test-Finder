import asyncio 
import time
import json
import aiohttp

from bs4 import BeautifulSoup

from modules.decorate import async_session


class Load_data:
	def search_url(self, text, site="", end="", pages=(1,2)):
		@async_session(None)
		async def get_test(session: aiohttp.ClientSession, page, text):
			p = {
				"q": text + f"site: {site}" if site else "",
				"start": page * 10
			}
			async with session.get("https://www.google.com/search", params=p) as req:
				soup = BeautifulSoup(await req.text(), "lxml")

			print(soup)
			return [item.get('href') for item in soup.find_all(attrs={"jsname": "UWckNb"})]

		async def async_run():
			task = [get_test(page, text=text) for page in range(*pages)]
			return await asyncio.gather(*task)

		return [item2 for item in asyncio.run(async_run()) for item2 in item if item2.endswith(end) or not end]


def data_info():
	return {"": ""}

if __name__ == '__main__':
	start = time.perf_counter()
	google = Load_data()

	print(google.search_url("на урок вулканізм"))



	print(time.perf_counter()-start)











































