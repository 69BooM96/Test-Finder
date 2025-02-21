import importlib
import os
import time
import json
import threading
import requests
import Core


def check_pl(log_signal, progress_signal, text_signal):
	progress_num = 0
	progress_item = 0
	try:
		list_update = []
		plugins_dirs = [name for name in os.listdir("plugins")]
		log_signal.emit("INFO", "Check plugins", f" [{len(plugins_dirs)}]")

		progress_num += 10
		progress_signal.emit(progress_num)
		text_signal.emit(f"[Check plugins][{len(plugins_dirs)}]")

		if len(plugins_dirs) <= 90:
			progress_item = 90 // len(plugins_dirs)

		for pl_index, pl_name in enumerate(plugins_dirs):
			try:
				with open(f"plugins/{pl_name}/metadata.json") as metadata:
					mt_data = json.load(metadata)

				# update = True if json.loads(requests.get(mt_data['check']).text)["version"] != mt_data["version"] else False
				
				update = True
				
				log_signal.emit("INFO", "load plugin", f" [{pl_index}][{pl_name}] [version][{mt_data['version']}] [update][{update}] [status][{mt_data['status']}]")
				text_signal.emit(f"[{mt_data['name']}]")

				if update == True:
					list_update.append(mt_data['update'])
			except Exception as e:
				log_signal.emit("ERROR", "load plugins", f" [{pl_index}][{pl_name}] [Failed to check plugin version] [{e}]")
			
			progress_num += progress_item
			progress_signal.emit(progress_num)

		progress_num = 100
		progress_signal.emit(progress_num)
		return list_update
	except Exception as e:
		log_signal.emit("ERROR", "check plugins", f" [{e}]")

def update_pl(self, list_update):
	log_signal.emit("INFO", "update plugin", f" [{len(list_update)}]{list_update}")
	for item_update in list_update:
		pass