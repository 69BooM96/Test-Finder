import requests

import os
import time
import json
import importlib
import threading
import Core

from bs4 import BeautifulSoup


def plugin_data(self, subject=None, klass=None, q=None, storinka=(1, 2), proxy=None, qtLogs=True):
	self.log_signal.emit("INFO", f"Start_search", f" [Text][{self.mainwindows.text_search}]")
	self.progress_signal.emit(2)
	big_start_time = time.perf_counter()
	plugins_list = [name for name in os.listdir("plugins")]

	progress_pl = (42//len(plugins_list))

	for pl_index, pl_name in enumerate(plugins_list, start=1):
		self.progress_index += progress_pl
		self.log_signal.emit("INFO", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [start]")
		self.progress_signal.emit(self.progress_index)
		start_time = time.perf_counter()
		try:
			urls_lists = []
			with open(f"plugins/{pl_name}/metadata.json") as metadata:
				mt_data = json.load(metadata)

			if mt_data['status'] == "works":
				if mt_data['type'] == "search":
					plugin = importlib.import_module(f"plugins.{pl_name}.{mt_data['file']}")
					data_info_pl = plugin.data_info()

					args_pl = {}

					if data_info_pl['search']['subject'][0] and subject:   args_pl["subject"]= subject
					if data_info_pl['search']['klass'][0] and klass:       args_pl["klass"]= klass
					if data_info_pl['search']['q'][0] and q:               args_pl["q"]= q
					if data_info_pl['search']['storinka'][0] and storinka: args_pl["storinka"]= storinka
					if data_info_pl['search']['proxy'][0] and proxy:       args_pl["proxy"]= proxy
					if data_info_pl['qt_logs'][0] and qtLogs:			   args_pl["qt_logs"]= self.log_signal

					if data_info_pl['search']['subject'][1] and not subject: pass
					elif data_info_pl['search']['klass'][1] and not klass: pass
					elif data_info_pl['search']['q'][1] and not q: pass
					elif data_info_pl['search']['storinka'][1] and not storinka: pass
					elif data_info_pl['search']['proxy'][1] and not proxy: pass
					elif data_info_pl['qt_logs'][1] and qtLogs: pass
					else:
						if data_info_pl['search']['cookie'][0]:
							session_pl = plugin.Load_data(json.load(open(f"data/cookies/{pl_name}", "r")))
							
							urls_lists = session_pl.search(**args_pl)
							self.urls_data_list = list(dict.fromkeys(self.urls_data_list + urls_lists))
						else:
							session_pl = plugin.Load_data()
							urls_lists = session_pl.search(**args_pl)
							self.urls_data_list = list(dict.fromkeys(self.urls_data_list + urls_lists))

				elif mt_data['type'] == "search_engine":
					...

			self.platforms_num += 1
			self.log_signal.emit("INFO", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [results][{len(urls_lists)}] [endTime][{time.perf_counter() - start_time:.02f}]s")
		except Exception as e:
			self.log_signal.emit("ERROR", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [{e}]")
	self.log_signal.emit("INFO", f"Stop_search", f" [results][{len(self.urls_data_list)}] [endTime][{time.perf_counter() - big_start_time:.02f}]s")
	self.urls_data_list = self.urls_data_list

def plugin_processing_data(self, index_session=None, list_urls=None, proxy=None, qtLogs=True):
	self.log_signal.emit("INFO", f"Start_load", f" [urls][{len(list_urls)}]")
	self.progress_signal.emit(46)
	big_start_time = time.perf_counter()
	plugins_list = [name for name in os.listdir("plugins")]
	dict_num = 0
	self.urls_data_list = []
	temp_json = []

	progress_pl = (42//len(plugins_list))
	for pl_index, pl_name in enumerate(plugins_list, start=1):
		self.progress_index += progress_pl
		self.progress_signal.emit(self.progress_index)
		self.log_signal.emit("INFO", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [start]")
		start_time = time.perf_counter()
		try:
			urls_lists = []
			with open(f"plugins/{pl_name}/metadata.json") as metadata:
				mt_data = json.load(metadata)

			if mt_data['status'] == "works":
				if mt_data['type'] == "search":
					dict_data = []
					plugin = importlib.import_module(f"plugins.{pl_name}.{mt_data['file']}")
					data_info_pl = plugin.data_info()
					args_pl = {}

					if data_info_pl['qt_logs'][0] and qtLogs: args_pl["qt_logs"]= self.log_signal
					if data_info_pl['qt_logs'][1] and qtLogs: pass
					else:
						if data_info_pl['processing_data']['cookie'][0]:
							session_pl = plugin.Load_data(json.load(open(f"data/cookies/{pl_name}", "r")))
							dict_data = session_pl.processing_data(url=list_urls, **args_pl)
						else:
							pl_load_data = plugin.Load_data()
							dict_data = pl_load_data.processing_data(url=list_urls, **args_pl)

					for index_item in range(len(dict_data)):
						test_data = dict_data[index_item]
						test_data["index_file"] = (index_item+dict_num)
						test_data["index_session"] = index_session

						temp_json.append(test_data)

					with open(f"temp_data/json/index_{index_session}.json", "w", encoding="utf-8") as session_set_sr_data:
						json.dump(temp_json, session_set_sr_data, ensure_ascii=False, indent=4)
					dict_num += len(dict_data)

			self.log_signal.emit("INFO", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [end][{time.perf_counter()-start_time:.02f}]s")
		except Exception as e:
			self.log_signal.emit("ERROR", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [error][{time.perf_counter()-start_time:.02f}]s [{e}]")
			
def plugin_answers_data(self, index_session=None, index_json=None, list_urls=None, proxy=None, qtLogs=True):
	self.log_signal.emit("INFO", f"Start_answers", f" [urls][{list_urls}]")
	big_start_time = time.perf_counter()
	plugins_list = [name for name in os.listdir("plugins")]
	dict_num = 0
	self.urls_data_list = []
	temp_json = []

	for pl_index, pl_name in enumerate(plugins_list, start=1):
		# self.progress_signal.emit(self.progress_index)
		
		start_time = time.perf_counter()
		try:
			urls_lists = []
			with open(f"plugins/{pl_name}/metadata.json") as metadata:
				mt_data = json.load(metadata)

			if mt_data['status'] == "works":
				if mt_data['type'] == "search":
					dict_data = []
					plugin = importlib.import_module(f"plugins.{pl_name}.{mt_data['file']}")
					data_info_pl = plugin.data_info()
					args_pl = {}

					if data_info_pl['answers']['url'][0] and list_urls: args_pl["url"] = [list_urls]
					if data_info_pl['answers']['proxy'][0] and proxy:   args_pl["proxy"] = proxy
					if data_info_pl['qt_logs'][0] and qtLogs:           args_pl["qt_logs"] = self.log_signal
					if data_info_pl['qt_logs'][1] and qtLogs: pass

					else:
						self.log_signal.emit("INFO", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [start]")
						if data_info_pl['answers']['cookie'][0]:
							session_pl = plugin.Load_data(json.load(open(f"data/cookies/{pl_name}", "r")))
							dict_data = session_pl.answers(**args_pl)
						else:
							pl_load_data = plugin.Load_data()
							dict_data = pl_load_data.answers(**args_pl)

						if dict_data:
							with open(f"temp_data/json/index_{index_session}.json", "r", encoding="utf-8") as file:
								data_session_test = json.load(file)

							data_session_test[index_json]["answers"] = dict_data[0]

							with open(f"temp_data/json/index_{index_session}.json", "w", encoding="utf-8") as session_set_sr_data:
								json.dump(data_session_test, session_set_sr_data, ensure_ascii=False, indent=4)
						self.log_signal.emit("INFO", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [end][{time.perf_counter()-start_time:.02f}]s")
		except Exception as e:
			self.log_signal.emit("ERROR", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [error][{time.perf_counter()-start_time:.02f}]s [{e}]")
			

def plugin_create_data(self):
	...


def wiki_data():
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
	wiki_data()