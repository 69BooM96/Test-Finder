import requests
import os
import time
import json
import importlib
import traceback
from bs4 import BeautifulSoup

class PluginStart:
	def __init__(self, front=None, plName=None, qtLogs=None, qtProgress=None):
		self.front = front
		self.plName = plName
		self.qtLogs = qtLogs
		self.qtProgress = qtProgress
		self.progress_pl = 0
		self.progress_index = 0
		self.info_pl = []

	def load_info(self, type_pl=None, **kwargs):
		if self.plName: self.plugins_list = [self.plName]
		else: self.plugins_list = [name for name in os.listdir("plugins")]

		self.progress_pl = 42//len(self.plugins_list)
		self.progress_index = 0
		self.info_pl = []

		for pl_index, pl_name in enumerate(self.plugins_list):
			self.info_pl.append({"name": pl_name})
			self.progress_index += self.progress_pl
			if self.qtLogs: self.qtLogs.emit("INFO", f"Plugin", f" [{pl_index+1}]/[{len(self.plugins_list)}] [{pl_name}] [start]")
			if self.qtProgress: self.qtProgress.emit(self.progress_index)

			try:
				with open(f"plugins/{pl_name}/metadata.json", "r", encoding="utf-8") as metadata:
					mt_data = json.load(metadata)

				if mt_data['status'] == "works":
					if mt_data['type'] == "search":
						plugin = importlib.import_module(f"plugins.{pl_name}.{mt_data['file']}")
						try:
							with open(f"data/cookies/{pl_name}", "r", encoding="utf-8") as f:
								cookies=json.load(f)
							PL_DATA = plugin.Main(interface=self.front, cookies=cookies, logs=self.qtLogs)
						except:
							PL_DATA = plugin.Main(interface=self.front, logs=self.qtLogs)

						yield [pl_name, PL_DATA]

			except:
				traceback.print_exc()

	def search_data(self, subject=None, klass=None, q=None, storinka=(1, 2), proxy=None):
		list_urls = {}
		for Main in self.load_info():
			try:
				if Main[1]:
					data = Main[1].search(search_query=q, subject=subject, grade=klass, pagination=storinka, proxy=proxy)
					list_urls[Main[0]] = data
			except Exception as e:
				pass

		return list_urls

	def processing_data(self, index_session=0, list_urls=None, proxy=None):
		temp_json = []
		for Main in self.load_info():
			try:
				if Main[1]:
					temp_json += Main[1].processing_data(urls=list_urls[Main[0]], proxy=proxy)
			except Exception as e:
				pass

		with open(f"temp_data/json/index_{index_session}.json", "w", encoding="utf-8") as f:
			json.dump(temp_json, f, ensure_ascii=False, indent=4)
				
	def answers_data(self, index_session=None, index_json=None, list_urls=None, proxy=None):
		for Main in self.load_info():
			try:
				if Main[1]:
					with open(f"plugins/{Main[0]}/metadata.json", "r", encoding="utf-8") as file:
						url_req = json.load(file)

					for pl_info in url_req["data"]:
						if pl_info["type"] == "test":
							if list_urls.startswith(pl_info["url"]):
								with open(f"temp_data/json/index_{index_session}.json", "r", encoding="utf-8") as file:
									data_session_test = json.load(file)

								data_session_test[index_json]["answers"] = Main[1].get_answer(urls=[list_urls], proxy=proxy)[0]

								with open(f"temp_data/json/index_{index_session}.json", "w", encoding="utf-8") as f:
									json.dump(data_session_test, f, ensure_ascii=False, indent=4)

								break
			except Exception as e:
				traceback.print_exc()

	def create_data(self):
		...

	def wiki_data(self):
		try:
			req = requests.get("https://ru.wikipedia.org/wiki/Python")		
			soup = BeautifulSoup(req.text, "lxml")
			b = [
				soup.find(class_="mw-page-title-main").text,
				soup.find(class_="mw-content-ltr mw-parser-output").find("p").text.strip().replace("\xa0", ""),
				"https:"+str(soup.find("img", class_="mw-file-element").get("src") if soup.find("img", class_="mw-file-element") else None)
				]

			print(b)
		except BaseException as e:
			print(e)

if __name__ == "__main__":
	PluginStart().load_info(subject=1234, klass=24)