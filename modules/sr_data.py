import requests
import os
import time
import json
import importlib
import traceback
import wikipedia
import multiprocessing
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz


class PluginStart:
	def __init__(self, front=None, plName=None, qtLogs=None, qtProgress=None):
		self.front = front
		self.plName = plName
		self.qtLogs = qtLogs
		self.multi_logs = multiprocessing.Queue()
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
							PL_DATA = plugin.Main(interface=self.front, cookies=cookies, logs=self.multi_logs)
						except:
							PL_DATA = plugin.Main(interface=self.front, logs=self.multi_logs)

						yield [pl_name, PL_DATA]

			except:
				pass

	def search_data(self, subject=None, klass=None, q=None, storinka=(1, 2), proxy=None):
		list_urls = {}
		pl_num = 4
		results = 0
		try:
			for Main in self.load_info():
				try:
					if Main[1]:
						# data = Main[1].search()
						data = None
						load_pr = multiprocessing.Process(target=Main[1].search, args=(q, subject, klass, storinka, proxy,))
						load_pr.start()

						while load_pr.is_alive() or not self.multi_logs.empty():
							if not self.multi_logs.empty():
								msg = self.multi_logs.get()
								if msg["type"] == "logs":
									self.qtLogs.emit(msg["level"], msg["source"], msg["data"])
								elif msg["type"] == "data": data = msg["data"]
						load_pr.join()

						list_urls[Main[0]] = data
						pl_num += 1
						results += len(data)
				except Exception as e:
					pass
		except:
			pass
		return list_urls, pl_num, results

	def processing_data(self, q=None, index_session=0, list_urls=None, proxy=None):
		temp_json = []
		for Main in self.load_info():
			try:
				if Main[1]:
					data = None
					load_pr = multiprocessing.Process(target=Main[1].processing_data, args=(list_urls[Main[0]], proxy,))
					load_pr.start()

					while load_pr.is_alive() or not self.multi_logs.empty():
						if not self.multi_logs.empty():
							msg = self.multi_logs.get()
							if msg["type"] == "logs": self.qtLogs.emit(msg["level"], msg["source"], msg["data"])
							elif msg["type"] == "data": data = msg["data"]

					load_pr.join()

					# data = Main[1].processing_data(urls=list_urls[Main[0]], proxy=proxy)

					if q:
						score = {
							"index": None,
							"text": None,
							"score": 0
						}
						for item in data:
							if item["name_test"]:
								fzz_0 = fuzz.WRatio(item["name_test"], q)
								if fzz_0 > score["score"]:
									score["index"] = [-1, -1]
									score["text"] = item["name_test"]
									score["score"] = fzz_0

								for index_answers, item_answers in enumerate(item["answers"]):
									if item_answers["text"]:
										fzz_1 = fuzz.WRatio(item_answers["text"], q)
										if fzz_1 > score["score"]:
											score["index"] = [index_answers, -1]
											score["text"] = item_answers["text"]
											score["score"] = fzz_1

										for index_value, item_value in enumerate(item_answers["value"]):
											if item_value["text"]:
												fzz_2 = fuzz.WRatio(item_value["text"], q)
												if fzz_2 > score["score"]:
													score["index"] = [index_answers, index_value]
													score["text"] = item_value["text"]
													score["score"] = fzz_2

							item["score"] = score
							temp_json.append(item)

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

	def wiki_data(self, q):
		try:
			img = None
			text = None
			title = None

			wikipedia.set_lang("ru")
			# results = wikipedia.search(q)

			text = wikipedia.summary(q, sentences=4)
			page = wikipedia.page(q)
			title = page.title

			if page.images:
			    img = page.images[-4]
			
			return title, text, img
		except BaseException as e:
			return None, None, None

if __name__ == "__main__":
	PluginStart().wiki_data(q="вулкан")