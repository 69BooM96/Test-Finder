import os
import time
import json
import psutil
import sys
import random
import multiprocessing
import asyncio
import aiohttp
import webbrowser

from typing import Literal
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileSystemModel, QListWidgetItem, QMessageBox, QWidget
from PyQt5.QtCore import QThread, QProcess
from PyQt5.QtCore import QTimer
from colorama import *

from modules import ld_plugins
from modules import sr_data
from modules import GUI
from modules import GUI_update
from modules import set_GUI_item_sr
from modules import ld_image
# from modules import visualizer
from modules.decorate import try_except


# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Core_answer(QThread):
	log_signal = QtCore.pyqtSignal(str, str, str)
	progress_signal = QtCore.pyqtSignal(int)
	update_data_signal = QtCore.pyqtSignal()

	def __init__(self, mainwindows):
		QThread.__init__(self)
		self.mainwindows = mainwindows
	
	def run(self):
		index_sessions = 0
		for item_num in self.mainwindows.listWidget_2.selectedIndexes():
			index_sessions = item_num.row()
		for item_num in self.mainwindows.listWidget_3.selectedIndexes():
			index_json = item_num.row()

		sr_data.plugin_answers_data(self, index_sessions, index_json, self.mainwindows.url_data_answers)
		self.update_data_signal.emit()
		

class Search_parser(QThread):
	log_signal = QtCore.pyqtSignal(str, str, str)
	progress_signal = QtCore.pyqtSignal(int)
	update_data_signal = QtCore.pyqtSignal(int, int, int, str, dict)

	def __init__(self, mainwindows):
		QThread.__init__(self)
		self.mainwindows = mainwindows
		self.urls_data_list = []
		self.len_url_list = 0
		self.platforms_num = 0
		self.wiki_text_data = ""
		self.wiki_title_data = ""
		self.progress_signal.emit(1)
		self.progress_index = 2
	
	def run(self):
		start_time = time.perf_counter()
		index_sessions = 0
		for item_num in self.mainwindows.listWidget_2.selectedIndexes():
			index_sessions = item_num.row()

		sr_data.PluginStart.search_data(self, search_query=self.mainwindows.text_search, subject=None, grade=None, pagination=(1,4), proxy=None)
		self.len_url_list = len(self.urls_data_list)
		sr_data.PluginStart.processing_data(self, index_sessions, self.urls_data_list)

		# sr_data.wiki_data(self)
		self.progress_signal.emit(100)		
		self.update_data_signal.emit(index_sessions, self.len_url_list, self.platforms_num, f"{time.perf_counter()-start_time:.02f}", {"title": self.wiki_title_data, "text": self.wiki_text_data})
		self.progress_signal.emit(0)

class Img_load(QThread):
	log_signal = QtCore.pyqtSignal(str, str, str)
	progress_signal = QtCore.pyqtSignal(int)

	def __init__(self, mainwindows):
		QThread.__init__(self)
		self.mainwindows = mainwindows

	def run(self):
		start_time = time.perf_counter()
		l_img = self.mainwindows.list_imgs

		if len(l_img) != 0:
			l_img_progress=0
			l_img_num = 100//len(l_img)

			self.log_signal.emit("INFO", f"Start_load_img", f" [img][{len(l_img)}]")

			queue = multiprocessing.Queue()
			load_pr = multiprocessing.Process(target=ld_image.load_img, args=(l_img, queue))
			load_pr.start()

			while load_pr.is_alive() or not queue.empty():
				if not queue.empty():
					msg = queue.get()
					l_img_progress += l_img_num
					self.log_signal.emit(msg["level"], msg["source"], msg["data"])
					self.progress_signal.emit(l_img_progress)

			load_pr.join()

			self.progress_signal.emit(100)
			self.log_signal.emit("INFO", f"Stop_load_img", f" [img][{len(l_img)}] [endTime][{time.perf_counter() - start_time:.02f}]s")
			self.progress_signal.emit(0)
		else:
			self.log_signal.emit("INFO", f"None_img", f" [img][{len(l_img)}] [endTime][0]s")
			self.progress_signal.emit(0)

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
		self.url_data_answers = ""
		self.show_w = True
		self.win_resizing_left = False
		self.win_resizing_right = False
		self.win_resizing_top = False
		self.win_resizing_bottom = False
		self.win_resizing_px = 4

	#Preload
		self.start_session()

	#Class
		self.parser_search = Search_parser(mainwindows=self)
		self.parser_search.log_signal.connect(self.logs)
		self.parser_search.progress_signal.connect(self.progress_search)
		self.parser_search.update_data_signal.connect(self.set_session_data)

		self.parser_img = Img_load(mainwindows=self)
		self.parser_img.log_signal.connect(self.logs)
		self.parser_img.progress_signal.connect(self.progress_img)

		self.parser_answers = Core_answer(mainwindows=self)
		self.parser_answers.log_signal.connect(self.logs)
		self.parser_answers.progress_signal.connect(self.progress_img)
		self.parser_answers.update_data_signal.connect(self.set_quiz_data_GUI)

	#Button
		self.pushButton_10.clicked.connect(self.close_)
		self.pushButton_18.clicked.connect(self.show_)
		self.pushButton_19.clicked.connect(self.show_winow_)
		self.pushButton_11.clicked.connect(self.start_search_0)
		self.pushButton_22.clicked.connect(self.start_search_1)
		self.pushButton.clicked.connect(self.back_page)
		self.pushButton_2.clicked.connect(self.next_page)

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
		self.pushButton_43.clicked.connect(self.open_settings_logs)
		self.pushButton_16.clicked.connect(self.open_git)
		self.pushButton_49.clicked.connect(self.add_tab_session)
		self.pushButton_46.clicked.connect(self.load_answer)

	#list Widget
		self.listWidget_3.clicked.connect(self.set_quiz_data)
		self.listWidget_2.clicked.connect(self.open_session)

#Core
#GUI|===================================================|
	def open_git(self):
		webbrowser.open_new_tab("https://github.com/69BooM96/Test-Finder/")

#Session|===============================================|
	def start_session(self):
		with open("data/sessions.json", "w", encoding="utf-8") as file:
			json.dump([], file, ensure_ascii=False, indent=4)

		self.add_tab_session()
		self.listWidget_2.setCurrentRow(0)

	def add_tab_session(self):
		item = QtWidgets.QListWidgetItem(self.listWidget_2)
		item.setSizeHint(QtCore.QSize(160, 26))
		ItemQWidget = set_GUI_item_sr.Item_tab(self.del_tab_session, item)
		
		self.listWidget_2.addItem(item)
		self.listWidget_2.setItemWidget(item, ItemQWidget)

		with open("data/sessions.json", "r", encoding="utf-8") as file:
			data_sessions = json.load(file)

		data_sessions.append({"search": None, "history_page": 0, "history": [{"page": "menu", "data": None}]})

		with open("data/sessions.json", "w", encoding="utf-8") as file:
			json.dump(data_sessions, file, ensure_ascii=False, indent=4)

	def del_tab_session(self, item):
		if self.listWidget_2.count() != 1:
			item_num = self.listWidget_2.row(item)
			if item_num != -1:
				with open("data/sessions.json", "r", encoding="utf-8") as file:
					data_sessions = json.load(file)
				del data_sessions[item_num]
				with open("data/sessions.json", "w", encoding="utf-8") as file:
					json.dump(data_sessions, file, ensure_ascii=False, indent=4)

				item = self.listWidget_2.takeItem(item_num)
				del item
		else:
			sys.exit(app.exec_())

	def set_session_data(self, index_session, results, platforms, times, wiki_text):
		data_write = {
			"results": results,
			"platforms": platforms,
			"times": times,
			"page": 0,}

		with open("data/sessions.json", "r", encoding="utf-8") as file:
			sessions_load = json.load(file)

		sessions_load[index_session]["search"] = data_write
		with open(f"data/sessions.json", "w", encoding="utf-8") as file_w:
			json.dump(sessions_load, file_w, ensure_ascii=False, indent=4)
		self.set_sr_data_GUI()

	def next_page(self):
		for item_num in self.listWidget_2.selectedIndexes():
			index_session = item_num.row()
		with open("data/sessions.json", "r", encoding="utf-8") as file:
			sessions_load = json.load(file)

		if (sessions_load[index_session]["history_page"] + 1) <= (len(sessions_load[index_session]["history"])-1):
			sessions_load[index_session]["history_page"] = sessions_load[index_session]["history_page"] + 1

			with open(f"data/sessions.json", "w", encoding="utf-8") as file_w:
				json.dump(sessions_load, file_w, ensure_ascii=False, indent=4)

			self.load_session(sessions_load[index_session]["history"][sessions_load[index_session]["history_page"]])

	def back_page(self):
		for item_num in self.listWidget_2.selectedIndexes():
			index_session = item_num.row()
		with open("data/sessions.json", "r", encoding="utf-8") as file:
			sessions_load = json.load(file)

		if (sessions_load[index_session]["history_page"] - 1) >= 0:
			sessions_load[index_session]["history_page"] = sessions_load[index_session]["history_page"] - 1

			with open(f"data/sessions.json", "w", encoding="utf-8") as file_w:
				json.dump(sessions_load, file_w, ensure_ascii=False, indent=4)

			self.load_session(sessions_load[index_session]["history"][sessions_load[index_session]["history_page"]])

	def add_history_sessions(self, page, data=None):
		for item_num in self.listWidget_2.selectedIndexes():
			index_session = item_num.row()
		with open("data/sessions.json", "r", encoding="utf-8") as file:
			sessions_load = json.load(file)
		sessions_load[index_session]["history"].append({"page": page, "data": data})
		sessions_load[index_session]["history_page"] = sessions_load[index_session]["history_page"] + 1
		with open(f"data/sessions.json", "w", encoding="utf-8") as file_w:
			json.dump(sessions_load, file_w, ensure_ascii=False, indent=4)

	def del_history_sessions(self, index_session):
		with open("data/sessions.json", "r", encoding="utf-8") as file:
			sessions_load = json.load(file)
		for item in range(index_session, len(sessions_load)):
			del sessions_load[item]
		with open(f"data/sessions.json", "w", encoding="utf-8") as file_w:
			json.dump(sessions_load, file_w, ensure_ascii=False, indent=4)

	def open_session(self):
		for item_num in self.listWidget_2.selectedIndexes():
			index_session = item_num.row()
		with open("data/sessions.json", "r", encoding="utf-8") as file:
			sessions_load = json.load(file)
		self.load_session(sessions_load[index_session]["history"][sessions_load[index_session]["history_page"]])

	def load_session(self, page_load):
		if page_load["page"] == "menu":
			self.stackedWidget.setCurrentIndex(0)
			self.lineEdit.setText("menu")
			if page_load["data"]:
				...

		elif page_load["page"] == "settings":
			self.stackedWidget.setCurrentIndex(3)
			self.lineEdit.setText("settings")
			if page_load["data"]:
				...

		elif page_load["page"] == "search":
			self.stackedWidget.setCurrentIndex(1)
			self.lineEdit.setText(f"search://{self.text_search.replace(" ", "+")}")
			self.set_sr_data_GUI()

		elif page_load["page"] == "test_browser":
			self.stackedWidget.setCurrentIndex(2)
			if page_load["data"]:
				self.set_quiz_data_GUI(page_load["data"])

		elif page_load["page"] == "web_browser":
			self.stackedWidget.setCurrentIndex(2)
			if page_load["data"]:
				...

#Search|================================================|
	def start_search_1(self):
		self.text_search = self.plainTextEdit_2.toPlainText()
		self.lineEdit.setText(f"search://{self.text_search.replace(" ", "+")}")
		self.parser_search.start()

	def start_search_0(self):
		self.plainTextEdit_2.setPlainText(self.plainTextEdit.toPlainText())
		self.text_search = self.plainTextEdit.toPlainText()
		self.plainTextEdit.setPlainText("")
		self.stackedWidget.setCurrentIndex(1)
		self.add_history_sessions("search")
		self.lineEdit.setText(f"search://{self.text_search.replace(" ", "+")}")
		self.parser_search.start()

	def progress_search(self, value_pr):
		self.progressBar.setValue(value_pr)

	def set_sr_data_GUI(self):
		index_sessions = 0
		for item_num in self.listWidget_2.selectedIndexes():
			index_sessions = item_num.row()

		with open(f"data/sessions.json", "r", encoding="utf-8") as file_r:
			session_sr = json.load(file_r)

		self.label_3.setText(f"[results]: [{session_sr[index_sessions]["search"]['results']}]")
		self.label_4.setText(f"[platforms]: [{session_sr[index_sessions]["search"]['platforms']}]")
		self.label_5.setText(f"[time]: [{session_sr[index_sessions]["search"]['times']}]")
		# self.label_2.setText(session_sr['wiki_text']['title'])
		# self.textBrowser.setText(session_sr['wiki_text']['text'])

		self.listWidget_3.clear()

		with open(f"temp_data/json/index_{index_sessions}.json", "r", encoding="utf-8") as file_r:
			session_data = json.load(file_r)

		for file_sr in session_data[(session_sr[index_sessions]["search"]['page']*10):(session_sr[index_sessions]["search"]['page']*10+10)]:
			ItemQWidget = set_GUI_item_sr.Item_search()
			ItemQWidget.setPl_sr(f"  {file_sr['platform']}  ")
			ItemQWidget.setUrl_sr(f"  {file_sr['url']}  ")
			ItemQWidget.setPl_icon_sr(f"plugins/{file_sr['platform']}/res/{file_sr['platform']}.png")
			ItemQWidget.setPrev_text_sr(f" {file_sr['name_test']} ")
			ItemQWidget.setType_sr(f" {file_sr['type_data']} ")
			ItemQWidget.setScor_sr("none")
			ItemQWidget.setQuest_sr(f" {len(file_sr['answers'])} ")
			ItemQWidget.setLess_sr(f" {file_sr['object']} ")
			ItemQWidget.setClass_sr(f" {file_sr['klass']} ")
			item = QtWidgets.QListWidgetItem(self.listWidget_3)
			item.setSizeHint(QtCore.QSize(245, 178))

			self.listWidget_3.addItem(item)
			self.listWidget_3.setItemWidget(item, ItemQWidget)

#Load_answer
	def load_answer(self):
		for item_num in self.listWidget_3.selectedIndexes():
			index_json = item_num.row()

		self.url_data_answers = self.lineEdit.text().strip()
		self.parser_answers.start()

#Load_data|=============================================|
	def set_quiz_data(self):
		self.stackedWidget.setCurrentIndex(2)
		QTimer.singleShot(20, lambda: self.set_quiz_data_GUI(h_set=True))
		QTimer.singleShot(90, self.start_load_img)

	def start_load_img(self):
		self.parser_img.start()

	def progress_img(self, value_pr):
		self.progressBar_2.setValue(value_pr)
		if value_pr == 0:
			self.set_quiz_data_GUI()

	@try_except(Exception, funk=(lambda ex: None))
	def set_quiz_data_GUI(self, index_json=None, h_set=False):
		self.listWidget_8.clear()
		self.stackedWidget_7.setCurrentIndex(0)
		self.list_imgs = []
		index_sessions = 0
		
		for item_num in self.listWidget_2.selectedIndexes():
			index_sessions = item_num.row()

		if index_json == None:
			for item_num in self.listWidget_3.selectedIndexes():
				index_json = item_num.row()

		if h_set: self.add_history_sessions("test_browser", index_json)
		with open(f"temp_data/json/index_{index_sessions}.json", "r", encoding="utf-8") as file_r:
			l_data = json.load(file_r)

		data = l_data[index_json]
		self.lineEdit.setText(f"{  data['url']}  ")
		self.label_48.setText(f"{  data['name_test']}  ")
		self.label_50.setText(f"{  data['object']}  ")
		self.label_51.setText(f"{  data['klass']}  ")
		self.label_49.setText(f"{  len(data['answers'])}  ")

		if data['type_data'] == "test":
			for index, data_item in enumerate(data['answers'], 1):
				ItemQWidget = set_GUI_item_sr.Item_quiz()
				ItemQWidget.setNum_quiz(f"   {index}   ")
				if data_item['img']: 
					ItemQWidget.setImg_quiz(f"temp_data/imgs/{data_item['img'].split('/')[-1]}")
					self.list_imgs.append(data_item['img'])
				else: ItemQWidget.setImg_quiz()
				ItemQWidget.setText_quiz(data_item['text'])
				ItemQWidget.setList_answer(data_item['value'], data_item['type'], img_l=self.list_imgs)
				
				item = QtWidgets.QListWidgetItem(self.listWidget_8)
				# item.setSizeHint(QtCore.QSize(245, 254))
				item.setSizeHint(QtCore.QSize(600, 288))
				self.listWidget_8.addItem(item)
				self.listWidget_8.setItemWidget(item, ItemQWidget)

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
		self.stackedWidget.setCurrentIndex(3)
		self.add_history_sessions("settings")

	#Close
	def close_settings_general(self):
		self.stackedWidget_4.setCurrentIndex(1)

	def close_settings(self):
		self.stackedWidget.setCurrentIndex(0)
		self.add_history_sessions("menu")

#System|================================================|
	def logs(self, type_log: Literal["info", "INFO", "WARN", "ERROR"], theme_log="none", text_log=""):
		time_ = time.strftime("%H:%M:%S")
		data_log = [f"[{time_}]", f"<{type_log}>", f"[{theme_log}]", f"[{text_log}]"]
		
		with open(f"logs/{time.strftime('%Y-%m-%d')}.log", "a", encoding="utf-8") as log_wr:
			log_wr.write(f'{data_log}\n')

		print(f"[{time_}] <{type_log}> [{theme_log}]{text_log}")
		
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
		if self.show_w:
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
		if self.show_w:
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
				elif delta.x() < 0:
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
				elif delta.y() < 0:
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
	