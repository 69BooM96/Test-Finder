import importlib
import os
import time
import json
import threading
import Core

def plugin_data(self, subject=None, klass=None, q=None, storinka=(1, 2), proxy=None):
	self.log_signal.emit("INFO", f"Start_search", f" [Text][{self.mainwindows.text_search}]")
	big_start_time = time.perf_counter()
	plugins_list = [name for name in os.listdir("plugins")]
	self.urls_data_list = []

	for pl_index, pl_name in enumerate(plugins_list, start=1):
		self.log_signal.emit("INFO", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [start]")
		start_time = time.perf_counter()
		try:
			urls_lists = []
			with open(f"plugins/{pl_name}/metadata.json") as metadata:
				mt_data = json.load(metadata)

			if mt_data['status'] == "works":
				if mt_data['type'] == "search":
					plugin = importlib.import_module(f"plugins.{pl_name}.{mt_data['file']}")
					data_info_pl = plugin.data_info()

					#funk_start
					args_pl = {}

					if data_info_pl['search']['subject'][0] and subject:   args_pl["subject"]= subject
					if data_info_pl['search']['klass'][0] and klass:       args_pl["klass"]= klass
					if data_info_pl['search']['q'][0] and q:               args_pl["q"]= q
					if data_info_pl['search']['storinka'][0] and storinka: args_pl["storinka"]= storinka
					if data_info_pl['search']['proxy'][0] and proxy:       args_pl["proxy"]= proxy

					if data_info_pl['search']['subject'][1] == False and subject == None: pass
					elif data_info_pl['search']['klass'][1] == False and klass == None: pass
					elif data_info_pl['search']['q'][1] == False and q == None: pass
					elif data_info_pl['search']['storinka'][1] == False and storinka == None: pass
					elif data_info_pl['search']['proxy'][1] == False and proxy == None: pass
					else:
						if data_info_pl['search']['cookie'][0]:
							session_pl = plugin.Load_data(json.load(open(f"data/cookies/{pl_name}", "r")))
							urls_lists = session_pl.search(**args_pl)
							self.urls_data_list.append({"platform": pl_name, "urls": urls_lists})
						else:
							urls_lists = plugin.Load_data.search(self, **args_pl)
							self.urls_data_list.append({"platform": pl_name, "urls": urls_lists})

				elif mt_data['type'] == "search_engine":
					pass


			self.log_signal.emit("INFO", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [results][{len(urls_lists)}] [endTime][{time.perf_counter() - start_time:.02f}]s")
		except Exception as e:
			self.log_signal.emit("ERROR", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [{e}]")
	self.log_signal.emit("INFO", f"Stop_search", f" [endTime][{time.perf_counter() - big_start_time:.02f}]s")
	# print(list_data_urls)
	self.urls_data_list

def plugin_processing_data(self, index_session=None, list_urls=None, proxy=None):
	print(index_session, list_urls)
	self.log_signal.emit("INFO", f"Start_load", f" [urls][]")
	return 0