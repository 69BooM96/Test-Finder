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
import random
from modules import ld_plugins
from modules import sr_data
from modules import GUI
from modules import GUI_update


class Core_load(QtWidgets.QMainWindow, GUI_update.Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

		path = f'res/gif/giphy ({random.randint(0, 40)}).webp'
		gif = QtGui.QMovie(path)
		self.label_2.setMovie(gif)
		gif.start()

		self.logs("INFO", "START LOAD")

		self.end_update()

	def end_update(self):
		self.hide()
		self.window2 = ExampleApp()
		self.window2.show()


	def logs(self, type_log: Literal["info", "INFO", "WARN", "ERROR"], theme_log="none", text_log=""):
		data_log = f'[{time.strftime("%H:%M:%S")}] <{type_log}> [{theme_log}]{text_log}'
		with open(f"logs/{time.strftime('%Y-%m-%d')}.log", "a", encoding="utf-8") as log_wr:
			log_wr.write(f'{data_log}\n')
		print(data_log)

	def mousePressEvent(self, event):
		try:
			if event.button() == QtCore.Qt.LeftButton:
				self.old_pos = event.pos()
		except:
			pass

	def mouseReleaseEvent(self, event):
		try:
			if event.button() == QtCore.Qt.LeftButton:
				self.old_pos = None
		except:
			pass

	def mouseMoveEvent(self, event):
		try:
			if not self.old_pos:
				return
			delta = event.pos() - self.old_pos
			self.move(self.pos() + delta)
		except:
			pass

class ExampleApp(QtWidgets.QMainWindow, GUI.Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)

		self.logs("INFO", "START")



	def logs(self, type_log: Literal["info", "INFO", "WARN", "ERROR"], theme_log="none", text_log=""):
		time_ = time.strftime("%H:%M:%S")
		data_log = f'[{time_}] <{type_log}> [{theme_log}]{text_log}'
		with open(f"logs/{time.strftime('%Y-%m-%d')}.log", "a", encoding="utf-8") as log_wr:
			log_wr.write(f'{data_log}\n')
		print(data_log)
		self.textBrowser_5.append(f'[{time_}] <{type_log}> [{theme_log}]{text_log}')


if __name__ == '__main__':
	start_core = 0

	for proc in psutil.process_iter():
		name = proc.name()
		if name == "Test_Finder.exe":
			start_core += 1

	if start_core < 2:
		app = QtWidgets.QApplication(sys.argv)
		window = Core_load()
		window.show()
		sys.exit(app.exec_())
	else:
		pass
	