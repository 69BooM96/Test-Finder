import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from time import perf_counter


def async_session(funk):
	async def wrapper(*agrs, **kwagrs):
		try:
			async with aiohttp.ClientSession(headers={"user-agent": UserAgent().random}, timeout=aiohttp.ClientTimeout(15)) as session:
				return await funk(session, *agrs, **kwagrs)
		except BaseException as ex: return ex
	return wrapper

class Load_data:
	def __init__(self, cookies=None):
		self.cookies = {item["name"]: item["value"] for item in cookies} if cookies else None

	def search(self, object="", klass=0, q="", storinka=(1,2), proxy=None):
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
				"utl": str(req.url),
				"name_test": soup.find(class_="h1-block h1-single").text,
				"object": soup.find_all(attrs={"itemprop": "name"})[1].text if len(soup.find_all(attrs={"itemprop": "name"})) >= 2 else None,
				"klass": soup.find_all(attrs={"itemprop": "name"})[2].text if len(soup.find_all(attrs={"itemprop": "name"})) >= 3 else None,
				"questions": int(soup.find(class_="block-head").text.split()[0]),

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

	def get_test(self, url: list, proxy=None):
		@async_session
		async def async_get_test(session: aiohttp.ClientSession, url):
			session.cookie_jar.update_cookies(self.cookies)
			async with session.get(url, proxy=proxy) as req:
				soup = BeautifulSoup(await req.text(), "lxml")
			
			data = {
				"_csrf": soup.find(attrs={"name": "csrf-token"}).get("content"),
				"Homework[name]": "Test-Finder",
				"Homework[deadline_day]": soup.find(id="homework-deadline_day").find_all("option")[3].get("value"),
				"Homework[deadline_hour]": "18:00",
				"Homework[shuffle_question]": "0",
				"Homework[shuffle_options]": [
					"0",
					"1"
				],
				"Homework[show_answer]": "0",
				"Homework[show_review]": [
					"0",
					"1"
				],
				"Homework[show_leaderbord]": [
					"0",
					"1"
				],
				"Homework[available_attempts]": "0",
				"Homework[duration]": "40",
				"Homework[show_timer]": "0",
				"Homework[show_flashcard]": "0",
				"Homework[show_match]": "0"
			}
			
			async with session.get(url, data=data, proxy=proxy) as req:
				soup = BeautifulSoup(await req.text(), "lxml")
			
			return soup.find(class_="form-control input-xs").get("value").split("=")[-1]

		async def run():
			task = [async_get_test(f"{url[:-5]}/set") for url in url]
			return await asyncio.gather(*task)

		return asyncio.run(run())
	
	def test_pass(self, gamecode: list, proxy=None):
		@async_session
		async def async_test_pass(session: aiohttp.ClientSession, gamecode):
			async with session.get("https://naurok.com.ua/test/join", proxy=proxy) as req:
				soup = BeautifulSoup(await req.text(), "lxml")

			data = {
				"_csrf": soup.find(attrs={"name": "csrf-token"}).get("content"),
				"JoinForm[gamecode]": gamecode,
				"JoinForm[name]": "Test-Finder"
			}
			
			async with session.post("https://naurok.com.ua/test/join", data=data, proxy=proxy) as req: 
				soup = BeautifulSoup(await req.text(), "lxml")
			
			session_id = soup.find(class_="{{test.font}}").get("ng-init").split(",")[1]

			async with session.get(f"https://naurok.com.ua/api2/test/sessions/{session_id}", proxy=proxy) as req:
				session_res = await req.json()

			data = {
				"answer": [
					session_res["questions"][0]["options"][0]["id"]
				],
				"homework": True,
				"homeworkType": 1,
				"point":  session_res["questions"][0]["point"],
				"question_id": session_res["questions"][0]["id"],
				"session_id": session_res["session"]["id"],
				"show_answer": session_res["settings"]["show_answer"],
				"type": session_res["questions"][0]["type"]
				}
			
			async with session.put("https://naurok.com.ua/api2/test/responses/answer", data=data) as req: await req.text()
			async with session.put(f"https://naurok.com.ua/api2/test/sessions/end/{session_id}") as req:
				uuid = await req.json()
				return "https://naurok.com.ua/test/complete/" + uuid["session"]["uuid"]
			
			
		async def run():
			task = [async_test_pass(gamecode) for gamecode in gamecode]
			return await asyncio.gather(*task)

		return asyncio.run(run())			


def main():
	list_object = [
				"/algebra", "/angliyska-mova", "/astronomiya", "/biologiya", "/vsesvitnya-istoriya", "/geografiya", "/geometriya",
				"/gromadyanska-osvita", "/ekologiya", "/ekonomika", "/etika", "/zarubizhna-literatura", "/zahist-vitchizni", "/informatika", 
				"/inshi-inozemni-movi", "/ispanska-mova", "/istoriya-ukra-ni", "/kreslennya", "/literaturne-chitannya", "/lyudina-i-svit", "/matematika", 
				"/mistectvo", "/movi-nacionalnih-menshin", "/muzichne-mistectvo", "/navchannya-gramoti", "/nimecka-mova", "/obrazotvorche-mistectvo", 
				"/osnovi-zdorov-ya", "/polska-mova", "/pravoznavstvo", "/prirodnichi-nauki", "/prirodoznavstvo", "/tehnologi", "/trudove-navchannya", 
				"/ukrainska-literatura", "/ukrainska-mova", "/fizika", "/fizichna-kultura", "/francuzka-mova", "/himiya", "/hudozhnya-kultura", "/ya-doslidzhuyu-svit"
				]
	start = perf_counter()
	naurok = Load_data()
	
	a = naurok.search(storinka=(1,4))
	b = naurok.processing_data(a)

	for index in range(len(b)):
		with open(f"temp_data/json/index_{index}.json", "w", encoding="utf-8") as file:
			json.dump(b[index], file, indent=4, ensure_ascii=False)
		
	print(perf_counter()-start)
if __name__ == "__main__":
	main()