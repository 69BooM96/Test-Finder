import requests
import os
import time
import json
import importlib
import traceback
import wikipedia
import multiprocessing
from bs4 import BeautifulSoup
from modules import sr_scan
from modules import toolset


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
		processes = []
		pl_num = 4
		results = 0
		try:
			for Main in self.load_info():
				try:
					if Main[1]:
						load_pr = multiprocessing.Process(target=Main[1].search, args=(q, subject, klass, storinka, proxy,))
						load_pr.daemon = True
						processes.append({"processes": load_pr, "name": Main[0]})
						load_pr.start()
				except Exception as e:
					pass

			for p in processes:
				try:
					data = None
					while p["processes"].is_alive() or not self.multi_logs.empty():
						if not self.multi_logs.empty():
							msg = self.multi_logs.get()
							if msg["type"] == "logs": self.qtLogs.emit(msg["level"], msg["source"], msg["data"])
							elif msg["type"] == "data": 
								data = msg["data"]
								list_urls[p["name"]] = data
								pl_num += 1
								results += len(data)
					p["processes"].join()
				except Exception as e:
					pass
		except:
			pass
		return list_urls, pl_num, results

	def processing_data(self, q=None, index_session=0, list_urls=None, proxy=None):
		processes = []
		data = None
		temp_json = []
		for Main in self.load_info():
			try:
				if Main[1]:
					load_pr = multiprocessing.Process(target=Main[1].processing_data, args=(list_urls[Main[0]], proxy,))
					load_pr.daemon = True
					processes.append({"processes": load_pr, "name": Main[0]})
					load_pr.start()
			except Exception as e:
				pass

		for p in processes:
			try:
				while p["processes"].is_alive() or not self.multi_logs.empty():
					if not self.multi_logs.empty():
						msg = self.multi_logs.get()
						if msg["type"] == "logs": self.qtLogs.emit(msg["level"], msg["source"], msg["data"])
						elif msg["type"] == "data": data = msg["data"]

				if q:
					scan_processes = []
					scan_pr_num = 2
					if len(data) > scan_pr_num: urls_scan = toolset.chunk_list(data, 2)
					else: urls_scan = [data]

					for index, item in enumerate(urls_scan):
						scan_session = sr_scan.Scan(multi=self.multi_logs, text=q, data=item)
						scan_pr = multiprocessing.Process(target=scan_session.tests, args=(True, True, True,))
						scan_pr.daemon = True
						scan_processes.append({"processes": scan_pr, "name": index})
						scan_pr.start()

					for scan_p in scan_processes:
						while scan_p["processes"].is_alive() or not self.multi_logs.empty():
							if not self.multi_logs.empty():
								msg = self.multi_logs.get()
								if msg["type"] == "scan": temp_json = temp_json+msg["data"]
								elif msg["type"] == "logs": self.qtLogs.emit(msg["level"], msg["source"], f"[{scan_p["name"]+1}]/[{len(scan_processes)}]{msg["data"]}")

						scan_p["processes"].join()

				p["processes"].join()
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
		# return None, None, None

if __name__ == "__main__":
	PluginStart().wiki_data(q="вулкан")