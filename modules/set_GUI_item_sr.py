from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileSystemModel, QListWidgetItem, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, QProcess
from modules import GUI_sr_item


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
		if sr_text: self.label_7.setText(f"[type]: [{sr_text}]")
		else: self.label_7.hide()

	def setScor_sr(self, sr_text=None):
		if sr_text: self.label_4.setText(f"[score]: [{sr_text}]")
		else: self.label_4.hide()
		
	def setQuest_sr(self, sr_text=None):
		if sr_text: self.label_5.setText(f"[questions]: [{sr_text}]")
		else: self.label_5.hide()

	def setLess_sr(self, sr_text=None):
		if sr_text: self.label_6.setText(f"[lesson]: [{sr_text}]")
		else: self.label_6.hide()

	def setClass_sr(self, sr_text=None):
		if sr_text: self.label_3.setText(f"[class]: [{sr_text}]")
		else: self.label_3.hide()