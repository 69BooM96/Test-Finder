import json

import requests
import asyncio
import aiohttp

from time import sleep
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from modules.decorate import async_session
from modules.plugin_param import *


class Load_data:
    def __init__(self, cookies=None, qt_logs=None):
        self.qt_logs = qt_logs
        self.cookies = {item["name"]: item["value"] for item in cookies} if cookies else None

    def search(self, subject="", klass=0, q="", storinka=(1,2), proxy=None) -> list[str]:
        async def async_search(session: aiohttp.ClientSession, storinka=1):
            async with session.get(f"https://naurok.com.ua/test{subject}/?klas-{klass}&q={q}&storinka={storinka}", proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            if self.qt_logs: self.qt_logs.emit("info", f"Naurok", f" [{req.status}] [{str(req.url)}]")

            return ["https://naurok.com.ua" + obj.find("a").get("href") for obj in soup.find_all(class_="headline")]

        @async_session(self.cookies)
        async def run(session):
            task = [async_search(session, storinka=item) for item in range(*storinka)]
            return await asyncio.gather(*task)

        return list(set(item2 for item in asyncio.run(run()) for item2 in item))

    def search_by_url(self, url: list, proxy=None) -> list[dict]:
        """Получение вопросов по UUID типо
         https://naurok.com.ua/test/testing/0fad247b-cb1d-4355-b946-062bba08d6a6"""

        async def async_search_by_url(session: aiohttp.ClientSession, url):
            async with session.get(url, proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")
            id = soup.find(class_="{{test.font}}").get("ng-init").split(",")[1]

            async with session.get(f"https://naurok.com.ua/api2/test/sessions/{id}", proxy=proxy) as res:
                res = await res.json()

            return [
                {
                    "type": item.get("type"),
                    "text": BeautifulSoup(item.get("content"), "lxml").text.strip(),
                    "img": item.get("image"),
                    "value": [
                        {
                            "text": BeautifulSoup(item2.get("value"), "lxml").text.strip(),
                            "img": item2.get("image")
                        }
                    for item2 in item["options"]
                    ]
                }
            for item in res["questions"]
            ]

        @async_session(self.cookies)
        async def run(session):
            task = [async_search_by_url(session, url) for url in url]
            return await asyncio.gather(*task)

        return asyncio.run(run())

    def processing_data(self, url: list, proxy=None) -> list[dict]:
        """Получение вопросов с не пройденного теста"""
        async def async_processing_data(session: aiohttp.ClientSession, url):
            async with session.get(url, proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            if self.qt_logs: self.qt_logs.emit("info", f"Naurok", f" [{req.status}] [{str(req.url)}]")

            return {
                "platform": "naurok",
                "type_data": "test",
                "url": str(req.url),
                "name_test": soup.find(class_="h1-block h1-single").text,
                "object": soup.find_all(attrs={"itemprop": "name"})[1].text if len(soup.find_all(attrs={"itemprop": "name"})) >= 2 else None,
                "klass": soup.find_all(attrs={"itemprop": "name"})[2].text if len(soup.find_all(attrs={"itemprop": "name"})) >= 3 else None,

                "answers": [{
                    "type": "quiz" if obj.find(class_="option-marker quiz") else "multiquiz",
                    "text": obj.find(class_="question-view-item-content").text.strip().replace(" ", "").replace("﻿", "") if obj.find(class_="question-view-item-content") else None,
                    "img": obj.find(class_="question-view-item-image").get("src") if obj.find(class_="question-view-item-image") else None,
                    "value": [
                        {
                        "text": item.find("p").text.strip().replace(" ", "").replace("﻿", "") if item.find("p") else None,
                        "img": item.find("img").get("src") if item.find("img") else None,
                        "correctness": None
                    } for item in obj.select('.question-options > div')]
                } for obj in soup.find(class_="col-md-9 col-sm-8").find_all(class_="content-block entry-item question-view-item")]
            }

        @async_session(self.cookies)
        async def run(session):
            task = [async_processing_data(session, url) for url in url if url if url[:27] == "https://naurok.com.ua/test/"]
            return await asyncio.gather(*task)

        return asyncio.run(run())

    def create_test(self, url: list, proxy=None) -> list[str]:
        """создание теста"""
        async def async_get_test(session: aiohttp.ClientSession, url):
            async with session.get(url, proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            if self.qt_logs: self.qt_logs.emit("info", f"Naurok", f" [{req.status}] [{str(req.url)}]")

            data = {
                "_csrf": soup.find(attrs={"name": "csrf-token"}).get("content"),
                "Homework[name]": "Test-Finder",
                "Homework[deadline_day]": soup.find(id="homework-deadline_day").find_all("option")[3].get("value"),
                "Homework[deadline_hour]": "18:00",
                "Homework[shuffle_question]": 0,
                "Homework[shuffle_options]": [
                    0,
                    1
                ],
                "Homework[show_answer]": 0,
                "Homework[show_review]": [
                    0,
                    1
                ],
                "Homework[show_leaderbord]": [
                    0,
                    1
                ],
                "Homework[available_attempts]": 0,
                "Homework[duration]": 40,
                "Homework[show_timer]": 0,
                "Homework[show_flashcard]": 0,
                "Homework[show_match]": 0
            }

            async with session.get(url, data=data, proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            return soup.find(class_="form-control input-xs").get("value").split("=")[-1]

        @async_session(self.cookies)
        async def run(session):
            task = [async_get_test(session, f"{url[:-5]}/set") for url in url]
            return await asyncio.gather(*task)

        return asyncio.run(run())

    def test_pass(self, gamecode: list, proxy=None) -> list[str]:
        """получение ответов с теста по геймкоду который возврощяет create_test"""
        async def async_test_pass(session: aiohttp.ClientSession, gamecode):
            async with session.get("https://naurok.com.ua/test/join", proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            if self.qt_logs: self.qt_logs.emit("info", f"Naurok", f" [{req.status}] [{str(req.url)}]")

            data = {
                "_csrf": soup.find(attrs={"name": "csrf-token"}).get("content"),
                "JoinForm[gamecode]": gamecode,
                "JoinForm[name]": "Test-Finder"
            }

            async with session.post("https://naurok.com.ua/test/join", data=data, proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            if self.qt_logs: self.qt_logs.emit("info", f"Naurok", f" [{req.status}] [{str(req.url)}]")

            session_id = soup.find(class_="{{test.font}}").get("ng-init").split(",")[1]

            async with session.get(f"https://naurok.com.ua/api2/test/sessions/{session_id}", proxy=proxy) as req:
                session_res = await req.json()

            if self.qt_logs: self.qt_logs.emit("info", f"Naurok", f" [{req.status}] [{str(req.url)}]")

            data = {
                "answer": [
                    session_res["questions"][0]["options"][0]["id"]
                ],
                "homework": True,
                "homeworkType": 1,
                "point":  session_res["questions"][0]["point"],
                "question_id": session_res["questions"][0]["id"],
                "session_id": session_res["session"]["id"],
                "show_answer": session_res["settings"]["show_answer"],
                "type": session_res["questions"][0]["type"]
            }

            async with session.put("https://naurok.com.ua/api2/test/responses/answer", data=data) as req: await req.text()
            async with session.put(f"https://naurok.com.ua/api2/test/sessions/end/{session_id}") as req:
                uuid = await req.json()
                return "https://naurok.com.ua/test/complete/" + uuid["session"]["uuid"]

        @async_session(self.cookies)
        async def run(session):
            task = [async_test_pass(session, gamecode) for gamecode in gamecode]
            return await asyncio.gather(*task)

        return asyncio.run(run())

    def get_answer(self, url: list, proxy=None) -> list[dict]:
        """получение полных ответов с конечной сылки которая возврощяется test_pass (Очень похожа на processing_data)"""
        async def async_get_answer(session: aiohttp.ClientSession, url):
            async with session.get(url, proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            if self.qt_logs: self.qt_logs.emit("info", f"Naurok", f" [{req.status}] [{str(req.url)}]")

            return [{
                "type": obj.find(class_="homework-stat-option-line").find("span")['class'][1] if obj.find(class_="homework-stat-option-line").find("span") else None,
                "text": "".join([item.text.strip() for item in obj.find(class_='homework-stat-question-line').find_all('p', recursive=False)]).replace(" ", "").replace("﻿", ""),
                "img": obj.find("img").get("src") if obj.find(class_="col-md-6") else None,
                "value": [{
                    "text": item.find("p").text.strip().replace(" ", "").replace("﻿", "") if item.find("p") else None,
                    "img": item.find("img").get("src") if item.find("img") else None,
                    "correctness": True if item.find("span")['class'][0] == "correct" else False
                } for item in obj.find(class_="homework-stat-options").find_all(class_="row")]
            } for obj in soup.find(class_="homework-stats").find_all(class_="content-block")]

        @async_session(self.cookies)
        async def run(session):
            task = [async_get_answer(session, url) for url in url]
            return await asyncio.gather(*task)

        return asyncio.run(run())

class CreateTest:
    def __init__(self, name_test: str, subject: int, klass: int, cookies: list[dict], qt_logs=None):
        self.qt_logs = qt_logs

        self.session = requests.Session()
        self.session.cookies.update({i["name"]: i["value"] for i in cookies})
        self.session.headers.update({"user-agent": UserAgent().random})

        req = self.session.get("https://naurok.com.ua/test/create")
        soup = BeautifulSoup(req.text, "lxml")

        if self.qt_logs: self.qt_logs.emit("info", f"Naurok", f" [{req.status_code}] [{str(req.url)}]")

        data = {
            '_csrf': soup.find('input', attrs={'name': '_csrf'})["value"],
            'Document[name]': name_test,
            'Document[subject_id]': str(subject),
            'Document[grade_id]': str(klass)
        }

        req = self.session.post("https://naurok.com.ua/test/create", data=data, files={'Document[image]': ('', b'')})
        self.doc_id = req.url.split("/")[-1]
        self.csrf = soup.find('meta', {'name': 'csrf-token'})['content']

    def create_question(self, question: str, answers: dict[str, bool]):
        data = {
            "_csrf": self.csrf,
            "content": question,
            "document_id": self.doc_id,
            "hint": 0,
            "hint_description": "",
            "hint_penalty": 2,
            "id": False,
            "order": 1,
            "point": 1,
            "type": "quiz" if sum(answers.values()) <= 1 else 'multiquiz',
            "options": [{
                "value": key if key[:62] != "https://naurok-test2.nyc3.digitaloceanspaces.com/uploads/test/" else None,
                "correct": 1 if answers[key] else 0,
                "image": key if key[:62] == "https://naurok-test2.nyc3.digitaloceanspaces.com/uploads/test/" else None}
            for key in answers]
        }

        req = self.session.post('https://naurok.com.ua/api/test/questions?expand=options', json=data)

        if self.qt_logs: self.qt_logs.emit("info", f"Naurok", f" [{req.status_code}] [{str(req.url)}]")

    def end_create(self):
        req = self.session.put(f"https://naurok.com.ua/api/test/documents/{self.doc_id}")

        if self.qt_logs: self.qt_logs.emit("info", f"Naurok", f" [{req.status_code}] [{str(req.url)}]")

        return f"https://naurok.com.ua/test/{req.json()["slug"]}.html"

class AutoComplite(MainAutoComplite):
    def __init__(self, gamecode: str, name: str, cookies):
        super().__init__()
        self.session = requests.Session()
        cookies = {item["name"]: item["value"] for item in cookies} if cookies else None
        self.session.cookies.update(cookies)
        self.session.headers.update({"user-agent": UserAgent().random})

        req = self.session.get("https://naurok.com.ua/test/join")
        soup = BeautifulSoup(req.text, "lxml")

        data = {
            "_csrf": soup.find(attrs={"name": "_csrf"}).get("value"),
            "JoinForm[gamecode]": gamecode,
            "JoinForm[name]": name
        }

        self.req = self.session.post("https://naurok.com.ua/test/join", data=data)
        soup = BeautifulSoup(self.req.text, "lxml")

        self.id = soup.find(class_="{{test.font}}").get("ng-init").split(",")[1]
        self.questions = self.session.get("https://naurok.com.ua/api2/test/sessions/" + self.id).json()["questions"]
        self.point = sum(int(item["point"]) for item in self.questions)

    def var(self):
        for item in self.questions:
            yield {
                "id": item["id"],
                "type": item["type"],
                "point": item["point"],
                "text": BeautifulSoup(item["content"], "lxml").text.strip(),
                "img": item["image"],
                "answers": [
                    {
                    "id": i["id"],
                    "text": BeautifulSoup(i["value"], "lxml").text.strip(),
                    "img": i["image"]
                    }
                for i in item["options"]
                ]
            }

    def answer(self, queshion, index_answer: list):
        data = {
            "answer": [queshion["answers"][index]["id"] for index in index_answer],
            "homework": True,
            "homeworkType": 1,
            "point": queshion["point"],
            "question_id": queshion["id"],
            "session_id": self.id,
            "show_answer": 0,
            "type": queshion["type"]
        }

        self.session.put("https://naurok.com.ua/api2/test/responses/answer", json=data)

    def end(self):
        self.session.put("https://naurok.com.ua/api2/test/sessions/end/" + self.id)
        return "https://naurok.com.ua/test/complete/" + self.req.url.split("/")[-1]

class Main(MainPlugin):
    subject = {
        "algebra": ("/algebra", 1),
        "angliyska-mova": ("/angliyska-mova", 34),
        "astronomiya": ("/astronomiya", 40),
        "biologiya": ("/biologiya", 3),
        "vsesvitnya-istoriya": ("/vsesvitnya-istoriya", 9),
        "geografiya": ("/geografiya", 4),
        "geometriya": ("/geometriya", 5),
        "gromadyanska-osvita": ("/gromadyanska-osvita", 50),
        "ekologiya": ("/ekologiya", 41),
        "ekonomika": ("/ekonomika", 37),
        "etika": ("/etika", 45),
        "zarubizhna-literatura": ("/zarubizhna-literatura", 6),
        "zahist-vitchizni": ("/zahist-vitchizni", 43),
        "informatika": ("/informatika", 7),
        "inshi-inozemni-movi": ("/inshi-inozemni-movi", 53),
        "ispanska-mova": ("/ispanska-mova", 44),
        "istoriya-ukraini": ("/istoriya-ukraini", 8),
        "kreslennya": ("/kreslennya", 52),
        "literaturne-chitannya": ("/literaturne-chitannya", 26),
        "lyudina-i-svit": ("/lyudina-i-svit", 38),
        "matematika": ("/matematika", 10),
        "mistectvo": ("/mistectvo", 30),
        "movi-nacionalnih-menshin": ("/movi-nacionalnih-menshin", 29),
        "muzichne-mistectvo": ("/muzichne-mistectvo", 11),
        "navchannya-gramoti": ("/navchannya-gramoti", 12),
        "nimecka-mova": ("/nimecka-mova", 35),
        "obrazotvorche-mistectvo": ("/obrazotvorche-mistectvo", 31),
        "osnovi-zdorovya": ("/osnovi-zdorovya", 13),
        "polska-mova": ("/polska-mova", 48),
        "pravoznavstvo": ("/pravoznavstvo", 33),
        "prirodnichi-nauki": ("/prirodnichi-nauki", 49),
        "prirodoznavstvo": ("/prirodoznavstvo", 27),
        "tehnologi": ("/tehnologi", 42),
        "trudove-navchannya": ("/trudove-navchannya", 32),
        "ukrainska-literatura": ("/ukrainska-literatura", 15),
        "ukrainska-mova": ("/ukrainska-mova", 14),
        "fizika": ("/fizika", 2),
        "fizichna-kultura": ("/fizichna-kultura", 17),
        "francuzka-mova": ("/francuzka-mova", 36),
        "himiya": ("/himiya", 16),
        "hudozhnya-kultura": ("/hudozhnya-kultura", 39),
        "ya-doslidzhuyu-svit": ("/ya-doslidzhuyu-svit", 28)
    }
    grade = {
        "1 клас": 1,
        "2 клас": 2,
        "3 клас": 3,
        "4 клас": 4,
        "5 клас": 5,
        "6 клас": 6,
        "7 клас": 7,
        "8 клас": 8,
        "9 клас": 9,
        "10 клас": 10,
        "11 клас": 11,
    }

    def __init__(self, interface=None, logs=None, cookies=None):
        super().__init__(interface=interface, logs=logs, cookies=cookies)
        self.naurok = Load_data(cookies=self.cookies, qt_logs=self.logs)

    def search(self, search_query=None, subject=None, grade=None, pagination=(1,11), proxy=None):
        a = self.naurok.search(
            q=search_query if search_query else "",
            subject=subject if subject else "",
            klass=grade if grade else "0",
            storinka=pagination,
            proxy=proxy,
        )
        self.res_list += a
        return a

    def search_by_url(self, urls, proxy=None):
        if not urls:
            raise NotUrlsError

        return self.naurok.search_by_url(
            url=urls,
            proxy=proxy,
        )

    def processing_data(self, urls=None, proxy=None):
        return self.naurok.processing_data(
            url=urls or self.res_list,
            proxy=proxy
        )

    def get_answer(self, urls=None, proxy=None):
        if not self.cookies:
            raise NotCookiesError

        gamecode = self.naurok.create_test(
            url=urls or self.res_list,
            proxy=proxy,
        )

        answer_url = self.naurok.test_pass(
            gamecode=gamecode,
            proxy=proxy,
        )

        return self.naurok.get_answer(
            url=answer_url,
            proxy=proxy,
        )

    #create_test
    def test_build(self, name, subject, grade, *questions):
        if not self.cookies:
            raise NotCookiesError

        test = CreateTest(
            name_test=name,
            klass=grade,
            subject=subject,
            qt_logs=self.logs,
            cookies=self.cookies
        )
        for item in questions:
            test.create_question(
                question=item["question"],
                answers=item["answers"]
            )
        return test.end_create()

if __name__ == '__main__':
    naurok = Main(cookies=json.load(open("data/cookies/naurok")))
    print(naurok.auto_complite("адольф хэмингуэй", 2624500))

