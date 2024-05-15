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

from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import webbrowser
import aiohttp
import asyncio
import aiofiles
import multiprocessing
import lxml
import fake_useragent
import re
import psutil
import winapps
import requests
import pyperclip

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


#Get answers test (auto)
class Get_answers_test_auto(QThread):
    log_signal = QtCore.pyqtSignal(str, str)
    index_signal = QtCore.pyqtSignal(str)
    def __init__(self, mainwindows):
        QThread.__init__(self)
        self.mainwindows = mainwindows

    def run(self):
        join_test_url = ""
        try:
            join_test_url = f"https://naurok.com.ua/test/join?gamecode={self.mainwindows.gamecode_test}"

            usr_ = UserAgent()
            header = {'user-agent': f'{usr_.random}'}

            session_join = requests.Session()
            test_join = session_join.get(join_test_url, headers=header)
            soup = BeautifulSoup(test_join.text, "lxml")
            csrf_token = soup.find('input', {'name': '_csrf'})['value']

            data_join = {"_csrf": csrf_token,
                    "JoinForm[gamecode]": self.mainwindows.gamecode_test,
                    "JoinForm[name]": f"{self.mainwindows.user_name_test}"}

            header_join = {'user-agent': f'{usr_.random}',
                      'Referer': 'https://naurok.com.ua/test/join',
                      'Origin': 'https://naurok.com.ua'}

            test_join_start = session_join.post(join_test_url, headers=header_join, data=data_join)
            test_one_ = session_join.get(test_join_start.url, headers=header)
            soup = BeautifulSoup(test_one_.text, "lxml")

            ng_init_value = soup.find('div', attrs={'ng-init': True}).get('ng-init', '')
            value = ng_init_value.split(',')[1].strip()            

            #json
            questions_full = session_join.get(f"https://naurok.com.ua/api2/test/sessions/{value}", headers=header)
            self.mainwindows.list_question = questions_full.json()

            self.index_signal.emit("set_")
            self.log_signal.emit(f'[INFO] [Test join]: [url][<span style="color:#1AA8DD;">{join_test_url}</span>] [gamecode][{self.mainwindows.gamecode_test}]', "INFO_1")
            self.log_signal.emit(f'[INFO] [Test join]: [url][<span style="color:#1AA8DD;">{test_join_start.url}</span>]', "INFO_1")

            while True:
                if self.mainwindows.continue_answers_auto == True:
                    break
                time.sleep(1)

            for answers_urls in self.mainwindows.url_auto_test:
                self.log_signal.emit(f'[INFO] [Answers]: [{len(self.mainwindows.url_auto_test)}]', "INFO_1")
                self.log_signal.emit(f'[INFO] [Answers]: [url][<span style="color:#1AA8DD;">{answers_urls}</span>]', "INFO_1")

        except:
            self.index_signal.emit("ERROR")
            self.log_signal.emit(f'[ERROR] [Test join]: [url][<span style="color:#1AA8DD;">{join_test_url}</span>] [gamecode][{self.mainwindows.gamecode_test}]', "ERROR")

#Search test (auto)
class Search_test_auto(QThread):
    log_signal = QtCore.pyqtSignal(str, str)
    progress_signal = QtCore.pyqtSignal(int)
    def __init__(self, mainwindows):
        QThread.__init__(self)
        self.mainwindows = mainwindows

    def run(self):
        #start
        self.start_time = perf_counter()
        self.log_signal.emit(f"[start]: [auto]", "INFO_1")
        self.progress_signal.emit(5)
        with open("data/settings.json", "r", encoding="utf-8") as settings_r:
            self.settings_loads = json.load(settings_r)

        multiprocessing.Process(target=self.auto_test_search_()).start()

        self.progress_signal.emit(0)
        search_time = f"{(perf_counter() - self.start_time):.02f}"
        self.log_signal.emit(f"[end]: [{search_time}]\n<br>", "INFO_1")
        self.mainwindows.progressBar.setMaximum(100)

    def auto_test_search_(self):
        async def naurok_(num_url, header, session):
            try:
                async with session.get(f"https://naurok.com.ua/test?q={self.inputs_txt}&storinka={num_url}", headers=header, proxy=None) as response:
                    contents = await response.text()

                soup = BeautifulSoup(contents, "lxml")
                user_n = soup.find("div", class_="items")
                user_n_2 = user_n.find_all("div", class_="file-item test-item")
                for links in user_n_2:
                    link_n = f'https://naurok.com.ua{links.find("div", class_="row").find("div", class_="headline").find("a").get("href")}'
                    if re.search(r'\bhttps://naurok.com.ua/test/\b', link_n):
                        if re.search(r'\b.html\b', link_n):
                            self.links_naurok.append(link_n)

                self.log_signal.emit(f"[INFO] [Naurok]: [page][{num_url}]", "INFO_0")
            except:
                self.log_signal.emit(f"[ERROR] [Naurok]: [page][{num_url}]", "ERROR")

        async def google_(num_url, header, session):
            try:
                async with session.get(f"https://www.google.com/search?q=на+урок+{self.inputs_txt}&start={num_url}0&sa=N", headers=header, proxy=None) as response:
                    contents = await response.text()

                soup = BeautifulSoup(contents, "lxml")
                user_n = soup.find(class_="dURPMd").find_all("a")
                for links in user_n:
                    block = links.get("href")
                    if re.search(r'\bhttps://naurok.com.ua/test/\b', block):
                        if re.search(r'\b.html\b', block):
                            self.links_google.append(block)

                self.log_signal.emit(f"[INFO] [Google]: [page][{num_url}]", "INFO_0")
            except:
                self.log_signal.emit(f"[ERROR] [Google]: [page][{num_url}]", "ERROR")

        async def bing_(num_url, header, session):
            try:
                async with session.get(f"https://www.bing.com/search?q=на+урок+{self.inputs_txt}+&first={num_url}0&FORM=PERE", headers=header, proxy=None) as response:
                    contents = await response.text()

                soup = BeautifulSoup(contents, "lxml")
                user_n = soup.find_all(class_="tilk")
                for links in user_n:
                    block = links.get("href")
                    if re.search(r'\bhttps://naurok.com.ua/test/\b', block):
                        if re.search(r'\b.html\b', block):
                            self.links_bing.append(block)

                self.log_signal.emit(f"[INFO] [Bing]: [page][{num_url}]", "INFO_0")
            except:
                self.log_signal.emit(f"[ERROR] [Bing]: [page][{num_url}]", "ERROR")

        async def load_links_(num_url, header, url, session):
            try:
                for url_answer_auto in self.list_test_ansver:
                    if url_answer_auto['url'] == url:
                        self.log_signal.emit(f'[INFO] [Test]: [continue] [num][{num_url}] | [url][<span style="color:#1AA8DD;">{url}</span>]', "INFO_0")
                        break

                async with session.get(url, headers=header, proxy=None) as response:
                    contents = await response.text()
                try:
                    soup = BeautifulSoup(contents, "lxml")
                    num_t = soup.find("div", class_="block-head").text
                    num_t3 = num_t.replace(" запитань", "")
                    num_t4 = num_t3.replace(" запитання", "")

                    test_search_1 = soup.find("div", class_="col-md-9 col-sm-8")
                    test_search_2 = test_search_1.find_all("div", class_="content-block entry-item question-view-item")

                    test_search_num = 0
                    list_question_test = []
                    test_search_text = ""
                    index_num_question = 0
                    for item_text_question in self.mainwindows.list_question_content:
                        test_search_num_question = []
                        for test_search_3 in test_search_2:
                            test_search_4 = test_search_3.find("div", class_="question-view-item-content")
                            test_search_4 = test_search_4.text.replace("\n", "")
                            fuzz_num_ = fuzz.WRatio(item_text_question, test_search_4)
                            test_search_num_question.append(fuzz_num_)
                            if fuzz_num_ > 85:
                                list_question_test.append(index_num_question)
                        test_search_num += max(test_search_num_question)
                        index_num_question += 1

                    list_question_test = list(dict.fromkeys(list_question_test))

                    self.list_status.append({
                        "num_q": int(num_t4),
                        "url": url,
                        "question": list_question_test,
                        "max_": test_search_num,
                        "ERROR": False
                        })

                    self.log_signal.emit(f'[INFO] [Test]: [num][{num_url}] | [url][<span style="color:#1AA8DD;">{url}</span>]', "INFO_0")
                except:
                    self.log_signal.emit(f"[ERROR] [Test]: [num][{num_url}] | [url][{url}]", "ERROR")
                    self.list_status.append({
                        "num_q": None,
                        "url": None,
                        "question": None,
                        "max_": None,
                        "ERROR": True
                        })
            except:
                self.update_list_.emit()
                self.log_signal.emit(f"[ERROR] [Test]: [num][{num_url}] | [url][{url}]", "ERROR")
                self.list_status.append({
                    "num_q": None,
                    "url": None,
                    "question": None,
                    "max_": None,
                    "ERROR": True
                    })

        async def search_async():
            self.list_test_ansver = []
            break_search = False
            for inf_text_ in self.mainwindows.list_question_content:
                if break_search != True:
                    self.list_status = []
                    time.sleep(5)
                    self.log_signal.emit(f"[start]: [auto][{inf_text_}]", "INFO_1")
                    self.inf_text_ = inf_text_
                    self.inputs_txt = inf_text_.replace(" ", "+")
                    self.links_naurok = []
                    self.links_google = []
                    self.links_bing = []

                    usr_ = UserAgent()
                    header = {'user-agent': f'{usr_.random}'}

                    async with aiohttp.ClientSession() as session:
                    #Naurok
                        tasks = []
                        for num_link in range(self.settings_loads['naurok_page']):
                            tasks.append(asyncio.create_task(naurok_(num_link, header, session)))

                        await asyncio.gather(*tasks)
                        self.log_signal.emit(f"[INFO] [Naurok]: [pages][{self.settings_loads['naurok_page']}] | [links][{len(self.links_naurok)}]", "INFO_1")
                        self.progress_signal.emit(10)

                    #Google
                        tasks = []
                        for num_link in range(self.settings_loads['google_page']):
                            tasks.append(asyncio.create_task(google_(num_link, header, session)))

                        await asyncio.gather(*tasks)
                        self.log_signal.emit(f"[INFO] [Google]: [pages][{self.settings_loads['google_page']}] | [links][{len(self.links_google)}]", "INFO_1")
                        self.progress_signal.emit(15)

                    #Bing
                        tasks = []
                        for num_link in range(self.settings_loads['bing_page']):
                            tasks.append(asyncio.create_task(bing_(num_link, header, session)))

                        await asyncio.gather(*tasks)
                        self.log_signal.emit(f"[INFO] [Bing]: [pages][{self.settings_loads['bing_page']}] | [links][{len(self.links_bing)}]", "INFO_1")
                        self.progress_signal.emit(20)


                        all_link_ = list(dict.fromkeys(self.links_naurok + self.links_google + self.links_bing))

                        self.log_signal.emit(f"[INFO] [All_no_sort]: [links][{len(self.links_google) + len(self.links_bing) + len(self.links_naurok)}]", "INFO_1")
                        self.log_signal.emit(f"[INFO] [All]: [links][{len(all_link_)}]", "INFO_1")

                    #Load link
                        tasks = []
                        num_link = 0

                        for url_link in all_link_:
                            tasks.append(asyncio.create_task(load_links_(num_link, header, url_link, session)))
                            num_link += 1

                        await asyncio.gather(*tasks)

                #sort test auto
                    for item_test in self.list_status:
                        if item_test['ERROR'] == False:
                            if item_test['max_'] > item_test['num_q'] * 98:
                                if item_test['num_q'] >= len(self.mainwindows.list_question_content):
                                    self.mainwindows.url_auto_test = [f"{item_test['url']}"]
                                    self.log_signal.emit(f'[INFO] [Test answer]: [questions][{item_test["num_q"]}] [score][{item_test["max_"]}] | [url][<span style="color:#1AA8DD;">{item_test["url"]}</span>]', "INFO_1")
                                    break_search = True
                                    break

                            if item_test['max_'] > item_test['num_q'] * 85:
                                self.log_signal.emit(f'[INFO] [Test]: [questions][{item_test["num_q"]}] [score][{item_test["max_"]}] | [url][<span style="color:#1AA8DD;">{item_test["url"]}</span>]', "INFO_0")
                                self.mainwindows.url_auto_test.append(item_test)
                                self.list_test_ansver.append(item_test)

            self.mainwindows.continue_answers_auto = True
            print(self.list_test_ansver)
            print(self.list_status)



        if __name__ == '__main__':
            multiprocessing.freeze_support()
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            asyncio.run(search_async())

#Get answers
class Get_answers_test(QThread):
    log_signal = QtCore.pyqtSignal(str, str)
    reload_browser_signal = QtCore.pyqtSignal(str)
    progress_bar_signal = QtCore.pyqtSignal(int)
    def __init__(self, mainwindows):
        QThread.__init__(self)
        self.mainwindows = mainwindows

    def run(self):
        if self.mainwindows.url_test_reload != None:
            if self.mainwindows.login_ok == True:
                self.start_time = perf_counter()
                self.log_signal.emit(f'[start] [Get answers]: [url][<span style="color:#1AA8DD;">{self.mainwindows.url_test_reload}</span>]', "INFO_1")
                self.restart_request = 0
                self.progress_bar_signal.emit(15)
                self.parser_answers()

    def parser_answers(self):
        if self.restart_request < 3:
            self.restart_request += 1
            session = requests.Session()
            data_user_time = time.strftime('%H %M %S')
            try:
                usr_ = UserAgent()
                header = {'user-agent': f'{usr_.random}'}

                with open("data/cookies", "r") as read_file:
                    data_r = json.load(read_file)

                for cookie in data_r:
                    session.cookies.set(cookie['name'], cookie['value'])

                test_create_1 = session.get(self.mainwindows.url_test_reload, headers=header)
                soup = BeautifulSoup(test_create_1.text, "lxml")
                href_value = soup.find('a', class_='test-action-button')['href']

                test_create_2 = session.get(f'https://naurok.com.ua{href_value}', headers=header)
                soup = BeautifulSoup(test_create_2.text, "lxml")
                blok = soup.find_all('input', attrs={'name': '_csrf'})

                year = datetime.now().year
                month = datetime.now().month
                day = datetime.now().day + 1

                if month < 10:
                    month = f"0{month}"
                if day < 9:
                    day = f"0{day+1}"

                data = {
                    '_csrf': blok[1]["value"],
                    'Homework[name]': f'home y{year}m{month}d{day}{data_user_time}',
                    'Homework[deadline_day]': f'{year}-{month}-{day}',
                    'Homework[deadline_hour]': '18:00',
                    'Homework[shuffle_question]': '0',
                    'Homework[shuffle_options]': '1',
                    'Homework[show_answer]': '0',
                    'Homework[show_review]': '1',
                    'Homework[show_leaderbord]': '1',
                    'Homework[available_attempts]': '0',
                    'Homework[duration]': '40',
                    'Homework[show_timer]': '0',
                    'Homework[show_flashcard]': '0',
                    'Homework[show_match]': '0'
                }

                test_create_3 = session.get(f'https://naurok.com.ua{href_value}', headers=header, data=data)
                soup = BeautifulSoup(test_create_3.text, "lxml")
                blok_url = soup.find(class_="form-control input-xs")
                join_test_url = blok_url["value"]
                gamecode = join_test_url.split('=')[-1]
                self.log_signal.emit(f'[INFO] [Test create]: [url][<span style="color:#1AA8DD;">{join_test_url}</span>] [gamecode][{gamecode}]', "INFO_0")
                self.progress_bar_signal.emit(45)

                #join test
                session_join = requests.Session()
                test_join = session_join.get(join_test_url, headers=header)
                soup = BeautifulSoup(test_join.text, "lxml")
                csrf_token = soup.find('input', {'name': '_csrf'})['value']

                data_join = {"_csrf": csrf_token,
                        "JoinForm[gamecode]": gamecode,
                        "JoinForm[name]": f"u{year}s{month}e{day}r{data_user_time}"}

                header_join = {'user-agent': f'{usr_.random}',
                          'Referer': 'https://naurok.com.ua/test/join',
                          'Origin': 'https://naurok.com.ua'}

                test_join_start = session_join.post(join_test_url, headers=header_join, data=data_join)
                self.log_signal.emit(f'[INFO] [Test join]: [url][<span style="color:#1AA8DD;">{test_join_start.url}</span>]', "INFO_0")
                self.progress_bar_signal.emit(75)
                test_one_ = session_join.get(test_join_start.url, headers=header)
                soup = BeautifulSoup(test_one_.text, "lxml")

                ng_init_value = soup.find('div', attrs={'ng-init': True}).get('ng-init', '')
                value = ng_init_value.split(',')[1].strip()            

                #json
                questions_full = session_join.get(f"https://naurok.com.ua/api2/test/sessions/{value}", headers=header)
                questions_data = questions_full.json()
       
                data_answer = questions_data['questions'][0]['options'][0]['id']
                data_question_id = questions_data['questions'][0]['id']
                data_type = questions_data['questions'][0]['type']
                data_point = questions_data['questions'][0]['point']

                data = {
                    "session_id": int(value),
                    "answer": [f"{data_answer}"],
                    "question_id": f"{data_question_id}",
                    "show_answer": "0",
                    "type": f"{data_type}",
                    "point": f"{data_point}",
                    "homeworkType": "1",
                    "homework": "true"
                }

                header = {
                    'user-agent': f'{usr_.random}',
                    'Referer': test_join_start.url,
                    'Origin': 'https://naurok.com.ua'
                }

                session.put(f"https://naurok.com.ua/api2/test/responses/answer", json=data, headers=header)
                session.put(f"https://naurok.com.ua/api2/test/sessions/end/{value}")
                url_answer = test_join_start.url.replace("https://naurok.com.ua/test/testing", "https://naurok.com.ua/test/complete")
                answers_html = session_join.get(url_answer, headers=header)
                self.log_signal.emit(f'[INFO] [Test answer]: [url][<span style="color:#1AA8DD;">{url_answer}</span>]', "INFO_0")
                search_time = f"{(perf_counter() - self.start_time):.02f}" 
                self.progress_bar_signal.emit(95)

                #Read answers
                soup = BeautifulSoup(answers_html.text, "lxml")
                content_block = soup.find("div", class_="homework-stats").find_all("div", class_="homework-stat-question-line")
                block_save_ = ""
                for item_block in content_block:
                    text_option_text_quiz = str(item_block)
                    #replase space
                    self.text_option_quiz_ = text_option_text_quiz.replace('<div class="option-text">\n<p> ', '<div class="option-text">\n<p>')
                    self.text_option_quiz_ = self.text_option_quiz_.replace(f'<div class="option-text">\n<p>  ', '<div class="option-text">\n<p>')
                    self.text_option_quiz_ = self.text_option_quiz_.replace(f'<div class="option-text">\n<p>   ', '<div class="option-text">\n<p>')
                    self.text_option_quiz_ = self.text_option_quiz_.replace(f'<div class="option-text">\n<p>    ', '<div class="option-text">\n<p>')
                    self.text_option_quiz_ = self.text_option_quiz_.replace(f' ', '')
                    self.text_option_quiz_ = self.text_option_quiz_.replace(f'<p><br/></p>', '')

                    for item_option_block in item_block.find_all("div", class_="homework-stat-option-line"):
                        if item_option_block.find("span", class_="correct quiz"):
                            self.text_option_quiz_ = self.text_option_quiz_.replace(f'{item_option_block.find("span", class_="correct quiz")} <p>', '<p><img src="res/quiz_.png"/> ')
                        if item_option_block.find("span", class_="incorect quiz"):
                            self.text_option_quiz_ = self.text_option_quiz_.replace(f'{item_option_block.find("span", class_="incorect quiz")} <p>', '<p><img src="res/quiz_.png"/> ')
                        if item_option_block.find("span", class_="correct multiquiz"):
                            self.text_option_quiz_ = self.text_option_quiz_.replace(f'{item_option_block.find("span", class_="correct multiquiz")} <p>', '<p><img src="res/multiquiz_.png"/> ')
                        if item_option_block.find("span", class_="incorect multiquiz"):
                            self.text_option_quiz_ = self.text_option_quiz_.replace(f'{item_option_block.find("span", class_="incorect multiquiz")} <p>', '<p><img src="res/multiquiz_.png"/> ')

                    self.text_option_quiz_ = self.text_option_quiz_.replace('<div class="homework-stat-option-value correct">', '<div class="homework-stat-option-value-correct">')
                    self.text_option_quiz_ = self.text_option_quiz_.replace('<div class="homework-stat-option-value incorect">', '<div class="homework-stat-option-value-incorect">')
                    self.text_option_quiz_ = self.text_option_quiz_.replace(f'{item_block.find("div", class_="question-label")}', '')
                    url_imgz = item_block.find_all("img")
                    for links_img in url_imgz:
                        if links_img.get("src"):
                            img_names = links_img.get("src").split('/')[-1]
                            self.text_option_quiz_ = self.text_option_quiz_.replace(f'<img src="{links_img.get("src")}" width="100%"/>', f'<img src="temp_data/images/{img_names}"/>')
                    
                    self.text_option_quiz_ += "<br/><br/>"
                    block_save_ += self.text_option_quiz_

                num_test_html = soup.find("div", class_="homework-personal-stat-number").text
                name_test_html = soup.find("div", class_="homework-personal-stat-test").text

                url_file_answer = f"temp_data/answers_html/_d{time.strftime('%Y-%m-%d')}_t{data_user_time}_g{gamecode}.html"
                with open(url_file_answer, "w", encoding="utf-8") as answers_save:
                    answers_save.write('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
                                                <html><head><meta name="qrichtext" content="1" /><style type="text/css">
                                                .homework-stat-question-line{background-color:#1E1F22; font-family:'MS Shell Dlg 2'; font-size:10pt; font-weight:600;}
                                                .homework-stat-option-value-correct{background-color:#454545;}
                                                .homework-stat-option-line{font-size:9pt; font-weight:600; margin-left:20px;}
                                                </style>
                                                </head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;"><p style="font-size:12pt; font-weight:800;">''' + f'| {num_test_html}<br/>| {name_test_html}<br/>| Test [{self.mainwindows.url_test_reload}]<br/>| {url_answer}</p><br/>\n' + block_save_ + '</body></html>')
                self.mainwindows.url_answer_open = url_answer
                self.reload_browser_signal.emit(url_file_answer)
                self.log_signal.emit(f'[end]: [{search_time}]', "INFO_1")
                self.progress_bar_signal.emit(0)
            except:
                self.log_signal.emit(f"[ERROR] [Get answers][{self.restart_request}]: [url][{self.mainwindows.url_test_reload}]", "ERROR")
                self.parser_answers()

#Reload page
class Reload_page_naurok(QThread):
    log_signal = QtCore.pyqtSignal(str, str)
    reload_browser_signal = QtCore.pyqtSignal()
    def __init__(self, mainwindows):
        QThread.__init__(self)
        self.mainwindows = mainwindows

    def run(self):
        if self.mainwindows.url_test_reload != None:
            try:
                contents = requests.get(self.mainwindows.url_test_reload)
                with open(self.mainwindows.file_read_html_br, "w", encoding="utf-8") as while_asins:
                    while_asins.write('<p style=" font-size:12pt; font-weight:600;">404 сторінка не знайдена ¯\\_(ツ)_/¯')

                try:
                    inf_text_ = self.mainwindows.lineEdit_2.text()

                    soup = BeautifulSoup(contents.text, "lxml")
                    num_t = soup.find("div", class_="block-head").text

                    test_search_1 = soup.find("div", class_="col-md-9 col-sm-8")
                    test_search_2 = test_search_1.find_all("div", class_="content-block entry-item question-view-item")

                    test_search_num = []
                    test_search_text = ""
                    for test_search_3 in test_search_2:
                        if test_search_3.find("div", class_="option-marker quiz"):
                            text_option_text_quiz = str(test_search_3)
                            #replase space
                            text_option_quiz = text_option_text_quiz.replace('<div class="option-text">\n<p> ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f'<div class="option-text">\n<p>  ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f'<div class="option-text">\n<p>   ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f'<div class="option-text">\n<p>    ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f' ', '')
                            text_option_quiz = text_option_quiz.replace(f'<p><br/></p>', '')


                            text_option_quiz = text_option_quiz.replace('<div class="option-text">\n<p>\n', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace('<div class="option-text">\n<p>', '<div class="option-text">\n<p><img src="res/quiz_.png"/> ')
                            test_search_text += text_option_quiz

                        elif test_search_3.find("div", class_="option-marker multiquiz"):
                            text_option_text_quiz = str(test_search_3)
                            #replase space
                            text_option_quiz = text_option_text_quiz.replace(f'<div class="option-text">\n<p> ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f'<div class="option-text">\n<p>  ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f'<div class="option-text">\n<p>   ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f'<div class="option-text">\n<p>    ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f' ', '')
                            text_option_quiz = text_option_quiz.replace(f'<p><br/></p>', '')

                            text_option_quiz = text_option_quiz.replace('<div class="option-text">\n<p><br>', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace('<div class="option-text">\n<p>', '<div class="option-text">\n<p><img src="res/multiquiz_.png"/> ')
                            test_search_text += text_option_quiz
                        else:
                            test_search_text += str(test_search_3)

                        test_search_4 = test_search_3.find("div", class_="question-view-item-content")
                        test_search_4 = test_search_4.text.replace("\n", "")
                        test_search_num.append(fuzz.WRatio(inf_text_, test_search_4))

                    test_search_text = test_search_text.replace(' width="100%"/>', '/>')
                    with open(self.mainwindows.file_read_html_br, "w", encoding="utf-8") as while_asins:
                        while_asins.write('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
                                                <html><head><meta name="qrichtext" content="1" /><style type="text/css">
                                                .question-view-item-content{ font-family:'MS Shell Dlg 2'; font-size:10pt; background-color:#454545; font-weight:600;}
                                                .col-md-9{ font-family:'MS Shell Dlg 2'; font-size:10pt; background-color:#454545; font-weight:600;}
                                                .question-label{font-size:8pt; margin-top:48px; margin-left:10px;}
                                                .question-label-options{font-size:7pt;}
                                                .option-text{font-size:9pt; font-weight:600; margin-left:20px;}
                                                .image-only-option{margin-top:15px; margin-left:20px;}
                                                </style>
                                                </head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;"><p style="font-size:12pt; font-weight:800;">''' + f'| {num_t}<br/>| Збіг [{max(test_search_num)}%]</p><br/>\n' + test_search_text + '</body></html>')

                    self.log_signal.emit(f'[INFO] [Reload] [url][<span style="color:#1AA8DD;">{self.mainwindows.url_test_reload}</span>] [file][{self.mainwindows.file_read_html_br}]', "INFO_1")
                except Exception as e:
                    self.log_signal.emit(f"[ERROR] [Reload] [url][{self.mainwindows.url_test_reload}] [{e}]", "ERROR")
            except:
                self.log_signal.emit(f"[ERROR] [Reload] [url][{self.mainwindows.url_test_reload}]", "ERROR")
            self.reload_browser_signal.emit()

#check reg
class Check_reg(QThread):
    log_signal = QtCore.pyqtSignal(str, str)
    info_user_ = QtCore.pyqtSignal(str, str)

    def __init__(self, mainwindows):
        QThread.__init__(self)
        self.mainwindows = mainwindows

    def run(self):
        try:
            with open("data/cookies", "r") as read_file:
                data_r = json.load(read_file)

            session = requests.Session()
            for cookie in data_r:
                session.cookies.set(cookie['name'], cookie['value'])
            contents = session.get("https://naurok.com.ua/")
            soup = BeautifulSoup(contents.text, "lxml")
            n1 = soup.find("div", class_="container-fluid")
            n2 = n1.find_all(class_="dropdown-menu")
            id_user = ""
            for i in n2:
                if n2.index(i) == 2:
                    id_user = i.find(id).find("a").get("href")

            respon = session.get(f"https://naurok.com.ua{id_user}")
            soup = BeautifulSoup(respon.text, "lxml")
            n1 = soup.find("div", class_="personal-sidebar profile-sidebar")
            avatar = n1.find("img", class_="profile-avatar").get("src")
            name = n1.find_all("div")
            for user_n in name:
                if name.index(user_n) == 3:
                    reg_ok = user_n.find("div").text
                if name.index(user_n) == 1: 
                    name_user = user_n.text

            img_icon = session.get(avatar)
            with open("res/user_icon.png", "wb") as wr_img:
                wr_img.write(img_icon.content)

            self.info_user_.emit(name_user, reg_ok)
            self.log_signal.emit(f"[INFO] [Login naurok] [Login successful]", "INFO_1")
            self.mainwindows.login_ok = True
        except:
            self.log_signal.emit(f"[ERROR] [Login naurok] [Login failed]", "ERROR")

#reg naurok
class Reg_naurok(QThread):
    log_signal = QtCore.pyqtSignal(str, str)
    check_reg_user_ = QtCore.pyqtSignal()
    def __init__(self, mainwindows):
        QThread.__init__(self)
        self.mainwindows = mainwindows

    def run(self):
        list_browser = ['firefox', 'chrome', 'opera', 'edge']

        br_start = False
        for browser_ in list_browser:
            if br_start == False:
                for app in winapps.search_installed(browser_):
                    if app.name:
                        if list_browser.index(browser_) == 0:
                            driver = webdriver.Firefox()
                            br_start = True
                        if list_browser.index(browser_) == 1:
                            driver = webdriver.Chrome()
                            br_start = True
                        if list_browser.index(browser_) == 2:
                            driver = webdriver.Opera()
                            br_start = True
                        if list_browser.index(browser_) == 3:
                            driver = webdriver.Edge()
                            br_start = True

        driver.get('https://naurok.com.ua/registration')
        while True:
            time.sleep(1)
            if driver.current_url != "https://naurok.com.ua/registration":
                if driver.current_url != "https://naurok.com.ua/login":
                    if driver.current_url == "https://naurok.com.ua/":
                        try:
                            driver.find_element(by=By.XPATH, value="/html/body/nav/div/div[2]/ul[2]/li[2]/a/img").get_attribute('src')
                            cookies = driver.get_cookies()
                            with open("data/cookies", "w") as write_file:
                                json.dump(cookies, write_file, indent=4)
                            time.sleep(1)
                            driver.quit()
                            break
                        except:
                            pass
        self.check_reg_user_.emit()

#Load_img
class Load_img(QThread):
    log_signal = QtCore.pyqtSignal(str, str)
    progress_signal = QtCore.pyqtSignal(int)
    update_html_br = QtCore.pyqtSignal()

    def __init__(self, mainwindows):
        QThread.__init__(self)
        self.mainwindows = mainwindows

    def run(self):
        self.start_time = perf_counter()
        for item_num in self.mainwindows.listWidget.selectedIndexes():
            self.clicked_item_num_ = self.mainwindows.list_tests[item_num.row()]
        self.log_signal.emit(f'[start][load_img]: [Test][url][<span style="color:#1AA8DD;">{self.clicked_item_num_["url"]}</span>]', "INFO_1")
        self.progress_signal.emit(5)

        with open("data/settings.json", "r", encoding="utf-8") as settings_r:
            settings_loads = json.load(settings_r)

        self.x_img_size = settings_loads["img_x"]
        self.y_img_size = settings_loads["img_y"]

        try:
            multiprocessing.Process(target=self.download_image(), name="download_image").start()
        except:
            pass

        self.progress_signal.emit(0)
        load_time = f"{(perf_counter() - self.start_time):.02f}"
        self.log_signal.emit(f"[end]: [{load_time}]\n<br>", "INFO_1")
        self.update_html_br.emit()


    def download_image(self):
        async def download_img_async(url, header, session, val_progress_, path_img):
            try:
                link_img_name = url.split('/')[-1]
                async with session.get(url, headers=header, proxy=None, allow_redirects=True) as response:
                    contents_1 = response

                    async with aiofiles.open(f"temp_data/images/{link_img_name}", "wb") as while_img:
                        async for chunk in response.content.iter_chunked(64 * 1024):
                            await while_img.write(chunk)

                    img_obj = Image.open(f"temp_data/images/{link_img_name}")
                    img_obj = img_obj.resize((self.x_img_size, self.y_img_size), Image.LANCZOS)
                    img_obj.save(f"temp_data/images/{link_img_name}")

                self.val_progress_img += val_progress_

                self.log_signal.emit(f'[INFO] [Image]: [url][<span style="color:#1AA8DD;">{url}</span>]', "INFO_0")
                self.progress_signal.emit(self.val_progress_img)
            except:
                self.log_signal.emit(f"[ERROR] [Image]: [url][{url}]", "ERROR")
                self.progress_signal.emit(self.val_progress_img)
                async with aiofiles.open(f"temp_data/read_html/index{self.clicked_item_num_['num_file']}.html", "r", encoding="utf-8") as read_asins:
                    read_html = await read_asins.read()

                wr_html_ = read_html.replace(path_img, "res/error_img.png")
                async with aiofiles.open(f"temp_data/read_html/index{self.clicked_item_num_['num_file']}.html", "w", encoding="utf-8") as while_asins:
                    await while_asins.write(wr_html_)
                

        async def main():
            usr_ = UserAgent()
            header = {'user-agent': f'{usr_.random}'}

            links_imgs = []

            async with aiofiles.open(f"temp_data/read_html/index{self.clicked_item_num_['num_file']}.html", "r", encoding="utf-8") as read_asins:
                read_html = await read_asins.read()

            soup = BeautifulSoup(read_html, "lxml")
            image_url = soup.find_all(class_="question-view-item-image")
            image_url_question = soup.find_all(class_="option-image")
            links_img = []
            for img in image_url:
                try:
                    image_link = img.get("src")
                    if re.search(r'\bhttps\b', image_link):
                        image_link_1 = image_link.split('/')[-1]
                        image_link_repl = image_link.replace(image_link_1, '')
                        links_img.append(image_link)
                        async with aiofiles.open(f"temp_data/read_html/index{self.clicked_item_num_['num_file']}.html", "r", encoding="utf-8") as read_asins:
                            read_html = await read_asins.read()
                        wr_html = read_html.replace(image_link_repl, "temp_data/images/")
                        async with aiofiles.open(f"temp_data/read_html/index{self.clicked_item_num_['num_file']}.html", "w", encoding="utf-8") as while_asins:
                            await while_asins.write(wr_html)
                except:
                    pass

            try:
                async with aiofiles.open(f"temp_data/read_html/index{self.clicked_item_num_['num_file']}.html", "r", encoding="utf-8") as read_asins:
                    read_html_question = await read_asins.read()
            except:
                pass

            for img_question in image_url_question:
                try:
                    image_link = img_question.get("src")
                    if re.search(r'\bhttps\b', image_link):
                        image_link_1 = image_link.split('/')[-1]
                        image_link_repl = image_link.replace(image_link_1, '')
                        links_img.append(image_link)
                        async with aiofiles.open(f"temp_data/read_html/index{self.clicked_item_num_['num_file']}.html", "r", encoding="utf-8") as read_asins:
                            read_html = await read_asins.read()
                        wr_html_2 = read_html.replace(image_link_repl, "temp_data/images/")
                        async with aiofiles.open(f"temp_data/read_html/index{self.clicked_item_num_['num_file']}.html", "w", encoding="utf-8") as while_asins:
                            await while_asins.write(wr_html_2)
                except:
                    pass

            links_imgs = list(dict.fromkeys(links_img))

            if len(links_imgs) != 0:
                update_num = 95 // len(links_imgs)
                self.log_signal.emit(f"[INFO] [Image]: [{len(links_imgs)}]", "INFO_0")
            else:
                update_num = 95
                self.log_signal.emit(f"[INFO] [Image]: [None]", "INFO_0")
                self.progress_signal.emit(100)

            async with aiohttp.ClientSession() as session:
                #Download imgs
                tasks = []
                self.val_progress_img = 5
                for link in links_imgs:
                    path_img = f"temp_data/images/{link.split('/')[-1]}"
                    tasks.append(asyncio.create_task(download_img_async(link, header, session, update_num, path_img)))

                await asyncio.gather(*tasks)


        if __name__ == '__main__':
            with open("data/settings.json", "r", encoding="utf-8") as settings_r:
                settings_loads = json.load(settings_r)

            multiprocessing.freeze_support()
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            asyncio.run(main())

#Parser - search
class Search_test(QThread):
    log_signal = QtCore.pyqtSignal(str, str)
    progress_signal = QtCore.pyqtSignal(int)
    update_list_ = QtCore.pyqtSignal()
    info_search_t = QtCore.pyqtSignal(str)

    def __init__(self, mainwindows):
        QThread.__init__(self)
        self.mainwindows = mainwindows

    def run(self):
        #data request
        self.inputs_text = self.mainwindows.lineEdit_2.text()
        self.inputs_subject = self.mainwindows.comboBox_2.currentText()
        self.inputs_class = self.mainwindows.comboBox.currentText()
        self.data_url_naurok = ""
        self.num_subject = self.mainwindows.comboBox_2.currentIndex()
        if self.num_subject != 0:
            if self.num_subject == 1:
                self.data_url_naurok += "/algebra"
            if self.num_subject == 2:
                self.data_url_naurok += "/angliyska-mova"
            if self.num_subject == 3:
                self.data_url_naurok += "/astronomiya"
            if self.num_subject == 4:
                self.data_url_naurok += "/biologiya"
            if self.num_subject == 5:
                self.data_url_naurok += "/vsesvitnya-istoriya"
            if self.num_subject == 6:
                self.data_url_naurok += "/geografiya"
            if self.num_subject == 7:
                self.data_url_naurok += "/geometriya"
            if self.num_subject == 8:
                self.data_url_naurok += "/gromadyanska-osvita"
            if self.num_subject == 9:
                self.data_url_naurok += "/ekologiya"
            if self.num_subject == 10:
                self.data_url_naurok += "/ekonomika"
            if self.num_subject == 11:
                self.data_url_naurok += "/etika"
            if self.num_subject == 12:
                self.data_url_naurok += "/zarubizhna-literatura"
            if self.num_subject == 13:
                self.data_url_naurok += "/zahist-vitchizni"
            if self.num_subject == 14:
                self.data_url_naurok += "/informatika"
            if self.num_subject == 15:
                self.data_url_naurok += "/inshi-inozemni-movi"
            if self.num_subject == 16:
                self.data_url_naurok += "/ispanska-mova"
            if self.num_subject == 17:
                self.data_url_naurok += "/istoriya-ukra-ni"
            if self.num_subject == 18:
                self.data_url_naurok += "/kreslennya"
            if self.num_subject == 19:
                self.data_url_naurok += "/literaturne-chitannya"
            if self.num_subject == 20:
                self.data_url_naurok += "/lyudina-i-svit"
            if self.num_subject == 21:
                self.data_url_naurok += "/matematika"
            if self.num_subject == 22:
                self.data_url_naurok += "/mistectvo"
            if self.num_subject == 23:
                self.data_url_naurok += "/movi-nacionalnih-menshin"
            if self.num_subject == 24:
                self.data_url_naurok += "/muzichne-mistectvo"
            if self.num_subject == 25:
                self.data_url_naurok += "/navchannya-gramoti"
            if self.num_subject == 26:
                self.data_url_naurok += "/nimecka-mova"
            if self.num_subject == 27:
                self.data_url_naurok += "/obrazotvorche-mistectvo"
            if self.num_subject == 28:
                self.data_url_naurok += "/osnovi-zdorov-ya"
            if self.num_subject == 29:
                self.data_url_naurok += "/polska-mova"
            if self.num_subject == 30:
                self.data_url_naurok += "/pravoznavstvo"
            if self.num_subject == 31:
                self.data_url_naurok += "/prirodnichi-nauki"
            if self.num_subject == 32:
                self.data_url_naurok += "/prirodoznavstvo"
            if self.num_subject == 33:
                self.data_url_naurok += "/tehnologi"
            if self.num_subject == 34:
                self.data_url_naurok += "/trudove-navchannya"
            if self.num_subject == 35:
                self.data_url_naurok += "/ukrainska-literatura"
            if self.num_subject == 36:
                self.data_url_naurok += "/ukrainska-mova"
            if self.num_subject == 37:
                self.data_url_naurok += "/fizika"
            if self.num_subject == 38:
                self.data_url_naurok += "/fizichna-kultura"
            if self.num_subject == 39:
                self.data_url_naurok += "/francuzka-mova"
            if self.num_subject == 40:
                self.data_url_naurok += "/himiya"
            if self.num_subject == 41:
                self.data_url_naurok += "/hudozhnya-kultura"
            if self.num_subject == 42:
                self.data_url_naurok += "/ya-doslidzhuyu-svit"

        if self.mainwindows.comboBox.currentIndex() != 0:
            self.data_url_naurok += f"/klas-{self.mainwindows.comboBox.currentIndex()}"

        #start
        self.start_time = perf_counter()
        self.log_signal.emit(f"[start]: [{self.inputs_text}]", "INFO_1")
        self.progress_signal.emit(5)

        clear_image = os.listdir("temp_data/images")
        for clear_image_d in clear_image:
            os.remove(f"temp_data/images/{clear_image_d}")

        multiprocessing.Process(target=self.test_search_()).start()

        self.progress_signal.emit(0)
        search_time = f"{(perf_counter() - self.start_time):.02f}"
        self.log_signal.emit(f"[end]: [{search_time}]\n<br>", "INFO_1")
        self.mainwindows.progressBar.setMaximum(100)

    def test_search_(self):
        async def naurok_(num_url, header, session):
            try:
                async with session.get(f"https://naurok.com.ua/test{self.data_url_naurok}?q={self.inputs_txt}&storinka={num_url}", headers=header, proxy=None) as response:
                    contents = await response.text()

                soup = BeautifulSoup(contents, "lxml")
                user_n = soup.find("div", class_="items")
                user_n_2 = user_n.find_all("div", class_="file-item test-item")
                for links in user_n_2:
                    link_n = f'https://naurok.com.ua{links.find("div", class_="row").find("div", class_="headline").find("a").get("href")}'
                    if re.search(r'\bhttps://naurok.com.ua/test/\b', link_n):
                        if re.search(r'\b.html\b', link_n):
                            self.links_naurok.append(link_n)

                self.log_signal.emit(f"[INFO] [Naurok]: [page][{num_url}]", "INFO_0")
            except:
                self.log_signal.emit(f"[ERROR] [Naurok]: [page][{num_url}]", "ERROR")

        async def google_(num_url, header, session):
            try:
                async with session.get(f"https://www.google.com/search?q=на+урок+{self.inputs_txt}&start={num_url}0&sa=N", headers=header, proxy=None) as response:
                    contents = await response.text()

                soup = BeautifulSoup(contents, "lxml")
                user_n = soup.find(class_="dURPMd").find_all("a")
                for links in user_n:
                    block = links.get("href")
                    if re.search(r'\bhttps://naurok.com.ua/test/\b', block):
                        if re.search(r'\b.html\b', block):
                            self.links_google.append(block)

                self.log_signal.emit(f"[INFO] [Google]: [page][{num_url}]", "INFO_0")
            except:
                self.log_signal.emit(f"[ERROR] [Google]: [page][{num_url}]", "ERROR")

        async def bing_(num_url, header, session):
            try:
                async with session.get(f"https://www.bing.com/search?q=на+урок+{self.inputs_txt}+&first={num_url}0&FORM=PERE", headers=header, proxy=None) as response:
                    contents = await response.text()

                soup = BeautifulSoup(contents, "lxml")
                user_n = soup.find_all(class_="tilk")
                for links in user_n:
                    block = links.get("href")
                    if re.search(r'\bhttps://naurok.com.ua/test/\b', block):
                        if re.search(r'\b.html\b', block):
                            self.links_bing.append(block)

                self.log_signal.emit(f"[INFO] [Bing]: [page][{num_url}]", "INFO_0")
            except:
                self.log_signal.emit(f"[ERROR] [Bing]: [page][{num_url}]", "ERROR")

        async def load_links_(num_url, header, url, session):
            try:
                async with session.get(url, headers=header, proxy=None) as response:
                    contents = await response.text()

                async with aiofiles.open(f"temp_data/read_html/index{num_url}.html", "w", encoding="utf-8") as while_asins:
                    await while_asins.write('<p style=" font-size:12pt; font-weight:600;">404 сторінка не знайдена ¯\\_(ツ)_/¯')

                try:
                    soup = BeautifulSoup(contents, "lxml")
                    num_t = soup.find("div", class_="block-head").text
                    num_t3 = num_t.replace(" запитань", "")
                    num_t4 = num_t3.replace(" запитання", "")

                    test_search_1 = soup.find("div", class_="col-md-9 col-sm-8")
                    test_search_2 = test_search_1.find_all("div", class_="content-block entry-item question-view-item")

                    test_search_num = []
                    test_search_text = ""
                    for test_search_3 in test_search_2:
                        if test_search_3.find("div", class_="option-marker quiz"):
                            text_option_text_quiz = str(test_search_3)
                            #replase space
                            text_option_quiz = text_option_text_quiz.replace('<div class="option-text">\n<p> ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f'<div class="option-text">\n<p>  ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f'<div class="option-text">\n<p>   ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f'<div class="option-text">\n<p>    ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f' ', '')
                            text_option_quiz = text_option_quiz.replace(f'<p><br/></p>', '')

                            text_option_quiz = text_option_quiz.replace('<div class="option-text">\n<p>', '<div class="option-text">\n<p><img src="res/quiz_.png"/> ')
                            test_search_text += text_option_quiz

                        elif test_search_3.find("div", class_="option-marker multiquiz"):
                            text_option_text_quiz = str(test_search_3)
                            #replase space
                            text_option_quiz = text_option_text_quiz.replace('<div class="option-text">\n<p> ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f'<div class="option-text">\n<p>  ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f'<div class="option-text">\n<p>   ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f'<div class="option-text">\n<p>    ', '<div class="option-text">\n<p>')
                            text_option_quiz = text_option_quiz.replace(f' ', '')
                            text_option_quiz = text_option_quiz.replace(f'<p><br/></p>', '')

                            text_option_quiz = text_option_quiz.replace('<div class="option-text">\n<p>', '<div class="option-text">\n<p><img src="res/multiquiz_.png"/> ')
                            test_search_text += text_option_quiz

                        else:
                            test_search_text += str(test_search_3)

                        test_search_4 = test_search_3.find("div", class_="question-view-item-content")
                        test_search_4 = test_search_4.text.replace("\n", "")
                        test_search_num.append(fuzz.WRatio(self.inf_text_, test_search_4))

                    test_search_text = test_search_text.replace(' width="100%"/>', '/>')
                    async with aiofiles.open(f"temp_data/read_html/index{num_url}.html", "w", encoding="utf-8") as while_asins:
                        await while_asins.write('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
                                                <html><head><meta name="qrichtext" content="1" /><style type="text/css">
                                                .question-view-item-content{ font-family:'MS Shell Dlg 2'; font-size:10pt; background-color:#454545; font-weight:600;}
                                                .col-md-9{ font-family:'MS Shell Dlg 2'; font-size:10pt; background-color:#454545; font-weight:600;}
                                                .question-label{font-size:8pt; margin-top:48px; margin-left:10px;}
                                                .question-label-options{font-size:7pt;}
                                                .option-text{font-size:9pt; font-weight:600; margin-left:20px;}
                                                .image-only-option{margin-top:15px; margin-left:20px;}
                                                </style>
                                                </head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;"><p style="font-size:12pt; font-weight:800;">''' + f'| {num_t}<br/>| Збіг [{max(test_search_num)}%]</p><br/>\n' + test_search_text + '</body></html>')

                    try:
                        lesson = soup.find("div", class_="breadcrumb breadcrumb-single").find_all("span")
                        lesson_name = "None"
                        class_num = "None"
                        for ls in lesson:
                            if ls.find("meta") != None:
                                meta_ = ls.find("meta").get("content")
                            if ls.get("itemprop") == "name":
                                if meta_ == "2":
                                    lesson_name = f"{ls.text}"
                                if meta_ == "3":
                                    class_num = f"{ls.text}"
                    except:
                        pass

                    self.mainwindows.list_tests_null.append({
                        "num_file": num_url,
                        "num_q": int(num_t4),
                        "url": url,
                        "max_": max(test_search_num),
                        "lesson_name": lesson_name,
                        "class_num": class_num,
                        "ERROR": False
                        })

                    self.log_signal.emit(f'[INFO] [Test]: [num][{num_url}] | [url][<span style="color:#1AA8DD;">{url}</span>]', "INFO_0")
                    self.update_list_.emit()
                    self.progress_load_naurok += self.progress_pr
                    self.progress_signal.emit(self.progress_load_naurok)
                except:
                    self.log_signal.emit(f"[ERROR] [Test]: [num][{num_url}] | [url][{url}]", "ERROR")
                    self.update_list_.emit()
                    self.mainwindows.list_tests_null.append({
                        "num_file": None,
                        "num_q": None,
                        "url": None,
                        "max_": None,
                        "lesson_name": None,
                        "class_num": None,
                        "ERROR": True
                        })
            except:
                self.update_list_.emit()
                self.log_signal.emit(f"[ERROR] [Test]: [num][{num_url}] | [url][{url}]", "ERROR")
                self.mainwindows.list_tests_null.append({
                    "num_file": None,
                    "num_q": None,
                    "url": None,
                    "max_": None,
                    "lesson_name": None,
                    "class_num": None,
                    "ERROR": True
                    })

        async def search_async(inf_text_, inf_subject_, inf_class_, settings_loads):
            self.inf_text_ = inf_text_
            self.inputs_txt = inf_text_.replace(" ", "+")
            self.links_naurok = []
            self.links_google = []
            self.links_bing = []

            usr_ = UserAgent()
            header = {'user-agent': f'{usr_.random}'}

            async with aiohttp.ClientSession() as session:
                #Naurok
                tasks = []
                for num_link in range(settings_loads['naurok_page']):
                    tasks.append(asyncio.create_task(naurok_(num_link, header, session)))

                await asyncio.gather(*tasks)
                self.log_signal.emit(f"[INFO] [Naurok]: [pages][{settings_loads['naurok_page']}] | [links][{len(self.links_naurok)}]", "INFO_1")
                self.progress_signal.emit(10)


                #Google
                tasks = []
                for num_link in range(settings_loads['google_page']):
                    tasks.append(asyncio.create_task(google_(num_link, header, session)))

                await asyncio.gather(*tasks)
                self.log_signal.emit(f"[INFO] [Google]: [pages][{settings_loads['google_page']}] | [links][{len(self.links_google)}]", "INFO_1")
                self.progress_signal.emit(15)


                #Bing
                tasks = []
                for num_link in range(settings_loads['bing_page']):
                    tasks.append(asyncio.create_task(bing_(num_link, header, session)))

                await asyncio.gather(*tasks)
                self.log_signal.emit(f"[INFO] [Bing]: [pages][{settings_loads['bing_page']}] | [links][{len(self.links_bing)}]", "INFO_1")
                self.progress_signal.emit(20)


                all_link_ = list(dict.fromkeys(self.links_naurok + self.links_google + self.links_bing))

                self.log_signal.emit(f"[INFO] [All_no_sort]: [links][{len(self.links_google) + len(self.links_bing) + len(self.links_naurok)}]", "INFO_1")
                self.log_signal.emit(f"[INFO] [All]: [links][{len(all_link_)}]", "INFO_1")


                self.info_search_t.emit(f"About {len(all_link_)} results ({(perf_counter() - self.start_time):.02f} seconds)")

                #Load link
                tasks = []
                num_link = 0

                self.progress_load_naurok = 20
                if len(all_link_) > 80:
                    self.progress_pr = 1
                    max_progress_bar = len(all_link_) + 20
                    self.mainwindows.progressBar.setMaximum(max_progress_bar)
                else:
                    self.progress_pr = 80 // len(all_link_)
                for url_link in all_link_:
                    tasks.append(asyncio.create_task(load_links_(num_link, header, url_link, session)))
                    num_link += 1

                await asyncio.gather(*tasks)

        if __name__ == '__main__':
            with open("data/settings.json", "r", encoding="utf-8") as settings_r:
                settings_loads = json.load(settings_r)

            multiprocessing.freeze_support()
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            asyncio.run(search_async(self.inputs_text, self.inputs_subject, self.inputs_class, settings_loads))

#Main
class ExampleApp(QtWidgets.QMainWindow, GUI_.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    #Button
        self.pushButton.clicked.connect(self.search_question_0)
        self.pushButton_8.clicked.connect(self.sort_button)
        self.pushButton_15.clicked.connect(self.settings_save)
        self.pushButton_2.clicked.connect(self.search_question)
        self.pushButton_10.clicked.connect(self.reg_start)
        self.pushButton_23.clicked.connect(self.reload_page)
        self.pushButton_6.clicked.connect(self.open_url_browser)
        self.pushButton_14.clicked.connect(self.open_git_)
        self.pushButton_5.clicked.connect(self.search_question_1)
        self.pushButton_4.clicked.connect(self.search_question_2)
        self.pushButton_9.clicked.connect(self.getting_answers)
        self.pushButton_17.clicked.connect(self.return_search)
        self.pushButton_24.clicked.connect(self.copy_url_test_clicked)
        self.pushButton_24.pressed.connect(self.copy_url_test_pressed)
        self.pushButton_21.clicked.connect(self.open_history)
        self.pushButton_32.clicked.connect(self.search_question_2)
        self.pushButton_33.clicked.connect(self.search_question_2)
        self.pushButton_34.clicked.connect(self.search_question_2)
        self.pushButton_35.clicked.connect(self.search_question_2)
        self.pushButton_13.clicked.connect(self.open_web_answer_url)
        self.pushButton_16.clicked.connect(self.copy_web_answer_url)
        self.pushButton_12.clicked.connect(self.url_join_test_)
        self.pushButton_30.clicked.connect(self.del_history_logs)
        self.pushButton_28.clicked.connect(self.del_history_answer)
        self.pushButton_22.clicked.connect(self.getting_answers_auto)
        self.pushButton_36.clicked.connect(self.search_question_2)

    #radio button
        self.radioButton_14.clicked.connect(self.update_list_widget)
        self.radioButton_13.clicked.connect(self.update_list_widget)
        self.radioButton_12.clicked.connect(self.update_list_widget)
        self.radioButton_15.clicked.connect(self.update_list_widget)
        self.radioButton_16.clicked.connect(self.update_list_widget)

    #checkBox
        self.checkBox.clicked.connect(self.update_list_widget)

    #List
        self.listWidget.clicked.connect(self.clicked_list_test_)
        self.listWidget.doubleClicked.connect(self.open_url_browser)
        self.listWidget_4.clicked.connect(self.open_history_logs)
        self.listWidget_3.clicked.connect(self.open_history_answer)

    #Line
        self.lineEdit.returnPressed.connect(self.search_question_0)
        self.lineEdit_2.returnPressed.connect(self.search_question)

    #spinbox
        self.spinBox_10.valueChanged.connect(self.update_list_widget)
        self.spinBox_11.valueChanged.connect(self.update_list_widget)
        self.spinBox_12.valueChanged.connect(self.update_list_widget)
        self.spinBox_13.valueChanged.connect(self.update_list_widget)


    #Class
    #Search
        self.search_parser = Search_test(mainwindows=self)
        self.search_parser.log_signal.connect(self.logs_)
        self.search_parser.progress_signal.connect(self.progress_search)
        self.search_parser.update_list_.connect(self.update_list_widget)
        self.search_parser.info_search_t.connect(self.info_search_label)

    #Search html text

    #Download img
        self.download_img = Load_img(mainwindows=self)
        self.download_img.log_signal.connect(self.logs_)
        self.download_img.progress_signal.connect(self.progress_load_img)
        self.download_img.update_html_br.connect(self.set_html_browser)

    #REG naurok
        self.reg_n = Reg_naurok(mainwindows=self)
        self.reg_n.check_reg_user_.connect(self.check_user_reg_)
        self.reg_n.log_signal.connect(self.logs_)

    #Check reg
        self.check_regist = Check_reg(mainwindows=self)
        self.check_regist.info_user_.connect(self.set_info_user)
        self.check_regist.log_signal.connect(self.logs_)
        self.check_regist.start()

    #Reload test
        self.rl_test = Reload_page_naurok(mainwindows=self)
        self.rl_test.log_signal.connect(self.logs_)
        self.rl_test.reload_browser_signal.connect(self.clicked_list_test_)

    #Getting answers
        self.get_answer = Get_answers_test(mainwindows=self)
        self.get_answer.log_signal.connect(self.logs_)
        self.get_answer.reload_browser_signal.connect(self.reload_answer)
        self.get_answer.progress_bar_signal.connect(self.set_value_answer_web)

    #Search test auto
        self.search_parser_auto = Search_test_auto(mainwindows=self)
        self.search_parser_auto.log_signal.connect(self.logs_)
        self.search_parser_auto.progress_signal.connect(self.progress_search_auto)

    #Get answers test auto
        self.get_answer_auto = Get_answers_test_auto(mainwindows=self)
        self.get_answer_auto.log_signal.connect(self.logs_)
        self.get_answer_auto.index_signal.connect(self.signal_answers_auto)

    #======================
        #def start
        self.check_log_file()
        self.settings_load()
        self.logs_("[INFO] [START | Test_Finder]", "INFO_1")
        self.load_history_logs()
        self.load_history_answer()

        #info-data
        self.url_answer_open = None
        self.login_ok = False
        self.read_html = ""
        self.url_test_reload = None
        self.file_read_html_br = None
        self.continue_answers_auto = False
        self.url_auto_test = []

    def signal_answers_auto(self, index_s):
        if index_s == "set_":
            self.stackedWidget.setCurrentIndex(5)
            self.label_22.setText(f"{self.user_name_test} | [{self.gamecode_test}]")
            self.label_30.setText(f"{self.user_name_test} | [{self.gamecode_test}]")
            for item_list_question in self.list_question['questions']:
                soup = BeautifulSoup(item_list_question['content'], "lxml")
                text_question = soup.find("p")
                self.listWidget_6.addItem(text_question.text)
                self.list_question_content.append(text_question.text)
            self.search_parser_auto.start()

        elif index_s == "ERROR":
            self.label_29.setText("Such code does not exist or \nthere is no Internet")

    def getting_answers_auto(self):
        if self.login_ok != True:
            self.msg = QMessageBox()
            self.msg.setWindowTitle("Login ERROR")
            self.msg.setText("Будь ласка, увійдіть до облікового запису на урок,\nщоб отримати відповіді!")
            self.msg.setIcon(QMessageBox.Warning)
            self.msg.exec_()
        else:
            if self.lineEdit_6.text() != "":
                if self.lineEdit_7.text() != "":
                    self.list_question = []
                    self.list_question_content = []
                    self.label_29.setText("")
                    self.gamecode_test = self.lineEdit_6.text()
                    self.user_name_test = self.lineEdit_7.text()
                    self.get_answer_auto.start()
                else:
                    self.label_29.setText("Enter your name")
            else:
                self.label_29.setText("Enter a code")

    def progress_search_auto(self, value_):
        self.progressBar_5.setValue(value_)

    def del_history_logs(self):
        try:
            os.remove(f"logs/html/{self.list_logs_[self.index_history_logs]}")
            os.remove(f"logs/txt/{self.list_logs_[self.index_history_logs]}")
        except:
            pass

        self.load_history_logs()

    def del_history_answer(self):
        try:
            os.remove(f"temp_data/answers_html/{self.list_answer_[self.index_history_answer]}")
        except:
            pass

        self.load_history_answer()

    def open_history_logs(self):
        for item_num in self.listWidget_4.selectedIndexes():
            self.index_history_logs = item_num.row()
            with open(f"logs/html/{self.list_logs_[self.index_history_logs]}", "r", encoding="utf-8") as read_logs_f:
                self.textBrowser_6.setHtml(read_logs_f.read())

    def open_history_answer(self):
        for item_num in self.listWidget_3.selectedIndexes():
            self.index_history_answer = item_num.row()
            with open(f"temp_data/answers_html/{self.list_answer_[self.index_history_answer]}", "r", encoding="utf-8") as read_answer_f:
                self.textBrowser_5.setHtml(read_answer_f.read())

    def load_history_logs(self):
        self.listWidget_4.clear()
        self.list_logs_ = os.listdir("logs/html")
        for logs_file in self.list_logs_:
            self.listWidget_4.addItem(logs_file.split('.html')[0])

    def load_history_answer(self):
        self.listWidget_3.clear()
        self.list_answer_ = os.listdir("temp_data/answers_html")
        for answer_file in self.list_answer_:
            self.listWidget_3.addItem(answer_file.split('.html')[0])

    def url_join_test_(self):
        self.stackedWidget.setCurrentIndex(3)

    def set_value_answer_web(self, value_):
        self.progressBar_3.setValue(value_)

    def copy_web_answer_url(self):
        if self.url_answer_open != None:
            pyperclip.copy(self.url_answer_open)

    def open_web_answer_url(self):
        if self.url_answer_open != None:
            webbrowser.open_new_tab(self.url_answer_open)

    def open_history(self):
        self.stackedWidget.setCurrentIndex(4)

    def copy_url_test_pressed(self):
        if self.url_test_reload != None:
            pyperclip.copy(self.url_test_reload)
            self.lineEdit_8.setText("Copied")

    def copy_url_test_clicked(self):
        if self.url_test_reload != None:
            self.lineEdit_8.setText(self.url_test_reload)

    def reload_answer(self, url_html):
        with open(url_html, "r", encoding="utf-8") as read_answer:
            html_read_answer = read_answer.read()
        self.textBrowser_3.setHtml(html_read_answer)

    def return_search(self):
        self.stackedWidget.setCurrentIndex(1)

    def getting_answers(self):
        if self.url_test_reload != None:
            if self.login_ok != True:
                self.msg = QMessageBox()
                self.msg.setWindowTitle("Login ERROR")
                self.msg.setText("Будь ласка, увійдіть до облікового запису на урок,\nщоб отримати відповіді!")
                self.msg.setIcon(QMessageBox.Warning)
                self.msg.exec_()
            else:
                self.stackedWidget.setCurrentIndex(2)
                self.get_answer.start()

    def open_git_(self):
        webbrowser.open_new_tab("https://github.com/69BooM96/Test-Finder")

    def check_log_file(self):
        try:
            with open(f"logs/html/{time.strftime('%Y-%m-%d')}.html", "r", encoding="utf-8") as log_wr:
                log_wr.read()
        except:
            with open(f"logs/html/{time.strftime('%Y-%m-%d')}.html", "a", encoding="utf-8") as log_wr:
                log_wr.write('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
                                <html><head><meta name="qrichtext" content="1" />
                                </head><body style=" background-color:#141518; color: #A7A8A9; font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">''')

    def open_url_browser(self):
        if self.url_test_reload != None:
            try:
                webbrowser.open_new_tab(self.url_test_reload)
                self.logs_(f'[INFO] [Open url webbrowser] [url][<span style="color:#1AA8DD;">{self.url_test_reload}</span>]', "INFO_1")
            except:
                self.logs_(f"[ERROR] [Open url webbrowser] [url][{self.url_test_reload}]", "ERROR")

    def reload_page(self):
        self.rl_test.start()

    def check_user_reg_(self):
        self.check_regist.start()

    def set_info_user(self, text_, text_2):
        self.label_14.setText(text_)
        self.label_15.setText(text_2)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap("res/user_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.pushButton_3.setIcon(icon11)
        self.pushButton_10.setIcon(icon11)

    def reg_start(self):
        self.reg_n.start()

    def progress_load_img(self, value_):
        self.progressBar_2.setValue(value_)

    def set_html_browser(self):
        try:
            with open(self.file_read_html_br, "r", encoding="utf-8") as read_html_test:
                read_html = read_html_test.read()
            self.textBrowser_2.setHtml(read_html)
        except:
            self.textBrowser_2.setText("404 сторінка не знайдена ¯\\_(ツ)_/¯")

    def clicked_list_test_(self):
        try:
            for item_num in self.listWidget.selectedIndexes():
                #Reload data
                self.url_test_reload = self.list_tests[item_num.row()]['url']
                self.file_read_html_br = f"temp_data/read_html/index{self.list_tests[item_num.row()]['num_file']}.html"

                with open(self.file_read_html_br, "r", encoding="utf-8") as read_html_test:
                    read_html = read_html_test.read()
                if self.pushButton_7.isChecked() == False:
                    self.download_img.start()

                self.lineEdit_8.setText(self.list_tests[item_num.row()]['url'])
                self.textBrowser_2.setHtml(read_html)
        except:
            self.textBrowser_2.setText("404 сторінка не знайдена ¯\\_(ツ)_/¯")

    def info_search_label(self, text_):
        self.label_3.setText(text_)

    def update_list_widget(self):
        self.listWidget.clear()
        self.list_tests = []
        if self.radioButton_14.isChecked() == True:
            self.list_tests = self.list_tests_null

        if self.radioButton_13.isChecked() == True:
            if self.checkBox.isChecked() != True:
                self.list_tests = sorted(self.list_tests_null, key=lambda user: user['num_q'], reverse=self.radioButton_16.isChecked())
            else:
                for items_list_null in self.list_tests_null:
                    if self.spinBox_12.value() >= items_list_null['num_q']:
                        if self.spinBox_10.value() <= items_list_null['num_q']:
                            self.list_tests.append(items_list_null)
                self.list_tests = sorted(self.list_tests, key=lambda user: user['max_'], reverse=self.radioButton_16.isChecked())

        if self.radioButton_12.isChecked() == True:
            if self.checkBox.isChecked() != True:
                self.list_tests = sorted(self.list_tests_null, key=lambda user: user['max_'], reverse=self.radioButton_16.isChecked())
            else:
                for items_list_null in self.list_tests_null:
                    if self.spinBox_13.value() >= items_list_null['max_']:
                        if self.spinBox_11.value() <= items_list_null['max_']:
                            self.list_tests.append(items_list_null)
                self.list_tests = sorted(self.list_tests, key=lambda user: user['num_q'], reverse=self.radioButton_16.isChecked())

        for wr_item_list_test in self.list_tests:
            icon_max_ = "error.png"
            if wr_item_list_test['ERROR'] != True:
                if int(wr_item_list_test['max_']) >= 90:
                    icon_max_ = "100_.png"
                if int(wr_item_list_test['max_']) < 90:
                    icon_max_ = "50_.png"
                if int(wr_item_list_test['max_']) < 50:
                    icon_max_ = "0_.png"

            item = QtWidgets.QListWidgetItem()
            item.setText(f"[{wr_item_list_test['num_q']}] [{wr_item_list_test['max_']}%]     [{wr_item_list_test['class_num']}] [{wr_item_list_test['lesson_name']}]")
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(f"res/{icon_max_}"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            item.setIcon(icon)
            self.listWidget.addItem(item)

    def settings_save(self):
        settings = {
            "google_page": self.spinBox.value(),
            "bing_page": self.spinBox_2.value(),
            "naurok_page": self.spinBox_3.value(),
            "time_question_min": self.spinBox_4.value(),
            "time_question_max": self.spinBox_5.value(),
            "deliberate_mistake_min": self.spinBox_6.value(),
            "deliberate_mistake_max": self.spinBox_7.value(),
            "img_x": self.spinBox_8.value(),
            "img_y": self.spinBox_9.value()
        }

        with open("data/settings.json", "w", encoding="utf-8") as settings_w:
            json.dump(settings, settings_w, ensure_ascii=False, indent=4)

    def settings_load(self):
        try:
            with open("data/settings.json", "r", encoding="utf-8") as settings_r:
                settings_loads = json.load(settings_r)

            self.spinBox.setValue(settings_loads["google_page"])
            self.spinBox_2.setValue(settings_loads["bing_page"])
            self.spinBox_3.setValue(settings_loads["naurok_page"])
            self.spinBox_4.setValue(settings_loads["time_question_min"])
            self.spinBox_5.setValue(settings_loads["time_question_max"])
            self.spinBox_6.setValue(settings_loads["deliberate_mistake_min"])
            self.spinBox_7.setValue(settings_loads["deliberate_mistake_max"])
            self.spinBox_8.setValue(settings_loads["img_x"])
            self.spinBox_9.setValue(settings_loads["img_y"])
            self.logs_("[INFO] [Settings load]", "INFO_1")
        except:
            self.logs_("[ERROR] [Settings load]", "ERROR")

    def search_question_2(self):
        self.stackedWidget.setCurrentIndex(0)

    def search_question_1(self):
        self.stackedWidget.setCurrentIndex(1)

    def search_question_0(self):
        self.stackedWidget.setCurrentIndex(1)
        self.lineEdit_2.setText(self.lineEdit.text())
        self.search_question()

    def search_question(self):
        self.label_3.setText("About 0 results (0.0 seconds)")
        self.list_tests_null = []
        self.listWidget.clear()
        self.search_parser.start()

    def logs_(self, text_log, type_log):
        self.data_d = time.strftime('%Y-%m-%d')
        self.data_t = time.strftime('%H:%M:%S')

        text_log_txt = text_log.replace('<span style="color:#1AA8DD;">', "")
        text_log_txt = text_log_txt.replace('</span>', "")
        text_log_txt = text_log_txt.replace('<br>', "")

        with open(f"logs/txt/{self.data_d}.log", "a", encoding="utf-8") as log_wr:
            log_wr.write(f'[{self.data_t}] {text_log_txt}\n')

        if type_log == "ERROR":
            self.textBrowser.append(f'<span style="color:#F23F43;">[{self.data_t}] {text_log}</span>')
            with open(f"logs/html/{self.data_d}.html", "a", encoding="utf-8") as log_wr:
                log_wr.write(f'<span style="color:#F23F43;">[{self.data_t}] {text_log}</span><br>\n')

        if type_log == "INFO_0":
            self.textBrowser.append(f'<span>[{self.data_t}] {text_log}</span>')
            with open(f"logs/html/{self.data_d}.html", "a", encoding="utf-8") as log_wr:
                log_wr.write(f'<span>[{self.data_t}] {text_log}</span><br>\n')

        if type_log == "INFO_1":
            self.textBrowser.append(f'<span style="color:#F0B232;">[{self.data_t}] {text_log}</span>')
            with open(f"logs/html/{self.data_d}.html", "a", encoding="utf-8") as log_wr:
                log_wr.write(f'<span style="color:#F0B232;">[{self.data_t}] {text_log}</span><br>\n')

    def progress_search(self, value_):
        self.progressBar.setValue(value_)

    def sort_button(self):
        if self.pushButton_8.isChecked() == True:
            self.stackedWidget_2.setCurrentIndex(1)
        else:
            self.stackedWidget_2.setCurrentIndex(0)

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