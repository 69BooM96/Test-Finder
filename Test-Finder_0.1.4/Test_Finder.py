from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileSystemModel, QListWidgetItem, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread
import GUI_

import os
import time
from time import perf_counter
from datetime import datetime
import sys
import json
from PIL import Image
from fuzzywuzzy import fuzz

from bs4 import BeautifulSoup
import requests
import webbrowser
import aiohttp
import asyncio
import aiofiles
import multiprocessing
from lxml import html
import re
import psutil


#info update
class info_update_p(QThread):
    info_update_textbrowser = QtCore.pyqtSignal(str)

    def __init__(self, mainwindows):
        QThread.__init__(self)
        self.mainwindows = mainwindows

    def run(self):
        version_ = "0.1.4\n"
        try:
            info_update_req = requests.get("https://raw.githubusercontent.com/69BooM96/Test-Finder/main/version.info")
            self.info_update_textbrowser.emit('<p style=" font-size:12pt; font-weight:600;">None update ¯\\_(ツ)_/¯</p>')
            if info_update_req.text != version_:
                info_update_text = requests.get("https://raw.githubusercontent.com/69BooM96/Test-Finder/main/info_v")
                self.info_update_textbrowser.emit(info_update_text.text)
        except:
            self.info_update_textbrowser.emit('''<p style=" font-size:12pt; font-weight:600;">ERROR ¯\\_(ツ)_/¯</p>
<br/>
<p style=" font-size:10pt; font-weight:600;">Немає підключення до Інтернету</p>
<p style=" font-size:8pt; font-weight:600;">Спробуйте зробити таке:</p>
<p style=" margin-left:20px; font-size:8pt;">Перевірте мережні кабелі, модем та маршрутизатор.</p>
<p style=" margin-left:20px; font-size:8pt;">Підключіться до мережі Wi-Fi ще раз.</p>
<p style=" margin-left:20px; font-size:8pt;">Виконайте діагностику мережі</p>
<p style=" ">ERR_INTERNET_DISCONNECTED</p>''')
        

#Search text
class search_html(QThread):
    search_html_end = QtCore.pyqtSignal(list, int)

    def __init__(self, mainwindows):
        QThread.__init__(self)
        self.mainwindows = mainwindows

    def run(self):
        search_result = []
        search_result_final = -1
        try:
            for html_file_num in range(len(self.mainwindows.array_tests)):
                line_search_result = 0
                with open(f"temp_data/read_html/index{html_file_num}.html", "r", encoding="utf-8") as read_html_test:
                    read_html = read_html_test.read().splitlines()

                for read_html_line in read_html:
                    line_search_result += 1
                    if re.findall(self.mainwindows.lineEdit_3.text(), read_html_line):
                        search_result_final += 1
                        search_result.append({
                            "html_file": html_file_num,
                            "line": line_search_result
                            })

            self.search_html_end.emit(search_result, search_result_final)
        except:
            pass

#Image
class download_image(QThread):
    progress_signal = QtCore.pyqtSignal(int)
    progress_update_signal_2 = QtCore.pyqtSignal(str)

    def __init__(self, mainwindows):
        QThread.__init__(self)
        self.mainwindows = mainwindows

    def run(self):
        self.progress_signal.emit(5)
        inputs_num = self.mainwindows.list_num
        multiprocessing.Process(target=self.download_im(inputs_num), name="download_image").start()
        self.progress_signal.emit(0)

    def download_im(self, inputs_num):
        async def download_img(link_image_url, num_url_img):
            try:
                link_img_name = link_image_url.split('/')[-1]

                async with aiohttp.ClientSession() as session:
                    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
                    async with session.get(link_image_url, headers=header, proxy=None, allow_redirects=True) as response:
                        contents_1 = response

                        async with aiofiles.open(f"temp_data/images/{link_img_name}", "wb") as while_img:
                            async for chunk in response.content.iter_chunked(64 * 1024):
                                await while_img.write(chunk)

                        img_obj = Image.open(f"temp_data/images/{link_img_name}")
                        img_obj = img_obj.resize((200, 200), Image.LANCZOS)
                        img_obj.save(f"temp_data/images/{link_img_name}")

                self.progress_update_signal_2.emit(f"[INFO] [Image] [url_img] [{link_image_url}]")
            except:
                self.progress_update_signal_2.emit(f"[ERROR] [Image] [url_img] [{link_image_url}]")
                

        async def main(inputs_num):
            async with aiofiles.open(f"temp_data/read_html/index{inputs_num}.html", "r", encoding="utf-8") as read_asins:
                read_html = await read_asins.read()

            soup = BeautifulSoup(read_html, "lxml")
            image_url = soup.find_all(class_="question-view-item-image")
            image_url_question = soup.find_all(class_="option-image")
            links_img = []
            for img in image_url:
                image_link = img.get("src")
                if re.search(r'\bhttps\b', image_link):
                    image_link_1 = image_link.split('/')[-1]
                    image_link_repl = image_link.replace(image_link_1, '')
                    links_img.append(image_link)
                    async with aiofiles.open(f"temp_data/read_html/index{inputs_num}.html", "r", encoding="utf-8") as read_asins:
                        read_html = await read_asins.read()
                    wr_html = read_html.replace(image_link_repl, "temp_data/images/")
                    async with aiofiles.open(f"temp_data/read_html/index{inputs_num}.html", "w", encoding="utf-8") as while_asins:
                        await while_asins.write(wr_html)

            async with aiofiles.open(f"temp_data/read_html/index{inputs_num}.html", "r", encoding="utf-8") as read_asins:
                read_html_question = await read_asins.read()

            for img_question in image_url_question:
                image_link = img_question.get("src")
                if re.search(r'\bhttps\b', image_link):
                    image_link_1 = image_link.split('/')[-1]
                    image_link_repl = image_link.replace(image_link_1, '')
                    links_img.append(image_link)
                    async with aiofiles.open(f"temp_data/read_html/index{inputs_num}.html", "r", encoding="utf-8") as read_asins:
                        read_html = await read_asins.read()
                    wr_html_2 = read_html.replace(image_link_repl, "temp_data/images/")
                    async with aiofiles.open(f"temp_data/read_html/index{inputs_num}.html", "w", encoding="utf-8") as while_asins:
                        await while_asins.write(wr_html_2)

            links_imgs = list(dict.fromkeys(links_img))

            if len(links_imgs) != 0:
                update_num = 95 // len(links_imgs)
                self.progress_update_signal_2.emit(f"[INFO] [Image]: [{len(links_imgs)}]")
            else:
                update_num = 95
                self.progress_update_signal_2.emit(f"[INFO] [Image]: [None]")
            
            tasks = []
            num_url_img = 5
            for link_image_url in links_imgs:
                tasks.append(asyncio.create_task(download_img(link_image_url, num_url_img)))
                num_url_img += update_num
                self.progress_signal.emit(num_url_img)

            await asyncio.gather(*tasks)


        if __name__ == '__main__':
            multiprocessing.freeze_support()
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            asyncio.run(main(inputs_num))

#Parser
class Parser(QThread):
    progress_update_signal = QtCore.pyqtSignal(str)
    list_update_signal = QtCore.pyqtSignal(int, str, int, str)
    progressbar_update_parser = QtCore.pyqtSignal(int)

    def __init__(self, mainwindows):
        QThread.__init__(self)
        self.mainwindows = mainwindows

    def run(self):
        clear_image = os.listdir("temp_data/images")
        for clear_image_d in clear_image:
            os.remove(f"temp_data/images/{clear_image_d}")

        inputs_text = self.mainwindows.lineEdit.text()
        self.progress_update_signal.emit(f"")
        self.progress_update_signal.emit(f"[INFO] [start][{inputs_text}]")
        multiprocessing.Process(target=self.test_t(inputs_text), name="parser_html").start()
        self.progress_update_signal.emit(f"[INFO] [end][{self.search_time}]\n")
        self.mainwindows.search_test = False
        self.mainwindows.pushButton.setEnabled(True)
        self.mainwindows.update_history()
        self.progressbar_update_parser.emit(0)

    def test_t(self, inputs_text):
        async def download_html(url_link, num_link, contents_1, inputs_text):
            try:
                async with aiohttp.ClientSession() as session:
                    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

                    async with session.get(url_link, headers=header, proxy=None) as response:
                        contents_1 = await response.text()

                    async with aiofiles.open(f"temp_data/read_html/index{num_link}.html", "w", encoding="utf-8") as while_asins:
                        await while_asins.write('<p style=" font-size:12pt; font-weight:600;">404 сторінка не знайдена ¯\\_(ツ)_/¯')
                    try:
                        soup = BeautifulSoup(contents_1, "lxml")
                        num_t = soup.find_all("div", class_="block-head")
                        for num_t2 in num_t:
                            num_t3 = num_t2.text.replace(" запитань", "")
                            num_t4 = num_t3.replace(" запитання", "")

                        test_search_1 = soup.find("div", class_="col-md-9 col-sm-8")
                        test_search_2 = test_search_1.find_all("div", class_="content-block entry-item question-view-item")

                        test_search_num = []
                        test_search_text = ""
                        for test_search_3 in test_search_2:
                            test_search_text += str(test_search_3)
                            test_search_4 = test_search_3.find("div", class_="question-view-item-content")
                            test_search_4 = test_search_4.text.replace("\n", "")
                            test_search_num.append(fuzz.WRatio(inputs_text, test_search_4))

                        test_search_text = test_search_text.replace(' width="100%"/>', '/>')
                        async with aiofiles.open(f"temp_data/read_html/index{num_link}.html", "w", encoding="utf-8") as while_asins:
                            await while_asins.write('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
.question-view-item-content{ font-family:'MS Shell Dlg 2'; font-size:10pt; background-color:#2f502c; font-weight:600;}
.col-md-9{ font-family:'MS Shell Dlg 2'; font-size:10pt; background-color:#2f502c; font-weight:600;}
.question-label{font-size:8pt; margin-top:48px}
.question-label-options{font-size:7pt;}
.option-text{font-size:9pt; font-weight:600; margin-left:20px;}
.image-only-option{margin-top:15px; margin-left:20px;}
</style>
</head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">\n''' + test_search_text + '</body></html>')

                        maxs = test_search_num[0]
                        for nums in range(1, len(test_search_num)):
                            if test_search_num[nums] > maxs:
                                maxs = test_search_num[nums]

                        self.list_update_signal.emit(num_link, num_t4, maxs, url_link)
                    except:
                        self.list_update_signal.emit(num_link, "Error", 0, url_link)

                    self.progressbar_update_num_s += self.progressbar_update
                    self.progressbar_update_parser.emit(self.progressbar_update_num_s)
                    self.progress_update_signal.emit(f"[INFO] [{num_link}] [url] [{url_link}]")
            except:
                self.progressbar_update_num_s += self.progressbar_update
                self.progressbar_update_parser.emit(self.progressbar_update_num_s)
                self.progress_update_signal.emit(f"[ERROR] [{num_link}] [url] [{url_link}]")
                self.list_update_signal.emit(num_link, "Error", 0, url_link)
                async with aiofiles.open(f"temp_data/read_html/index{num_link}.html", "w", encoding="utf-8") as while_asins:
                    await while_asins.write('''<p style=" font-size:12pt; font-weight:600;">ERROR ¯\\_(ツ)_/¯</p>
<br/>
<p style=" font-size:10pt; font-weight:600;">Немає підключення до Інтернету</p>
<p style=" font-size:8pt; font-weight:600;">Спробуйте зробити таке:</p>
<p style=" margin-left:20px; font-size:8pt;">Перевірте мережні кабелі, модем та маршрутизатор.</p>
<p style=" margin-left:20px; font-size:8pt;">Підключіться до мережі Wi-Fi ще раз.</p>
<p style=" margin-left:20px; font-size:8pt;">Виконайте діагностику мережі</p>
<p style=" ">ERR_INTERNET_DISCONNECTED</p>''')

        async def main(inputs_text):
            start = perf_counter()
            header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

            inputs_text = inputs_text.replace(" ", "+")
            link_l = "на+урок+тест+" + inputs_text

            links_bing = []
            links_google = []
            links_naurok = []

            #Bing
            try:
                resp = requests.get(f"https://www.bing.com/search?q={link_l}", headers=header)
                soup = BeautifulSoup(resp.content, "lxml")
                user_n = soup.find_all(class_="tilk")
                for links in user_n:
                    block = links.get("href")
                    if re.search(r'\bhttps://naurok.com.ua/test/\b', block):
                        if re.search(r'\b.html\b', block):
                            links_bing.append(block)

                self.progressbar_update_parser.emit(5)
                self.progress_update_signal.emit(f"[INFO] [Bing]: [{len(links_bing)}]")
            except:
                self.progressbar_update_parser.emit(5)
                self.progress_update_signal.emit(f"[ERROR] [Bing]")

            #Google
            try:
                resp = requests.get(f"https://www.google.com/search?q={link_l}", headers=header)
                soup = BeautifulSoup(resp.content, "lxml")
                user_n = soup.find(class_="dURPMd").find_all("a")
                for links in user_n:
                    block = links.get("href")
                    if re.search(r'\bhttps://naurok.com.ua/test/\b', block):
                        if re.search(r'\b.html\b', block):
                            links_google.append(block)

                self.progressbar_update_parser.emit(10)
                self.progress_update_signal.emit(f"[INFO] [Google]: [{len(links_google)}]")
            except:
                self.progressbar_update_parser.emit(10)
                self.progress_update_signal.emit(f"[ERROR] [Google]")

            try:
                for num_url in range(3):
                    async with aiohttp.ClientSession() as session:
                        header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
                        async with session.get(f"https://naurok.com.ua/test?q={inputs_text}&storinka={num_url}", headers=header, proxy=None) as response:
                            contents = await response.text()

                        soup = BeautifulSoup(contents, "lxml")
                        user_n = soup.find("div", class_="items")
                        user_n_2 = user_n.find_all("div", class_="file-item test-item")
                        for links in user_n_2:
                            links_2 = f'https://naurok.com.ua{links.find("div", class_="row").find("div", class_="headline").find("a").get("href")}'
                            if re.search(r'\bhttps://naurok.com.ua/test/\b', links_2):
                                if re.search(r'\b.html\b', links_2):
                                    links_naurok.append(links_2)

                self.progressbar_update_parser.emit(15)
                self.progress_update_signal.emit(f"[INFO] [Naurok]: [{len(links_naurok)}]")
            except:
                self.progressbar_update_parser.emit(15)
                self.progress_update_signal.emit(f"[ERROR] [Naurok]")


            links_browser = list(dict.fromkeys(links_google + links_bing + links_naurok))
            self.mainwindows.label_3.setText(f"{len(links_browser)}")
            self.progress_update_signal.emit(f"[INFO] [Links]: [{len(links_browser)}]")

            num_link = 0
            self.progressbar_update_num_s = 15
            if 85 < len(links_browser):
                self.progressbar_update = 1
                max_progressbar = len(links_browser) + 15
                self.mainwindows.progressBar.setMaximum(max_progressbar)
            else:
                if len(links_browser) != 0:
                    self.progressbar_update = 85 // len(links_browser)

            tasks = []
            contents_1 = ""
            for url_link in links_browser:
                tasks.append(asyncio.create_task(download_html(url_link, num_link, contents_1, inputs_text)))
                num_link += 1

            await asyncio.gather(*tasks)
            self.search_time = f"{(perf_counter() - start):.02f}"

        if __name__ == '__main__':
            multiprocessing.freeze_support()
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            asyncio.run(main(inputs_text))


#Menu
class ExampleApp(QtWidgets.QMainWindow, GUI_.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #Button
        self.pushButton.clicked.connect(self.search_question)
        self.pushButton_2.clicked.connect(self.open_browser_test)
        self.pushButton_9.clicked.connect(self.open_url_update_checked)

        self.radioButton_6.clicked.connect(self.sort_start)
        self.radioButton_5.clicked.connect(self.sort_start)
        self.radioButton_3.clicked.connect(self.sort_start)
        self.radioButton_2.clicked.connect(self.sort_start)
        self.radioButton_4.clicked.connect(self.sort_start)

        #<>
        self.pushButton_7.clicked.connect(self.update_search_html_left)
        self.pushButton_10.clicked.connect(self.update_search_html_right)


        #Edit
        self.lineEdit.returnPressed.connect(self.search_question)
        self.search_test = False
        self.lineEdit_3.returnPressed.connect(self.start_search_text_html)

        #List
        self.listWidget_3.clicked.connect(self.read_history)
        self.listWidget_2.doubleClicked.connect(self.open_browser_test)
        self.listWidget_2.clicked.connect(self.possible_answers_clicked)

        #Update start
        self.update_history()
        self.data_log("")
        self.data_log("[INFO] [Start_program]\n")

        #Parser
        self.search_parser = Parser(mainwindows=self)
        self.search_parser.progress_update_signal.connect(self.data_log)
        self.search_parser.list_update_signal.connect(self.list_link_2)
        self.search_parser.progressbar_update_parser.connect(self.progressbar_update_n)

        #Images
        self.images_p = download_image(mainwindows=self)
        self.images_p.progress_signal.connect(self.update_image)
        self.images_p.progress_update_signal_2.connect(self.data_log)

        #Search
        self.search_html_parser = search_html(mainwindows=self)
        self.search_html_parser.search_html_end.connect(self.update_search_html)

        #Update_parser
        self.checked_update = info_update_p(mainwindows=self)
        self.checked_update.info_update_textbrowser.connect(self.update_checked_set)
        self.checked_update.start()

    def open_url_update_checked(self):
        webbrowser.open_new_tab("https://github.com/69BooM96/Test-Finder/tags")

    def update_checked_set(self, text_info):
        self.textBrowser_5.setText(text_info)

    #connect Button
    def search_question(self):
        if self.search_test == True:
            pass
        else:
            self.array_tests = []
            self.search_test = True
            self.pushButton.setEnabled(False)
            self.update_history()
            self.label_3.setText("0")
            self.listWidget_2.clear()
            self.num_ts = self.spinBox_5.value()
            self.search_parser.start()

    def progressbar_update_n(self, progress_num):
        self.progressBar.setValue(progress_num)

    #Search_text_html

    def update_search_html(self, list_res, number_matches_1):
        try:
            self.search_html_res_num = 0
            self.number_matches = number_matches_1
            if number_matches_1 == -1:
                self.label_16.setText(f"{self.search_html_res_num}/{number_matches_1+1}")
            else:
                self.label_16.setText(f"{self.search_html_res_num+1}/{number_matches_1+1}")

            self.search_html_res = list_res
            self.update_search_html_set()
        except:
            pass

    def update_search_html_set(self):
        try:
            list_num_sort = self.search_html_res[self.search_html_res_num]['html_file']
            list_line_sort = self.search_html_res[self.search_html_res_num]['line']
            self.list_num = list_num_sort

            for url_sort_list in self.scan_array_tests:
                if url_sort_list['html'] == list_num_sort:
                    url_sort = url_sort_list['urls_test']
                    break

            self.lineEdit_4.setText(url_sort)
            self.data_log(f'[INFO] [HTML] [url_test] [{url_sort}]')
            if self.pushButton_5.isChecked() == True:
                self.images_p.start()

            with open(f"temp_data/read_html/index{list_num_sort}.html", "r", encoding="utf-8") as read_html_test:
                read_html = read_html_test.read()
            self.textEdit_3.setHtml(read_html)
            self.vbar_search = self.textEdit_3.verticalScrollBar()
            list_line_sort_x = list_line_sort*7
            self.vbar_search.setValue(list_line_sort_x)
        except:
            pass

    def update_search_html_left(self):
        try:
            if self.search_html_res_num > 0:
                self.search_html_res_num -= 1
                self.label_16.setText(f"{self.search_html_res_num+1}/{self.number_matches+1}")
                self.update_search_html_set()
        except:
            pass

    def update_search_html_right(self):
        try:
            if self.search_html_res_num < self.number_matches:
                self.search_html_res_num += 1
                self.label_16.setText(f"{self.search_html_res_num+1}/{self.number_matches+1}")
                self.update_search_html_set()
        except:
            pass

    def start_search_text_html(self):
        self.search_html_parser.start()

    def sort_start(self):
        try:
            if self.radioButton_6.isChecked() == True:
                self.scan_array_tests = self.array_tests

            if self.radioButton_5.isChecked() == True:
                self.scan_array_tests = sorted(self.array_tests, key=lambda user: user['num_test'], reverse=self.radioButton_4.isChecked())

            if self.radioButton_3.isChecked() == True:
                self.scan_array_tests = sorted(self.array_tests, key=lambda user: user['similarity'], reverse=self.radioButton_4.isChecked())

            self.listWidget_2.clear()

            for scan_array_list in self.scan_array_tests:
                if scan_array_list['num_test'] != "Error":
                    if self.num_ts == int(scan_array_list['num_test']):
                        brush = QtGui.QBrush(QtGui.QColor(44, 62, 44))
                        if 89 < scan_array_list['similarity']:
                            brush = QtGui.QBrush(QtGui.QColor(34, 92, 44))
                    else:
                        brush = QtGui.QBrush(QtGui.QColor(24, 32, 24))
                        if 89 < scan_array_list['similarity']:
                            brush = QtGui.QBrush(QtGui.QColor(44, 62, 44))

                    item = QtWidgets.QListWidgetItem()
                    self.listWidget_2.addItem(item)
                    brush.setStyle(QtCore.Qt.SolidPattern)
                    item.setBackground(brush)
                    item.setText(f"[Запитань]: [{scan_array_list['num_test']}] [Схожість]: [{scan_array_list['similarity']}%]")
                else:
                    brush = QtGui.QBrush(QtGui.QColor(134, 32, 24))
                    item = QtWidgets.QListWidgetItem()
                    self.listWidget_2.addItem(item)
                    brush.setStyle(QtCore.Qt.SolidPattern)
                    item.setBackground(brush)
                    item.setText("Error")
        except:
            pass

    def open_browser_test(self):
        if self.listWidget_2.currentItem().text() != "":
            for item2 in self.listWidget_2.selectedIndexes():
                webbrowser.open_new_tab(self.scan_array_tests[item2.row()]['urls_test'])

    #connect List
    def update_image(self, progress):
        self.progressBar_4.setValue(progress)
        if progress == 0:
            with open(f"temp_data/read_html/index{self.list_num}.html", "r", encoding="utf-8") as read_html_test:
                read_html = read_html_test.read()
            read_html = read_html.replace("</p><p><br/>", "")
            self.textEdit_3.setHtml(read_html)

    def possible_answers_clicked(self):
        if self.listWidget_2.currentItem().text() != "":
            for item2 in self.listWidget_2.selectedIndexes():
                self.list_num = self.scan_array_tests[item2.row()]['html']
                self.lineEdit_4.setText(self.scan_array_tests[item2.row()]['urls_test'])
                self.data_log(f'[INFO] [HTML] [url_test] [{self.scan_array_tests[item2.row()]["urls_test"]}]')
                if self.pushButton_5.isChecked() == True:
                    self.images_p.start()

                with open(f"temp_data/read_html/index{self.list_num}.html", "r", encoding="utf-8") as read_html_test:
                    read_html = read_html_test.read()
                read_html = read_html.replace("</p><p><br/>", "")
                self.textEdit_3.setHtml(read_html)

    def update_history(self):
        self.listWidget_3.clear()
        files = os.listdir("logs")
        for history in files:
            item = QtWidgets.QListWidgetItem()
            self.listWidget_3.addItem(item)
            item.setText(f"{history}")

    def read_history(self):
        item = self.listWidget_3.currentItem().text()
        with open(f"logs/{item}", "r", encoding="utf-8") as read_logs:
            self.textBrowser_6.setText(read_logs.read())

    #List update
    def list_link_2(self, num_item, test_info_num, similarity_test, urls_test):
        self.array_tests.append({
            "similarity": similarity_test,
            "num_test": test_info_num,
            "html": num_item,
            "urls_test": urls_test
            })

        self.sort_start()

    #logs
    def data_log(self, info_log):
        self.data_d = time.strftime('%Y-%m-%d')
        self.data_t = time.strftime(f'%H:%M:%S')
        info_log = info_log.replace("\n", "")
        if info_log == '':
            with open(f"logs/{self.data_d}.log", "a", encoding="utf-8") as write_log:
                write_log.write(f"\n")
            self.textEdit_4.append(f"\n")

        else:
            with open(f"logs/{self.data_d}.log", "a", encoding="utf-8") as write_log:
                write_log.write(f"[{self.data_t}] {info_log}\n")
            self.textEdit_4.append(f"[{self.data_t}] {info_log}")

        self.vbar = self.textEdit_4.verticalScrollBar()
        
        max_v = 0
        for num_log in self.textEdit_4.toPlainText():
            max_v += 1
        self.vbar.setValue(max_v)


def main():
    start_core = 0

    for proc in psutil.process_iter():
        name = proc.name()
        if name == "Test_Finder.exe":
            start_core += 1

    if start_core < 2:
        app = QtWidgets.QApplication(sys.argv)
        window = ExampleApp()
        window.show()
        app.exec_()
    else:
        pass
    
if __name__ == '__main__':
    main()