import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def async_session(funk):
	async def wrapper(*agrs, **kwagrs):
		async with aiohttp.ClientSession(headers={"user-agent": UserAgent().random}) as session:
			return await funk(session, *agrs, **kwagrs)
	return wrapper

class Load_data:
	list_object = [
					"/algebra", "/angliyska-mova", "/astronomiya", "/biologiya", "/vsesvitnya-istoriya", "/geografiya", "/geometriya",
					"/gromadyanska-osvita", "/ekologiya", "/ekonomika", "/etika", "/zarubizhna-literatura", "/zahist-vitchizni", "/informatika", 
					"/inshi-inozemni-movi", "/ispanska-mova", "/istoriya-ukra-ni", "/kreslennya", "/literaturne-chitannya", "/lyudina-i-svit", "/matematika", 
					"/mistectvo", "/movi-nacionalnih-menshin", "/muzichne-mistectvo", "/navchannya-gramoti", "/nimecka-mova", "/obrazotvorche-mistectvo", 
					"/osnovi-zdorov-ya", "/polska-mova", "/pravoznavstvo", "/prirodnichi-nauki", "/prirodoznavstvo", "/tehnologi", "/trudove-navchannya", 
					"/ukrainska-literatura", "/ukrainska-mova", "/fizika", "/fizichna-kultura", "/francuzka-mova", "/himiya", "/hudozhnya-kultura", "/ya-doslidzhuyu-svit"
					]
	
	def search(self, object="", klass=0, q="", storinka=(1,11), proxy=None):
		@async_session
		async def async_search(session: aiohttp.ClientSession, storinka=1):
			async with session.get(f"https://naurok.com.ua/test{object}/klas-{klass}?q={q}&storinka={storinka}", proxy=proxy) as req:
				soup = BeautifulSoup(await req.text(), "lxml")
		
			return ["https://naurok.com.ua" + obj.find("a").get("href") for obj in soup.find_all(class_="headline")]
		
		async def run():
			task = [async_search(storinka=item) for item in range(*storinka)]
			return await asyncio.gather(*task)
		
		return sum(asyncio.run(run()), [])

	def processing_data(self, url: list, proxy=None):
		@async_session
		async def async_processing_data(session: aiohttp.ClientSession, url):
			async with session.get(url, proxy=proxy) as req:
				soup = BeautifulSoup(await req.text(), "lxml")
			
			return {
				"platform": "naurok",
				"name_test": soup.find(class_="h1-block h1-single").text,
				"object": soup.find_all(attrs={"itemprop": "name"})[1].text,
				"klass": soup.find_all(attrs={"itemprop": "name"})[2].text,
				"questions": soup.find(class_="block-head").text.split()[0],

				"answers": [{
					"type": "quiz" if obj.find(class_="option-marker quiz") else "multiquiz",
					"text": obj.find(class_="question-view-item-content").text.strip().replace(" ", "") if obj.find(class_="question-view-item-content") else None,
					"img": obj.find(class_="question-view-item-image").get("src") if obj.find(class_="question-view-item-image") else None,
					"value": [{
						"text": item.find("p").text.strip().replace(" ", "") if item.find("p") else None,
						"img": item.find("img").get("src") if item.find("img") else None
					} for item in obj.select('.question-options > div')]
					} for obj in soup.find(class_="col-md-9 col-sm-8").find_all(class_="content-block entry-item question-view-item")]
			}
		
		async def run():
			task = [async_processing_data(url=item) for item in url]
			return await asyncio.gather(*task)

		return asyncio.run(run())

def main():
	naurok = Load_data()

	b = naurok.processing_data(["https://naurok.com.ua/test/olimpiada-mova-i-literatura-11-klas-3054071.html"])
	print(b)
	with open("temp_data/json/index_1.json", "w", encoding="utf-8") as file:
		json.dump(b, file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
	main()