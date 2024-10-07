import importlib
import os
import time
import json
import threading
import requests
import Core


def check_pl(self):
	try:
		list_update = []
		plugins_dirs = [name for name in os.listdir("plugins")]
		self.logs("INFO", "Check plugins", f" [{len(plugins_dirs)}]")
		for pl_index, pl_name in enumerate(plugins_dirs):
			try:
				with open(f"plugins/{pl_name}/metadata.json") as metadata:
					mt_data = json.load(metadata)

				update = True if json.loads(requests.get(mt_data['check']).text)["version"] != mt_data["version"] else False
				plugin = importlib.import_module(f"plugins.{pl_name}.{mt_data['file']}")

				self.logs("INFO", "load plugin", f" [{pl_index}][{pl_name}] [version][{mt_data['version']}] [update][{update}] [status][{plugin.Main.work('works')}]")
				if update == True:
					list_update.append(mt_data['update'])
			except Exception as e:
				self.logs("ERROR", "load plugins", f" [{pl_name}] [{e}]")

		return list_update
	except Exception as e:
		self.logs("ERROR", "check plugins", f" [{e}]")

def update_pl(self, list_update):
	self.logs("INFO", "update plugin", f" [{len(list_update)}]{list_update}")
	for item_update in list_update:
		pass