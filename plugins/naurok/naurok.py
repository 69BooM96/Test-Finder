import time

import json

import numpy
import asyncio
import threading

import aiohttp
import multiprocessing

from bs4 import BeautifulSoup
from fake_useragent import UserAgent


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Load_img():
	def __init__(self):
		super().__init__()

class Load_data():
	def __init__(self):
		super().__init__()
	
	def search_url(self, pages, text="", subject=1, klas=0, prox=None):
		self.url_list = []
		self.list_subject = ["/algebra", "/angliyska-mova", "/astronomiya", "/biologiya", "/vsesvitnya-istoriya", "/geografiya", "/geometriya",
						"/gromadyanska-osvita", "/ekologiya", "/ekonomika", "/etika", "/zarubizhna-literatura", "/zahist-vitchizni", "/informatika", 
						"/inshi-inozemni-movi", "/ispanska-mova", "/istoriya-ukra-ni", "/kreslennya", "/literaturne-chitannya", "/lyudina-i-svit", "/matematika", 
						"/mistectvo", "/movi-nacionalnih-menshin", "/muzichne-mistectvo", "/navchannya-gramoti", "/nimecka-mova", "/obrazotvorche-mistectvo", 
						"/osnovi-zdorov-ya", "/polska-mova", "/pravoznavstvo", "/prirodnichi-nauki", "/prirodoznavstvo", "/tehnologi", "/trudove-navchannya", 
						"/ukrainska-literatura", "/ukrainska-mova", "/fizika", "/fizichna-kultura", "/francuzka-mova", "/himiya", "/hudozhnya-kultura", "/ya-doslidzhuyu-svit"]
		async def get_test(session, page, text=text, subject=subject, klas=klas):
			subject = self.list_subject[subject-1] if subject != 0 else ""

			async with session.get(f"https://naurok.com.ua/test{subject}/klas-{klas}/storinka-{page}?q={text}", proxy=prox) as req:
				soup = BeautifulSoup(await req.text(), "lxml")
				print(req.url)
			for item in soup.find_all(class_="headline"):
				self.url_list.append("https://naurok.com.ua"+item.find("a").get("href"))

		async def async_run():
			async with aiohttp.ClientSession(headers={"user-agent": UserAgent().random}) as session:
				task = [get_test(session, page) for page in range(1, pages+1)]
				await asyncio.gather(*task)
		
		start = time.perf_counter()
		asyncio.run(async_run())
		print(time.perf_counter()-start)
		return self.url_list
	
	def load_test(self, index_, url_list):
		self.index = index_
		async def get_test(session, url):
			async with session.get(url) as req:
				soup = BeautifulSoup(await req.text(), "lxml")
			data = [{"INFO":{"type": "test",
							"resp_code": req.status,
							"name": soup.find_all(itemprop="name")[1].text,
							"class": soup.find_all(itemprop="name")[2].text,
							"questions": len(soup.find_all(class_="content-block entry-item question-view-item")),
							"url": url,
							"platform": "naurok",
							"answers": "None"}}]

			for index, sp in enumerate(soup.find_all(class_="content-block entry-item question-view-item")):
				text = sp.find(class_="question-view-item-content")
				if text:
					text = text.text.replace(" ", " ").rstrip().lstrip()
					if text[0] == " ": text = text[1:]
					if text[-1] == " ": text = text[:-1]
				else: text = "None"
				
				img = sp.find(class_="question-view-item-content").find("img")
				if img:
					img = img.get("src")
				else: img = "None"

				data.append({"type": "quiz" if sp.find(class_="option-marker quiz") else "multiquiz",
							"num": index,
							"text": text,
							"img": img,
							"answers": [{"text": item.text.replace(" ", " ").rstrip().lstrip() if item else "None",
										 "img": item.get("src") if item else "None"}
										 for item in sp.find_all(class_=["option-text", "option-image"])]
							})
			
			self.index += 1
			
			with open(f"temp_data/json/index_{self.index}.json", "w", encoding="utf-8") as file:
				json.dump(data, file, indent=4, ensure_ascii=False)

		async def async_run():
			async with aiohttp.ClientSession(headers={"user-agent": UserAgent().random}) as session:
				task = [get_test(session, url) for url in url_list]
				await asyncio.gather(*task)

		start = time.perf_counter()
		asyncio.run(async_run())
		print(time.perf_counter()-start)






class Main():
	def work(status):
		return status