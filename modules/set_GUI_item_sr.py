from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileSystemModel, QListWidgetItem, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, QProcess
from modules import GUI_sr_item
from modules import GUI_quiz
from modules import GUI_answer
from modules import GUI_tab


class Item_search(QtWidgets.QWidget, GUI_sr_item.Ui_Form):
	def __init__(self, parent=None):
		super(Item_search, self).__init__(parent)
		self.setupUi(self)

	def setPl_sr(self, sr_name=None):
		self.label.setText(sr_name)

	def setUrl_sr(self, sr_url=None):
		self.label_2.setText(sr_url)

	def setPl_icon_sr(self, sr_ico=None):
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(sr_ico), QtGui.QIcon.Normal, QtGui.QIcon.On)
		self.pushButton.setIcon(icon)

	def setPrev_text_sr(self, sr_text=None):
		if sr_text: self.textBrowser.setText(sr_text)
		else: self.textBrowser.hide()

	def setType_sr(self, sr_text=None):
		if sr_text: self.label_7.setText(f"  [type]: [{sr_text}]  ")
		else: self.label_7.hide()

	def setScor_sr(self, sr_text=None):
		if sr_text: self.label_4.setText(f"  [score]: [{sr_text}]  ")
		else: self.label_4.hide()
		
	def setQuest_sr(self, sr_text=None):
		if sr_text: self.label_5.setText(f"  [questions]: [{sr_text}]  ")
		else: self.label_5.hide()

	def setLess_sr(self, sr_text=None):
		if sr_text: self.label_6.setText(f"  [lesson]: [{sr_text}]  ")
		else: self.label_6.hide()

	def setClass_sr(self, sr_text=None):
		if sr_text: self.label_3.setText(f"  [class]: [{sr_text}]  ")
		else: self.label_3.hide()

class Item_quiz(QtWidgets.QWidget, GUI_quiz.Ui_Form):
	def __init__(self, zoom_img, item_w, parent=None):
		super(Item_quiz, self).__init__(parent)
		self.setupUi(self)

		self.zoom_img = zoom_img
		self.item_w = item_w

		self.pushButton.clicked.connect(lambda: zoom_img(self.pushButton.property("icon_path")))

	def setNum_quiz(self, qz_num=None):
		if qz_num:
			self.label.setText(qz_num)
		else: self.label.hide()

	def setImg_quiz(self, qz_ico=None):
		if qz_ico:
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(qz_ico), QtGui.QIcon.Normal, QtGui.QIcon.On)
			self.pushButton.setIcon(icon)
			self.pushButton.setProperty("icon_path", qz_ico)
		else: self.pushButton.hide()

	def setText_quiz(self, qz_text=None):
		if qz_text: self.textBrowser.setText(qz_text)
		else: self.textBrowser.hide()

	def setList_answer(self, qz_item=None, type=None, index_hd=True, img_l=None):
		if type == "matching":
			for item_qz in qz_item['value']:
				self.listWidget.addItem(item_qz[0]['text'])
				self.listWidget_2.addItem(item_qz[0]['text'])

		elif type == "sorting":
			for item_qz in qz_item['value']:
				for item_2 in item_qz['value']:
					self.listWidget.addItem(item_qz['text'])
					self.label_2.hide()

		else:
			if qz_item: 
				for index, item_qz in enumerate(qz_item, 1):
					ItemQWidget = Item_answer(self.zoom_img, self.item_w)
					ItemQWidget.setImg_answer(item_qz['img'])
					ItemQWidget.setText_answer(item_qz['text'])
					item = QtWidgets.QListWidgetItem(self.listWidget)

					if index_hd: ItemQWidget.setNum_answer(f" {index} ", item_qz["correctness"])
					else: ItemQWidget.setNum_answer()
					if item_qz['img']: 
						item.setSizeHint(QtCore.QSize(245, 76))
						img_l.append(item_qz['img'])
					else: item.setSizeHint(QtCore.QSize(245, 32))
					
					self.listWidget.addItem(item)
					self.listWidget.setItemWidget(item, ItemQWidget)

			else: self.listWidget.hide()
			self.listWidget_2.hide()
			self.label_2.hide()

class Item_answer(QtWidgets.QWidget, GUI_answer.Ui_Form):
	def __init__(self, zoom_img, item_w, parent=None):
		super(Item_answer, self).__init__(parent)
		self.setupUi(self)

		self.pushButton.clicked.connect(lambda: zoom_img(self.pushButton.property("icon_path")))

	def setNum_answer(self, qz_num=None, correctness=None):
		if correctness: self.pushButton_2.setChecked(correctness)
		if qz_num: self.pushButton_2.setText(f" {qz_num} ")
		else: 
			self.pushButton_2.hide()

	def setImg_answer(self, qz_ico=None, correctness=None):
		if qz_ico:
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(qz_ico), QtGui.QIcon.Normal, QtGui.QIcon.On)
			self.pushButton.setIcon(icon)
			self.pushButton.setProperty("icon_path", qz_ico)
		else: self.pushButton.hide()

	def setText_answer(self, qz_text=None, correctness=None):
		if qz_text: self.textBrowser.setText(qz_text)
		else: self.textBrowser.hide()

class Item_tab(QtWidgets.QWidget, GUI_tab.Ui_Form):
	def __init__(self, del_tab_session, item_tab, parent=None):
		super(Item_tab, self).__init__(parent)
		self.setupUi(self)

		self.pushButton.clicked.connect(lambda: del_tab_session(item_tab))