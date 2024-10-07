import os
import time
import json
from typing import Literal
from modules import ld_plugins


class Core():
	def __init__(self):
		super().__init__()

		self.logs("INFO", "START")

		list_update = ld_plugins.check_pl(self)
		if len(list_update) != 0:
			ld_plugins.update_pl(self, list_update)


	def logs(self, type_log: Literal["info", "INFO", "WARN", "ERROR"], theme_log="none", text_log=""):
		data_log = f'[{time.strftime("%H:%M:%S")}] <{type_log}> [{theme_log}]{text_log}'
		with open(f"logs/{time.strftime('%Y-%m-%d')}.log", "a", encoding="utf-8") as log_wr:
			log_wr.write(f'{data_log}\n')
		print(data_log)

if __name__ == '__main__':
	Core()