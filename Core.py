import os
import time
import json
from typing import Literal
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileSystemModel, QListWidgetItem, QMessageBox, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, QProcess
import psutil
import sys
from modules import ld_plugins
from modules import sr_data
from modules import GUI


class ExampleApp(QtWidgets.QMainWindow, GUI.Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)

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
    start_core = 0

    for proc in psutil.process_iter():
        name = proc.name()
        if name == "Test_Finder.exe":
            start_core += 1

    if start_core < 2:
        app = QtWidgets.QApplication(sys.argv)
        window = ExampleApp()
        window.show()
        sys.exit(app.exec_())
    else:
        pass
	