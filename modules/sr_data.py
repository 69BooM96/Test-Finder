import importlib
import os
import time
import json
import threading
import Core

def plugin_data():
	for pl_name in [name for name in os.listdir("plugins")]:
		try:
			with open(f"plugins/{pl_name}/metadata.json") as metadata:
				mt_data = json.load(metadata)

			if mt_data['type'] == "search":
				plugin = importlib.import_module(f"plugins.{pl_name}.{mt_data['file']}")
				print(plugin.data_info())
			
		except Exception as e:
			pass
