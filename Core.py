import os
import time
import json
import psutil
import sys
import random
import multiprocessing
import asyncio
import aiohttp
from typing import Literal
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileSystemModel, QListWidgetItem, QMessageBox, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, QProcess
from modules import ld_plugins
from modules import sr_data
from modules import GUI
from modules import GUI_update
from modules import set_GUI_item_sr

from modules.decorate import try_except
from rich import print as color_print

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Search_parser(QThread):
	log_signal = QtCore.pyqtSignal(str, str, str)
	progress_signal = QtCore.pyqtSignal(int)
	update_data_signal = QtCore.pyqtSignal(int, int, int, str, dict, list)

	def __init__(self, mainwindows):
		QThread.__init__(self)
		self.mainwindows = mainwindows
	
	def run(self):
		start_time = time.perf_counter()
		index_sessions = 0
		for item_num in self.mainwindows.listWidget_2.selectedIndexes():
			index_sessions = item_num.row()
		self.urls_data_list = []
		self.platforms_num = 0
		self.wiki_text_data = ""
		self.wiki_title_data = ""
		multiprocessing.Process(target=sr_data.plugin_data(self, subject="/geografiya", q=self.mainwindows.text_search)).start()
		multiprocessing.Process(target=sr_data.plugin_processing_data(self, index_sessions, self.urls_data_list)).start()
		# sr_data.wiki_data(self)
		
		self.update_data_signal.emit(index_sessions, len(self.urls_data_list), self.platforms_num, f"{time.perf_counter()-start_time:.02f}", {"title": self.wiki_title_data, "text": self.wiki_text_data}, self.urls_data_list)

class Core_load_flow(QThread):
	log_signal = QtCore.pyqtSignal(str, str, str)
	progress_signal = QtCore.pyqtSignal(int)
	text_signal = QtCore.pyqtSignal(str)
	core_start_signal = QtCore.pyqtSignal()

	def __init__(self, mainwindows):
		QThread.__init__(self)
		self.mainwindows = mainwindows
	
	def run(self):
		ld_plugins.check_pl(self.log_signal, self.progress_signal, self.text_signal)
		self.core_start_signal.emit()

class Core_load(QtWidgets.QMainWindow, GUI_update.Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

		path = f'res/gif/giphy ({random.randint(0, 40)}).webp'
		self.gif = QtGui.QMovie(path)
		self.label_2.setMovie(self.gif)
		self.gif.start()

		self.logs("INFO", "START LOAD")

		#Flow start
		self.load_process = Core_load_flow(mainwindows=self)
		self.load_process.log_signal.connect(self.logs)
		self.load_process.progress_signal.connect(self.progress_load)
		self.load_process.text_signal.connect(self.text_load)
		self.load_process.core_start_signal.connect(self.load_core_start)
		self.load_process.start()


	def load_core_start(self):
		self.close()
		self.app2 = ExampleApp()
		self.app2.show()

	def progress_load(self, progress_set):
		self.progressBar.setValue(progress_set)

	def text_load(self, text_set):
		self.label.setText(text_set)

	def logs(self, type_log: Literal["info", "INFO", "WARN", "ERROR"], theme_log="none", text_log=""):
		data_log = f'[{time.strftime("%H:%M:%S")}] <{type_log}> [{theme_log}]{text_log}'
		with open(f"logs/{time.strftime('%Y-%m-%d')}.log", "a", encoding="utf-8") as log_wr:
			log_wr.write(f'{data_log}\n')
		print(data_log)

	@try_except(Exception, funk=(lambda ex: None))
	def mousePressEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self.old_pos = event.pos()


	@try_except(Exception, funk=(lambda ex: None))
	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self.old_pos = None


	@try_except(Exception, funk=(lambda ex: None))
	def mouseMoveEvent(self, event):
		if self.old_pos:
			delta = event.pos() - self.old_pos
			self.move(self.pos() + delta)

class ExampleApp(QtWidgets.QMainWindow, GUI.Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		self.logs("INFO", "START")
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

	#Data
		self.text_search = ""
		self.show_w = True
		self.win_resizing_left = False
		self.win_resizing_right = False
		self.win_resizing_top = False
		self.win_resizing_bottom = False
		self.win_resizing_px = 4

	#Class
		self.parser_search = Search_parser(mainwindows=self)
		self.parser_search.log_signal.connect(self.logs)
		self.parser_search.progress_signal.connect(self.progress_search)
		self.parser_search.update_data_signal.connect(self.set_session_data)

	#Button
		self.pushButton_10.clicked.connect(self.close_)
		self.pushButton_18.clicked.connect(self.show_)
		self.pushButton_19.clicked.connect(self.show_winow_)
		self.pushButton_11.clicked.connect(self.start_search_0)
		self.pushButton_22.clicked.connect(self.start_search_1)

	#Close Button
		self.pushButton_36.clicked.connect(self.close_settings)
		self.pushButton_25.clicked.connect(self.close_settings_general)
		self.pushButton_45.clicked.connect(self.close_settings_general)
		self.pushButton_48.clicked.connect(self.close_settings_general)

	#Open Button
		self.pushButton_17.clicked.connect(self.open_settings)
		self.pushButton_26.clicked.connect(self.open_settings_general)
		self.pushButton_28.clicked.connect(self.open_settings_search)
		self.pushButton_29.clicked.connect(self.open_settings_security)
		self.pushButton_30.clicked.connect(self.open_settings_addons)
		self.pushButton_27.clicked.connect(self.open_settings_info)
		self.pushButton_47.clicked.connect(self.open_settings_info)
		self.pushButton_39.clicked.connect(self.open_settings_info)
		self.pushButton_35.clicked.connect(self.open_settings_info)
		self.pushButton_34.clicked.connect(self.open_settings_general)
		self.pushButton_38.clicked.connect(self.open_settings_accounts)
		self.pushButton_33.clicked.connect(self.open_settings_history)
		self.pushButton_40.clicked.connect(self.open_settings_history_search)
		self.pushButton_44.clicked.connect(self.open_settings_history_answers)
		self.pushButton_42.clicked.connect(self.open_settings_history_logs)
		self.pushButton_31.clicked.connect(self.open_settings_addons_search)
		self.pushButton_41.clicked.connect(self.open_settings_addons_plugins)
		self.pushButton_32.clicked.connect(self.open_settings_addons)
		self.pushButton_37.clicked.connect(self.open_settings_manual)
		self.pushButton_16.clicked.connect(self.open_settings_manual)
		self.pushButton_43.clicked.connect(self.open_settings_logs)

#Core
	#Search|============================================|
	def start_search_1(self):
		self.text_search = self.plainTextEdit_2.toPlainText()
		self.parser_search.start()

	def start_search_0(self):
		self.plainTextEdit_2.setPlainText(self.plainTextEdit.toPlainText())
		self.text_search = self.plainTextEdit.toPlainText()
		self.plainTextEdit.setPlainText("")
		self.stackedWidget.setCurrentIndex(1)
		self.parser_search.start()
		
	def set_session_data(self, index_session, results, platforms, times, wiki_text, lists_data):
		data_write = {
			"session_index": index_session,
			"results": results,
			"platforms": platforms,
			"times": times,
			"lists_data": lists_data,
			"page": 0,}
			# "wiki_text": wiki_text
		
		with open(f"temp_data/sessions/session_{index_session}.json", "w", encoding="utf-8") as session_set_sr_data:
			json.dump(data_write, session_set_sr_data, ensure_ascii=False, indent=4)
		self.set_sr_data_GUI()

	def progress_search(self, value_pr):
		self.progressBar.setValue(value_pr)

	def set_sr_data_GUI(self):
		index_sessions = 0
		for item_num in self.listWidget_2.selectedIndexes():
			index_sessions = item_num.row()

		with open(f"temp_data/sessions/session_{index_sessions}.json", "r", encoding="utf-8") as file_r:
			session_sr = json.load(file_r)

		self.label_3.setText(f"[results]: [{session_sr['results']}]")
		self.label_4.setText(f"[platforms]: [{session_sr['platforms']}]")
		self.label_5.setText(f"[time]: [{session_sr['times']}]")
		# self.label_2.setText(session_sr['wiki_text']['title'])
		# self.textBrowser.setText(session_sr['wiki_text']['text'])
		for index_files in session_sr['lists_data'][(session_sr['page']*10):(session_sr['page']*10+10)]:
			with open(f"temp_data/json/index_{index_sessions}_{index_files}.json", "r", encoding="utf-8") as file_r:
				file_sr = json.load(file_r)
				
			ItemQWidget = set_GUI_item_sr.Item_search()
			ItemQWidget.setPl_sr(f"  {file_sr['platform']}  ")
			ItemQWidget.setUrl_sr(f"  {file_sr['url']}  ")
			ItemQWidget.setPl_icon_sr(f"plugins/{file_sr['platform']}/res/{file_sr['platform']}.png")
			ItemQWidget.setPrev_text_sr(file_sr['name_test'])
			ItemQWidget.setType_sr(file_sr['type_data'])
			ItemQWidget.setScor_sr("none")
			ItemQWidget.setQuest_sr(len(file_sr['answers']))
			ItemQWidget.setLess_sr(file_sr['object'])
			ItemQWidget.setClass_sr(file_sr['klass'])
			item = QtWidgets.QListWidgetItem(self.listWidget_3)
			item.setSizeHint(QtCore.QSize(245, 178))
			self.listWidget_3.addItem(item)
			self.listWidget_3.setItemWidget(item, ItemQWidget)


#Settings|==============================================|
	#History
	def open_settings_history_search(self):
		self.stackedWidget_5.setCurrentIndex(7)

	def open_settings_history_answers(self):
		self.stackedWidget_5.setCurrentIndex(8)

	def open_settings_history_logs(self):
		self.stackedWidget_5.setCurrentIndex(9)

	def open_settings_history(self):
		self.pushButton_40.setChecked(True)
		self.stackedWidget_4.setCurrentIndex(3)
		self.stackedWidget_5.setCurrentIndex(7)

	#Addons
	def open_settings_addons(self):
		self.stackedWidget_4.setCurrentIndex(2)
		self.stackedWidget_5.setCurrentIndex(3)
		self.pushButton_31.setChecked(True)

	def open_settings_addons_search(self):
		self.stackedWidget_5.setCurrentIndex(3)

	def open_settings_addons_plugins(self):
		self.stackedWidget_5.setCurrentIndex(6)

	#Settings|==========================================|
	def open_settings_manual(self):
		self.stackedWidget_5.setCurrentIndex(4)
		self.open_settings()
		self.pushButton_37.setChecked(True)

	def open_settings_logs(self):
		self.stackedWidget_5.setCurrentIndex(11)

	def open_settings_accounts(self):
		self.stackedWidget_5.setCurrentIndex(5)

	def open_settings_security(self):
		self.stackedWidget_5.setCurrentIndex(2)

	def open_settings_info(self):
		self.stackedWidget_5.setCurrentIndex(10)

	def open_settings_search(self):
		self.stackedWidget_5.setCurrentIndex(1)

	def open_settings_general(self):
		self.pushButton_26.setChecked(True)
		self.stackedWidget_4.setCurrentIndex(0)
		self.stackedWidget_5.setCurrentIndex(0)

	def open_settings(self):
		self.stackedWidget.setCurrentIndex(2)

	#Close
	def close_settings_general(self):
		self.stackedWidget_4.setCurrentIndex(1)

	def close_settings(self):
		self.stackedWidget.setCurrentIndex(0)

#System|================================================|

	def logs(self, type_log: Literal["info", "INFO", "WARN", "ERROR"], theme_log="none", text_log=""):
		time_ = time.strftime("%H:%M:%S")
		data_log = [f"[{time_}]", f"<{type_log}>", f"[{theme_log}]", f"[{text_log}]"]
		
		with open(f"logs/{time.strftime('%Y-%m-%d')}.log", "a", encoding="utf-8") as log_wr:
			log_wr.write(f'{data_log}\n')

		print(data_log)
		
		if type_log == "ERROR":
			data_log = f'<span style="color:#F23F43;">[{time_}] &lt;ERROR&gt; <{type_log}> [{theme_log}]{text_log}</span>'

		elif type_log == "info":
			data_log = f'<span>[{time_}] &lt;INFO&gt; <{type_log}> [{theme_log}]{text_log}</span>'

		elif type_log == "INFO":
			data_log = f'<span style="color:#23A55A;">[{time_}] &lt;INFO&gt; <{type_log}> [{theme_log}]{text_log}</span>'

		elif type_log == "WARN":
			data_log = f'<span style="color:#F0B232;">[{time_}] &lt;INFO&gt; <{type_log}> [{theme_log}]{text_log}</span>'

		self.textBrowser_5.append(data_log)


	@try_except(Exception, funk=(lambda ex: None))
	def mousePressEvent(self, event):
		if self.show_w == True:
			if event.button() == QtCore.Qt.LeftButton:
				self.old_pos = event.pos()
				if self.win_resizing_px >= self.old_pos.x():
					self.win_resizing_left = True

				if (self.size().width() - self.win_resizing_px) <= self.old_pos.x():
					self.win_resizing_right = True

				if self.win_resizing_px >= self.old_pos.y():
					self.win_resizing_top = True

				if (self.size().height() - self.win_resizing_px) <= self.old_pos.y():
					self.win_resizing_bottom = True


	@try_except(Exception, funk=(lambda ex: None))
	def mouseReleaseEvent(self, event):
		if self.show_w == True:
			if event.button() == QtCore.Qt.LeftButton:
				self.old_pos = None
				self.win_resizing_left = False
				self.win_resizing_right = False
				self.win_resizing_top = False
				self.win_resizing_bottom = False


	@try_except(Exception, funk=(lambda ex: None))
	def mouseMoveEvent(self, event):
		if self.show_w and self.old_pos:
			delta = event.pos() - self.old_pos
			if self.win_resizing_left:
				if self.geometry().width() > 616:
					self.setGeometry(QtCore.QRect(self.geometry().x() + delta.x(), 
												  self.geometry().y(), 
												  self.geometry().width() - delta.x(), 
												  self.geometry().height()))
				else:
					if delta.x() < 0:
						self.setGeometry(QtCore.QRect(self.geometry().x() + delta.x(), 
													  self.geometry().y(), 
													  self.geometry().width() - delta.x(), 
													  self.geometry().height()))

			elif self.win_resizing_right:
				self.setGeometry(QtCore.QRect(self.geometry().x(), 
											  self.geometry().y(), 
											  event.pos().x(), 
											  self.geometry().height()))
			
			elif self.win_resizing_top:
				if self.geometry().height() > 434:
					self.setGeometry(QtCore.QRect(self.geometry().x(), 
												  self.geometry().y() + delta.y(), 
												  self.geometry().width(), 
												  self.geometry().height() - delta.y()))
				else:
					if delta.y() < 0:
						self.setGeometry(QtCore.QRect(self.geometry().x(), 
													  self.geometry().y() + delta.y(), 
													  self.geometry().width(), 
													  self.geometry().height() - delta.y()))
			
			elif self.win_resizing_bottom:
				self.setGeometry(QtCore.QRect(self.geometry().x(), 
											  self.geometry().y(), 
											  self.geometry().width(), 
											  event.pos().y()))

			else:
				self.move(self.pos() + delta)

	def close_(self):
		sys.exit()

	def show_(self):
		if self.show_w:
			self.showMaximized()
			self.show_w = False
		else:
			self.showNormal()
			self.show_w = True

	def show_winow_(self):
		self.showMinimized()


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
	