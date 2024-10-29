import importlib
import os
import time
import json
import threading
import Core

def plugin_data(self):
	self.log_signal.emit("INFO", f"Start_search", f" [Text][{self.mainwindows.text_search}]")
	plugins_list = [name for name in os.listdir("plugins")]
	for pl_index, pl_name in enumerate(plugins_list, start=1):
		self.log_signal.emit("INFO", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [start]")
		start_time = time.perf_counter()
		try:
			with open(f"plugins/{pl_name}/metadata.json") as metadata:
				mt_data = json.load(metadata)

			if mt_data['type'] == "search":
				plugin = importlib.import_module(f"plugins.{pl_name}.{mt_data['file']}")
				print(plugin.data_info())

			self.log_signal.emit("INFO", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [endTime][{time.perf_counter() - start_time}s]")
		except Exception as e:
			self.log_signal.emit("ERROR", f"Plugin", f" [{pl_index}]/[{len(plugins_list)}] [{pl_name}] [endTime][{time.perf_counter() - start_time}s]")
