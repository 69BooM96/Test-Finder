from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileSystemModel, QListWidgetItem, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread
import os
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import V1_p
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
import pickle


class search_browser_test(QThread):
    error_info_browser = QtCore.pyqtSignal(str, str)
    progress_create_test = QtCore.pyqtSignal(int)

    def __init__(self, mainwindows):
        super().__init__()
        self.mainwindows = mainwindows

    def run(self):
        with open('data/settings.json') as f:
            data = json.load(f)

        self.progress_create_test.emit(10)

        try:
            item = self.mainwindows.listWidget_2.currentItem().text()
            item = item.replace(".html", "/realtime")
            print(item)
        except AttributeError:
            item = False

        if item != False:
            if data['Google_b'] == True:
                service = Service("chromedriver.exe")
                options = webdriver.ChromeOptions()

                options.add_argument("--headless")

                driver = webdriver.Chrome(service=service, options=options)
                driver_join_test = webdriver.Chrome(service=service, options=options)
            else:
                service = Service("geckodriver.exe")
                options = webdriver.FirefoxOptions()

                options.headless = True

                driver = webdriver.Firefox(service=service, options=options)

            #Registration
            self.progress_create_test.emit(15)

            driver.get('https://naurok.com.ua/')
            cookies = pickle.load(open("data/cookies", "rb"))
            for cookie in cookies:
                driver.add_cookie(cookie)

            driver.get('https://naurok.com.ua/')

            try:
                driver.find_element(by=By.XPATH, value="/html/body/nav/div/div[2]/ul[2]/li[2]/a/span[1]")
                Registration = True
            except:
                try:
                    driver.get('https://naurok.com.ua/login')
                    time.sleep(1)

                    print(data['email'])
                    print(data['password'])
                    driver.find_element(by=By.XPATH, value="/html/body/div[3]/div/div/div/div[2]/div[1]/form/div[4]/input").send_keys(data['email'])
                    driver.find_element(by=By.XPATH, value="/html/body/div[3]/div/div/div/div[2]/div[1]/form/div[5]/input").send_keys(data['password'])

                    time.sleep(1)
                    driver.find_element(by=By.XPATH, value="/html/body/div[3]/div/div/div/div[2]/div[1]/form/div[8]/button").click()

                    time.sleep(3)
                    try:
                        homepage_description = driver.find_element(by=By.XPATH, value="/html/body/nav/div/div[2]/ul[2]/li[2]/a/span[1]")
                        error_reg = False
                    except:
                        error_reg = True
                except:
                    pass

                if error_reg == True:
                    driver.quit()
                    self.error_info_browser.emit("Registration error", "Сталася помилка під час реєстрації...\n\nПеревірте, чи правильно написано пароль та імейл \nабо спробуйте змінити їх.")
                    Registration = False
                else:
                    pickle.dump(driver.get_cookies(), open("data/cookies", "wb"))

            if data['Firefox'] == True:
                service_j = Service("geckodriver.exe")
                options_j = webdriver.FirefoxOptions()

                options_j.headless = True

                driver_join_test = webdriver.Firefox(service=service_j, options=options_j)

            self.progress_create_test.emit(40)
            driver.get(item)
            driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/div[2]/div/a").click()
            gamecode = driver.find_element(by=By.CLASS_NAME, value='gamecode').text

            #Start Create
            driver_join_test.get('https://naurok.com.ua/test/join')
            time.sleep(2)
            self.progress_create_test.emit(60)
            driver_join_test.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div[1]/div/form/div[1]/input").send_keys(gamecode)
            driver_join_test.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div[1]/div/form/div[2]/input").send_keys(gamecode)

            driver_join_test.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div[1]/div/form/button").click()
            time.sleep(2)
            if 'https://naurok.com.ua/test/join' != driver_join_test.current_url:
                time.sleep(4)
                driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[2]/div[3]/div[2]/a[1]").click()

                url_lists = driver_join_test.current_url
                self.progress_create_test.emit(70)
                time.sleep(5)
                search_selenium = ""
                link_im_t = ""
                exit_test = False
                while True:
                    try:
                        try:
                            link = driver_join_test.find_element(by=By.XPATH, value="/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/div[1]/div/div[2]/div").text
                        except:
                            link = driver_join_test.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div/div/div/div[2]/div[1]/div/div[2]/div").text
                        try:
                            link_i = driver_join_test.find_element(by=By.XPATH, value="/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/div[1]/div/div[1]/img")
                            if link_i.get_attribute('src') == None:
                                pass
                            else:
                                if link_i.get_attribute('src') != link_im_t:
                                    link_im_t = link_i.get_attribute('src')
                        except:
                            pass
                        if search_selenium != link:
                            if exit_test == True:
                                break

                            if link != "":
                                driver_join_test.find_element(by=By.XPATH, value="/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div").click()
                                exit_test = True
                                self.progress_create_test.emit(80)
                    except:
                        pass

                    time.sleep(0.2)

            self.progress_create_test.emit(90)
            time.sleep(3)
            driver_join_test.find_element(by=By.XPATH, value="/html/body/div[1]/div/div[2]/nav/div/div/div[3]/div/a[3]/i").click()

            while True:
                if url_lists != driver_join_test.current_url:
                    break
                time.sleep(1)

            self.progress_create_test.emit(100)
            self.mainwindows.listWidget.addItem(driver_join_test.current_url)



            time.sleep(1)
            if Registration == True:
                self.progress_create_test.emit(0)
                driver.quit()
                driver_join_test.quit()
            else:
                self.progress_create_test.emit(0)
                driver_join_test.quit()


class browser_test(QThread):
    def __init__(self, mainwindows):
        super().__init__()
        self.mainwindows = mainwindows

    def run(self):
        with open('data/settings.json') as f:
            data = json.load(f)

        if data['Google_b'] == True:
            service = Service("chromedriver.exe")
            options = webdriver.ChromeOptions()
            driver = webdriver.Chrome(service=service, options=options)
        else:
            service = Service("geckodriver.exe")
            options = webdriver.FirefoxOptions()
            driver = webdriver.Firefox(service=service, options=options)

        try:
            driver.get('https://naurok.com.ua/test/join')
            search_selenium = ""
            link_im_t = ""
            while True:
                if 'https://naurok.com.ua/test/join' != driver.current_url:
                    try:
                        try:
                            link = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/div[1]/div/div[2]/div").text
                        except:
                            link = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div/div/div/div[2]/div[1]/div/div[2]/div").text
                        try:
                            link_i = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/div[1]/div/div[1]/img")
                            if link_i.get_attribute('src') == None:
                                pass
                            else:
                                if link_i.get_attribute('src') != link_im_t:
                                    link_im_t = link_i.get_attribute('src')
                        except:
                            pass
                        if search_selenium != link:
                            if link != "":
                                search_selenium = link
                                self.mainwindows.lineEdit_6.setText(link)
                                self.mainwindows.inputs_text_lineEdit = False
                                self.mainwindows.parser_n.start()
                                self.mainwindows.listWidget_2.clear()
                    except:
                        pass

                time.sleep(1)
        except:
            pass
        driver.quit()
        self.mainwindows.pushButton_15.setEnabled(True)

class update_settings(QThread):
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow

    def run(self):
        while True:
            sl = self.mainwindow.horizontalSlider_2.value()
            self.mainwindow.spinBox_2.setValue(sl)

            sl_1 = self.mainwindow.horizontalSlider_3.value()
            self.mainwindow.spinBox.setValue(sl_1)

            sl_2 = self.mainwindow.horizontalSlider.value()
            self.mainwindow.spinBox_3.setValue(sl_2)
            time.sleep(0.1)

#Info test
class info_test(QThread):
    info_test_signal = QtCore.pyqtSignal(str)
    load_gif = QtCore.pyqtSignal(str)

    def __init__(self, mainwindows):
        super().__init__()
        self.mainwindows = mainwindows

    def run(self):
        self.load_gif.emit("1")
        with open("data/list_info_test.log", "w", encoding="utf-8") as f:
            f.write("")
        self.load_gif.emit("2")
        try:
            clear_image = os.listdir("data/image")
            for clear_image_d in clear_image:
                os.remove(f"data/image/{clear_image_d}")
            self.load_gif.emit("3")
        except:
            self.load_gif.emit("3")
            pass

        #List_url
        if self.mainwindows.list_test_widget == True:
            item = self.mainwindows.listWidget_2.currentItem().text()
        else:
            item = self.mainwindows.lineEdit_5.text()
            self.mainwindows.listWidget_2.addItem(item)

        try:
            self.load_gif.emit("4")
            r = requests.get(item)
            soup = BeautifulSoup(r.content, "lxml")
            self.load_gif.emit("1")

            n_p = 1
            test_questions = soup.find_all("div", class_="col-md-9 col-sm-8")
            for test_que in test_questions:
                #Image test
                try:
                    image_test_link = soup.find("div", class_="preview-image").find("img").get("src")
                    image_test_name = image_test_link.split('/')[-1]
                    r_image_test = requests.get(image_test_link, allow_redirects=True)
                    with open(f"data/image/{image_test_name}", "wb") as image_test_w:
                        image_test_w.write(r_image_test.content)

                    img_obj = Image.open(f"data/image/{image_test_name}")
                    img_obj = img_obj.resize((300, 300), Image.LANCZOS)
                    img_obj.save(f"data/image/{image_test_name}")

                    question_test2 = f'<img src="data/image/{image_test_name}">'
                    with open("data/list_info_test.log", "a", encoding="utf-8") as f:
                        f.write(question_test2)
                except:
                    pass
                #Name test
                test_names = soup.find("h1", class_="h1-block h1-single").text
                name_test = f'<p style=" font-size:12pt; font-weight:600;">{test_names}<p>'
                with open("data/list_info_test.log", "a", encoding="utf-8") as f:
                    f.write(name_test)
                #Num test
                number_t = soup.find("div", class_="block-head").text
                number_test = f'<p style=" font-size:13pt; font-weight:600; margin-left: 10px"> {number_t}<p>'
                with open("data/list_info_test.log", "a", encoding="utf-8") as f:
                    f.write(number_test)

                test_ques = test_que.find_all("div", class_="content-block entry-item question-view-item")
                for test_quest in test_ques:
                    num_test = test_quest.find("div", class_="question-label")
                    num_test1 = num_test.text.replace("\n", "")
                    num_test2 = f'<br /><br /><p style=" font-size:8pt; font-weight:600;"># {num_test1}<p>'
                    with open("data/list_info_test.log", "a", encoding="utf-8") as f:
                        f.write(num_test2)


                    question_test = test_quest.find("div", class_="question-view-item-content")
                    #Image question
                    try:
                        image_test_question_link = question_test.find("div", class_="col-md-3").find("img").get("src")
                        image_test_question_name = image_test_question_link.split('/')[-1]
                        r_image_question_test = requests.get(image_test_question_link, allow_redirects=True)
                        with open(f"data/image/{image_test_question_name}", "wb") as image_question_test_w:
                            image_question_test_w.write(r_image_question_test.content)

                        img_obj = Image.open(f"data/image/{image_test_question_name}")
                        img_obj = img_obj.resize((200, 200), Image.LANCZOS)
                        img_obj.save(f"data/image/{image_test_question_name}")

                        question_test1 = question_test.text.replace("\n", "")
                        question_test2 = f'<br /><img src="data/image/{image_test_question_name}"><p style=" font-size:10pt; font-weight:600; color:#cdf078;"> 📄 {question_test1}<p>'
                        with open("data/list_info_test.log", "a", encoding="utf-8") as f:
                            f.write(question_test2)
                    except:
                        question_test1 = question_test.text.replace("\n", "")
                        question_test2 = f'<p style=" font-size:10pt; font-weight:600; color:#cdf078;"> 📄 {question_test1}<p>'
                        with open("data/list_info_test.log", "a", encoding="utf-8") as f:
                            f.write(question_test2)

                    #Image answer
                    answer_test = test_quest.find("div", class_="question-options")
                    try:
                        answer_tes = answer_test.find_all("div", class_="image-only-option")
                        for answer_tes2 in answer_tes:
                            answer_tes1 = answer_tes2.find("img").get("src")
                            answer_tes_name = answer_tes1.split('/')[-1]

                            r_image_answer_test = requests.get(answer_tes1, allow_redirects=True)
                            with open(f"data/image/{answer_tes_name}", "wb") as image_answer_test_w:
                                image_answer_test_w.write(r_image_answer_test.content)

                            img_obj = Image.open(f"data/image/{answer_tes_name}")
                            img_obj = img_obj.resize((200, 200), Image.LANCZOS)
                            img_obj.save(f"data/image/{answer_tes_name}")
                            
                            answer_tes3 = f'<p style=" font-size:8pt; font-weight:600; margin-left: 20px;">🔘 <img src="data/image/{answer_tes_name}"><p>'
                            with open("data/list_info_test.log", "a", encoding="utf-8") as f:
                                f.write(answer_tes3)
                    except:
                        pass
                    answer_tes = answer_test.find_all("div", class_="option-text")
                    for answer_tes2 in answer_tes:
                        answer_tes1 = answer_tes2.text.replace("\n", "")
                        answer_tes3 = f'<p style=" font-size:8pt; font-weight:600; margin-left: 20px;">🔘 {answer_tes1}<p>'
                        with open("data/list_info_test.log", "a", encoding="utf-8") as f:
                            f.write(answer_tes3)
                    
                    n_p += 1
                    if n_p > 4:
                        n_p = 0
                    self.load_gif.emit(f"{n_p}")

            self.load_gif.emit("2")
            self.info_test_signal.emit("OK")

        except:
            with open("data/list_info_test.log", "w", encoding="utf-8") as f:
                f.write("ERROR")
            self.load_gif.emit("2")
            self.info_test_signal.emit("ERROR")

        self.mainwindows.pushButton.setEnabled(True)
        self.mainwindows.pushButton_14.setEnabled(True)

#Parser
class parser(QThread):
    progress_update_signal = QtCore.pyqtSignal(int)

    def __init__(self, mainwindows):
        super().__init__()
        self.mainwindows = mainwindows

    def run(self):
        with open('data/url_test.log', 'w', encoding='utf-8') as clear_url:
            clear_url.write("")

        day_date = time.strftime('DATE: [%Y-%m-%d][%H:%M:%S]')
        day_d = time.strftime('%Y-%m-%d')

        if self.mainwindows.inputs_text_lineEdit == True:
            inputs_num = self.mainwindows.spinBox_5.text()
            inputs_text = self.mainwindows.lineEdit.text()
        else:
            inputs_text = self.mainwindows.lineEdit_6.text()

        #Google
        inputs_text_2 = inputs_text.replace(" ", "+")
        link = "https://www.google.com/search?q=на+урок+тест+" + inputs_text_2
        header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

        with open(f"logs/search_{day_d}.log", "a", encoding="utf-8") as write_file_log:
            write_file_log.write(f"\n\n{day_date}\n│\n├─ [Google]: [{link}]")
        try:
            response = requests.get(link, headers=header)
            soup = BeautifulSoup(response.text, "lxml")

            with open(f"logs/search_{day_d}.log", "a", encoding="utf-8") as write_file_log:
                write_file_log.write(f"\n│         ├─ [OK]\n│         │")

            user_n = soup.find(class_="v7W49e").find_all("a")
            for links in user_n:
                block = links.get("href")
                import re
                if re.search(r'\bhttps://naurok.com.ua/test/\b', block):
                    with open(f"data/url_test.log", "a", encoding="utf-8") as write_file_log:
                        write_file_log.write(f"{block}\n")

        except:
            with open(f"logs/search_{day_d}.log", "a", encoding="utf-8") as write_file_log:
                write_file_log.write(f"\n│         └─ [ERROR]\n│         │")

        #Check test
        progress_test_n = 0

        file = open('data/url_test.log', 'r', encoding='utf-8')
        for i in file:
            progress_test_n += 1
        file.close()

        if progress_test_n == 0:
            with open(f"logs/search_{day_d}.log", "a", encoding="utf-8") as write_file_log:
                write_file_log.write(f"\n│         └─ [Url]: [None]")
        else:
            progress_test_p = 100/progress_test_n

            file = open('data/url_test.log', 'r', encoding='utf-8')
            progress_test_s = 0
            for block in file:
                block = block.replace("\n", "")
                try:
                    with open(f"logs/search_{day_d}.log", "a", encoding="utf-8") as write_file_log:
                        write_file_log.write(f"\n│         ├─ [Url]: [Google][{block}]")

                    r = requests.get(str(block))
                    soup = BeautifulSoup(r.content, "lxml")

                    num_t = soup.find_all("div", class_="block-head")
                    for num_t2 in num_t:
                        num_t3 = num_t2.text.replace(" запитань", "")
                        num_t4 = num_t3.replace(" запитання", "")
                        test_n = soup.find_all("h1", class_="h1-block h1-single")
                        for test_name in test_n:
                            with open(f"logs/search_{day_d}.log", "a", encoding="utf-8") as write_file_log:
                                write_file_log.write(f"\n│         │        ├─ [OK]\n│         │        ├─ [test]: [{test_name.text}]\n│         │        └─ [number of questions]: [{num_t4}]\n│         │")

                            #Update
                            self.mainwindows.listWidget_2.addItem(block)
                except:
                    with open(f"logs/search_{day_d}.log", "a", encoding="utf-8") as write_file_log_error:
                        write_file_log_error.write("\n│         │        └─ [ERROR]\n│         │")

                progress_test_s += progress_test_p
                self.progress_update_signal.emit(int(progress_test_s))

            file.close()

            with open(f"logs/search_{day_d}.log", "a", encoding="utf-8") as write_file_log:
                write_file_log.write(f"\n│         └─ [number of tests]: [{progress_test_n}]")

        #Stops
        day_date_s = time.strftime('DATE: [%Y-%m-%d][%H:%M:%S]')
        with open(f"logs/search_{day_d}.log", "a", encoding="utf-8") as write_file_log:
            write_file_log.write(f"\n│\n└─ [STOP]: {day_date_s}")

        self.progress_update_signal.emit(0)
        self.mainwindows.pushButton.setEnabled(True)
        self.mainwindows.pushButton_14.setEnabled(True)



#Menu
class ExampleApp(QtWidgets.QMainWindow, V1_p.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #Button
        self.pushButton.clicked.connect(self.inputs)
        self.pushButton_14.clicked.connect(self.inputs_url)
        self.pushButton_3.clicked.connect(self.save_sattings)
        self.pushButton_15.clicked.connect(self.start_browser)
        self.pushButton_2.clicked.connect(self.create_browser_test)

        #List
        self.listWidget_2.doubleClicked.connect(self.open_link_url_list)
        self.listWidget_2.clicked.connect(self.link_url_list)

        self.listWidget.doubleClicked.connect(self.open_link_answers_url_list)

        #Parser
        self.parser_n = parser(mainwindows=self)
        self.parser_n.progress_update_signal.connect(self.update_log)

        #Info test
        self.p_info_test = info_test(mainwindows=self)
        self.p_info_test.info_test_signal.connect(self.update_info_test)
        self.p_info_test.load_gif.connect(self.load_gif_an)

        #Update settings
        self.Update_s = update_settings(mainwindow=self)
        self.Update_s.start()
        self.settings_app()

        #Browser
        self.browser_open = browser_test(mainwindows=self)
        self.search_browser = search_browser_test(mainwindows=self)
        self.search_browser.error_info_browser.connect(self.info_error)
        self.search_browser.progress_create_test.connect(self.progress_test_create)

    def progress_test_create(self, value):
        self.progressBar_2.setValue(value)

    def info_error(self, title_error, value):
        msg = QMessageBox()
        msg.setWindowTitle(title_error)
        msg.setText(value)
        msg.setIcon(QMessageBox.Critical)

        msg.exec_()

    def create_browser_test(self):
        self.search_browser.start()

    def start_browser(self):
        self.browser_open.start()
        self.pushButton_15.setEnabled(False)

    def settings_app(self):
        file = open("data/settings.json", "r")
        data = json.load(file)

        self.lineEdit_4.setText(data['email'])
        self.lineEdit_3.setText(data['password'])
        self.lineEdit_2.setText(data['name'])
        self.horizontalSlider_2.setValue(data['Naurok'])
        self.horizontalSlider_3.setValue(data['Google'])
        self.horizontalSlider.setValue(data['Bing'])
        self.radioButton.setChecked(data['Google_b'])
        self.radioButton_2.setChecked(data['Firefox'])

    def load_gif_an(self, value):
        if value == "1":
            self.textBrowser_3.setHtml('<br /><br /><img src="res/load1.png">')
        elif value == "2":
            self.textBrowser_3.setHtml('<br /><br /><img src="res/load2.png">')
        elif value == "3":
            self.textBrowser_3.setHtml('<br /><br /><img src="res/load3.png">')
        elif value == "4":
            self.textBrowser_3.setHtml('<br /><br /><img src="res/load4.png">')

    def update_info_test(self, value):
        with open("data/list_info_test.log", "r", encoding="utf-8") as f:
            self.textBrowser_3.setHtml(f.read())

    def update_log(self, value):
        day_d = time.strftime('%Y-%m-%d')
        with open(f"logs/search_{day_d}.log", "r", encoding="utf-8") as read_file_log:
            read_log = read_file_log.read()
        self.textBrowser_4.setText(read_log)
        self.progressBar.setValue(value)
        self.progressBar_3.setValue(value)

    def inputs(self):
        self.inputs_text_lineEdit = True
        self.parser_n.start()
        self.pushButton.setEnabled(False)
        self.pushButton_14.setEnabled(False)
        inputs_num = self.spinBox_5.text()
        inputs_text = self.lineEdit.text()

        self.listWidget.clear()
        self.listWidget_2.clear()

        day_date = time.strftime('DATE: [%Y-%m-%d][%H:%M:%S]')
        self.textBrowser_2.setText(f'\n{day_date}\n\nПитання: {inputs_text}\nКількість питань: {inputs_num}')

    def inputs_url(self):
        self.list_test_widget = False
        self.p_info_test.start()

        self.listWidget_2.clear()
        inputs_text = self.lineEdit_5.text()
        self.pushButton.setEnabled(False)
        self.pushButton_14.setEnabled(False)

        day_date = time.strftime('DATE: [%Y-%m-%d][%H:%M:%S]')
        self.textBrowser_2.setText(f'\n{day_date}\n\nUrl: {inputs_text}')

    def link_url_list(self):
        self.list_test_widget = True
        self.p_info_test.start()

    def open_link_url_list(self):
        item = self.listWidget_2.currentItem().text()
        webbrowser.open_new_tab(item)

    def open_link_answers_url_list(self):
        item = self.listWidget.currentItem().text()
        webbrowser.open_new_tab(item)

    def save_sattings(self):
        with open('data/settings.json') as f:
            data = json.load(f)


        data['email'] = self.lineEdit_4.text()
        data['password'] = self.lineEdit_3.text()
        data['name'] = self.lineEdit_2.text()
        data['Naurok'] = self.horizontalSlider_2.value()
        data['Google'] = self.horizontalSlider_3.value()
        data['Bing'] = self.horizontalSlider.value()
        data['Google_b'] = self.radioButton.isChecked()
        data['Firefox'] = self.radioButton_2.isChecked()

        with open('data/settings.json', 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
