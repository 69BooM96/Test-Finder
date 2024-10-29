import importlib
import os
import time
import json
import threading
import Core

def plugin_data(self, objects=None, klass=None, q="hello", storinka=(1, 2), proxy=None):
	self.log_signal.emit("INFO", f"Start_search", f" [Text][{self.mainwindows.text_search}]")
	plugins_list = [name for name in os.listdir("plugins")]
	for pl_index, pl_name in enumerate(plugins_list, start=1):
		self.log_signal.emit("INFO", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [start]")
		start_time = time.perf_counter()
		try:
			with open(f"plugins/{pl_name}/metadata.json") as metadata:
				mt_data = json.load(metadata)

			if mt_data['status'] == "works":
				if mt_data['type'] == "search":
					plugin = importlib.import_module(f"plugins.{pl_name}.{mt_data['file']}")
					data_info_pl = plugin.data_info()

					#funk_start
					args_pl = {}

					if data_info_pl['search']['objects'][0] and objects:   args_pl["objects"]= objects
					if data_info_pl['search']['klass'][0] and klass:       args_pl["klass"]= klass
					if data_info_pl['search']['q'][0] and q:               args_pl["q"]= q
					if data_info_pl['search']['storinka'][0] and storinka: args_pl["storinka"]= storinka
					if data_info_pl['search']['proxy'][0] and proxy:       args_pl["proxy"]= proxy

					if data_info_pl['search']['objects'][1] == False and objects == None: pass
					elif data_info_pl['search']['klass'][1] == False and klass == None: pass
					elif data_info_pl['search']['q'][1] == False and q == None: pass
					elif data_info_pl['search']['storinka'][1] == False and storinka == None: pass
					elif data_info_pl['search']['proxy'][1] == False and proxy == None: pass
					else:
						print(args_pl)
						if data_info_pl['search']['cookie']:
							session_pl = plugin.Load_data(json.load(open(f"data/cookies/{pl_name}", "r")))
							print(session_pl.search(**args_pl))
						else:
							print(plugin.Load_data.search(self, **args_pl))

				elif mt_data['type'] == "search_engine":
					pass


			self.log_signal.emit("INFO", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [endTime][{time.perf_counter() - start_time}]s")
		except Exception as e:
			self.log_signal.emit("ERROR", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [{e}]")
