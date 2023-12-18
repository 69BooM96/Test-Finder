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
from win32com.client import Dispatch
import lxml
import re
import zipfile



class update_p(QThread):
    progress_update_signal = QtCore.pyqtSignal(int, str, int)

    def __init__(self, mainwindows):
        super().__init__()
        self.mainwindows = mainwindows

    def run(self):
        self.progress_update_signal.emit(10, "CHECK DRIVERS", 0)

        with open("data/settings.json", "r", encoding="utf-8") as settings_r:
            settings = json.load(settings_r)

        with open("drivers/x32/version_chromedriver.info", "r", encoding="utf-8") as versin_crome_r:
            versin_crome_info = versin_crome_r.read()

        if settings["Google_v"] != False:
            if versin_crome_info != settings["Google_v"]:
                self.progress_update_signal.emit(15, "INSTALLING UPDATE Chromedriver", 0)
                crome_v = requests.get("https://chromedriver.chromium.org/downloads")
                soup = BeautifulSoup(crome_v.content, "lxml")

                s1 = soup.find("div", class_="tyJCtd mGzaTb Depvyb baZpAe")
                s2 = s1.find_all("a", class_="XqQF9c")
                for i in s2:
                    ir = i.get("href")
                    if re.search(r'\bpath=\b', f"{ir}"):
                        if re.search(fr'\b{settings["Google_v"]}\b', f"{ir}"):
                            break

                ir = ir.replace("index.html?path=", "")

                crome_d = requests.get(f"{ir}chromedriver_win32.zip", allow_redirects=True)
                with open(f"drivers/x32/chromedriver_win32.zip", "wb") as crome_r:
                    crome_r.write(crome_d.content)

                file_open = zipfile.ZipFile("drivers/x32/chromedriver_win32.zip", "r")
                file_open.extractall("drivers/x32/")

                with open("drivers/x32/version_chromedriver.info", "w", encoding="utf-8") as version_d:
                    version_d.write(settings["Google_v"])

        self.progress_update_signal.emit(20, "CHECK FOR UPDATES", 0)
        version = requests.get("https://raw.githubusercontent.com/69BooM96/Test-Finder/main/version.info").text
        with open("version.info", "r", encoding="utf-8") as version_read:
            version_p = version_read.read()

        if version != version_p:
            updates = requests.get("https://raw.githubusercontent.com/69BooM96/Test-Finder/main/update.json").text
            updates = updates.replace("\n", "")
            with open("update.json", "w", encoding="utf-8") as updates_w:
                updates_w.write(updates)

            with open("update.json", "r", encoding="utf-8") as updates_r:
                data_update = json.load(updates_r)

            progress_in = 80//len(data_update)
            progress_s = 20
            num_up = len(data_update)
            num_down = 0

            for i in data_update:
                num_down += 1
                progress_s += progress_in
                if data_update[i] == True:
                    file_name = i.split('/')[-1]
                    updates_file = requests.get(f"https://raw.githubusercontent.com/69BooM96/Test-Finder/{i}").text
                    with open(file_name, "w", encoding="utf-8") as updates_f:
                        updates_f.write(updates_file)

                    self.progress_update_signal.emit(progress_s, f"INSTALLING UPDATE {num_down} OF {num_up}", 0)
            self.progress_update_signal.emit(100, "STARTING...", 1)


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
        try:
            filepath = r'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
            parser = Dispatch("Scripting.FileSystemObject")
            version = parser.GetFileVersion(filepath)
            ver = version.split('.')[-1]
            versions_c = version.replace(f".{ver}", "")
        except:
            try:
                filepath = r'C:/Program Files/Google/Chrome/Application/chrome.exe'
                parser = Dispatch("Scripting.FileSystemObject")
                version = parser.GetFileVersion(filepath)
                ver = version.split('.')[-1]
                versions_c = version.replace(f".{ver}", "")
            except:
                versions_c = False

        try:
            filepath_f = r'C:/Program Files (x86)/Mozilla Firefox/firefox.exe'
            parser_f = Dispatch("Scripting.FileSystemObject")
            version_f = parser_f.GetFileVersion(filepath_f)
            ver_f = version_f.split('.')[-1]
            versions_f = version_f.replace(f".{ver_f}", "")
            OS_Architecture = "32"
        except:
            try:
                filepath_f = r'C:/Program Files/Mozilla Firefox/firefox.exe'
                parser_f = Dispatch("Scripting.FileSystemObject")
                version_f = parser_f.GetFileVersion(filepath_f)
                ver_f = version_f.split('.')[-1]
                versions_f = version_f.replace(f".{ver_f}", "")
                OS_Architecture = "64"
            except:
                versions_f = False

        with open('data/settings.json') as f:
            data = json.load(f)

        data['Architecture'] = OS_Architecture
        data['Firefox_v'] = versions_f
        data['Google_v'] = versions_c

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