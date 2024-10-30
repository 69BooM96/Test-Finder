import asyncio 
import time
import json
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class Load_data():
	def __init__(self):
		super().__init__()
	
	def search_url(self, pages, text):
		self.url_list = []
		async def get_test(session, page, text):
			async with session.get("https://www.google.com/search", params={"q": text, "start": page * 10}) as req:
				soup = BeautifulSoup(await req.text(), "lxml")

			for item in soup.find_all(attrs={"jsname": "UWckNb"}):
				if item.get('href').startswith("https://naurok.com.ua/test/"):
					self.url_list.append(item.get('href'))
				print(item.get('href'))

		async def async_run():
			async with aiohttp.ClientSession(headers={"user-agent": UserAgent().random}) as session:
				task = [get_test(session, page, text=text) for page in range(pages)]
				await asyncio.gather(*task)
			
		
		start = time.perf_counter()
		asyncio.run(async_run())
		print(time.perf_counter()-start)
		return self.url_list
		

# a = Load_data().search_url(15, "на урок тест укр мова")
# print(a)

def data_info():
	return {"": ""}