import time

import numpy
import asyncio
import threading

import aiohttp
import multiprocessing

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class Load_img():
	def __init__(self):
		super().__init__()

class Load_data():
	def __init__(self):
		super().__init__()
	
	def search_url(self, pages, text="", subject="", klas="0"):
		self.url_list = []
		async def get_test(session, page, text=text, subject=subject, klas=klas):
			if subject != "": subject = f"/{subject}"

			async with session.get(f"https://naurok.com.ua/test{subject}/klas-{klas}/storinka-{page}?q={text}") as req:
				soup = BeautifulSoup(await req.text(), "lxml")
			for item in soup.find_all(class_="headline"):
				self.url_list.append("https://naurok.com.ua"+item.find("a").get("href"))

		async def async_run():
			async with aiohttp.ClientSession(headers={"user-agent": UserAgent().random}) as session:
				task = [get_test(session, page) for page in range(1, pages+1)]
				await asyncio.gather(*task)

				print(self.url_list) 
				

		start = time.perf_counter()
		asyncio.run(async_run())
		print(time.perf_counter()-start)

a = Load_data()
a.search_url(3, text="", subject="", klas="0")












class Main():
	def work(status):
		return status