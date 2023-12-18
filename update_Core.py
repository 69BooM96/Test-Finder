from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileSystemModel, QListWidgetItem
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread
import os
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import update
import time
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import webbrowser
import sys
import json
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
import wmi


class update_p(QThread):
    progress_update_signal = QtCore.pyqtSignal(int, str, int)

    def __init__(self, mainwindows):
        super().__init__()
        self.mainwindows = mainwindows

    def run(self):
        self.progress_update_signal.emit(10, "version.info", 0)
        version = requests.get("https://raw.githubusercontent.com/69BooM96/Test-Finder/main/version.info").text
        with open("version.info", "r", encoding="utf-8") as version_read:
            version_p = version_read.read()

        if version != version_p:
            updates = requests.get("https://raw.githubusercontent.com/69BooM96/Test-Finder/main/update.json").text
            self.progress_update_signal.emit(20, "update.json", 0)
            updates = updates.replace("\n", "")
            with open("update.json", "w", encoding="utf-8") as updates_w:
                updates_w.write(updates)

            with open("update.json", "r", encoding="utf-8") as updates_r:
                data_update = json.load(updates_r)

            progress_in = 80//len(data_update)
            progress_s = 20

            for i in data_update:
                progress_s += progress_in
                if data_update[i] == True:
                    file_name = i.split('/')[-1]
                    updates_file = requests.get(f"https://raw.githubusercontent.com/69BooM96/Test-Finder/{i}").text
                    with open(file_name, "w", encoding="utf-8") as updates_f:
                        updates_f.write(updates_file)

                    self.progress_update_signal.emit(progress_s, file_name, 0)
            self.progress_update_signal.emit(100, "Start", 1)


#Update
class ExampleApp(QtWidgets.QMainWindow, update.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        path = 'res/g1.gif'
        gif = QtGui.QMovie(path)
        self.label.setMovie(gif)
        gif.start()

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        #parser
        self.parser_n = update_p(mainwindows=self)
        self.parser_n.progress_update_signal.connect(self.update_start)
        
        self.drivers_update()

    def mousePressEvent(self, event):         
        if event.button() == QtCore.Qt.LeftButton:
            self.old_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.old_pos = None

    def mouseMoveEvent(self, event):
        if not self.old_pos:
            return
        delta = event.pos() - self.old_pos
        self.move(self.pos() + delta)

    def update_start(self, value, text_progress, start_files):
        self.progressBar.setValue(value)
        self.label_2.setText(text_progress)
        if start_files == 1:
            os.startfile("Test-Finder.py")
            time.sleep(1)
            exit()

    def drivers_update(self):
        computer = wmi.WMI()
        os_info = computer.Win32_OperatingSystem()[0]
        OS_Architecture = os_info.OSArchitecture

        




        with open('data/settings.json') as f:
            data = json.load(f)

        data['Architecture'] = OS_Architecture
        data['Firefox_v'] = 
        data['Google_v'] = 

        with open('data/settings.json', 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        self.parser_n.start()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()