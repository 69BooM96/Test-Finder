import requests
import asyncio
import aiohttp

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from modules.decorate import async_session


class Load_data:
    def __init__(self, cookies=None):
        self.cookies = {item["name"]: item["value"] for item in cookies} if cookies else None

    def search(self, subject="", klass=0, q="", storinka=(1,2), proxy=None, qt_logs=None) -> list[str]:
        async def async_search(session: aiohttp.ClientSession, storinka=1):
            async with session.get(f"https://naurok.com.ua/test{subject}/klas-{klass}?q={q}&storinka={storinka}", proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            if qt_logs: qt_logs.emit("info", f"Naurok", f" [{req.status}] [{str(req.url)}]")

            return ["https://naurok.com.ua" + obj.find("a").get("href") for obj in soup.find_all(class_="headline")]

        @async_session(self.cookies)
        async def run(session):
            task = [async_search(session, storinka=item) for item in range(*storinka)]
            return await asyncio.gather(*task)

        return list(set(item2 for item in asyncio.run(run()) for item2 in item))

    def search_by_url(self, url: list, proxy=None, qt_logs=None) -> list[dict]:
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

    def processing_data(self, url: list, proxy=None, qt_logs=None) -> list[dict]:
        """Получение вопросов с не пройденного теста"""
        async def async_processing_data(session: aiohttp.ClientSession, url):
            async with session.get(url, proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            if qt_logs: qt_logs.emit("info", f"Naurok", f" [{req.status}] [{str(req.url)}]")

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

    def create_test(self, url: list, proxy=None, qt_logs=None) -> list[str]:
        """создание теста"""
        async def async_get_test(session: aiohttp.ClientSession, url):
            async with session.get(url, proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            if qt_logs: qt_logs.emit("info", f"Naurok", f" [{req.status}] [{str(req.url)}]")

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

    def test_pass(self, gamecode: list, proxy=None, qt_logs=None) -> list[str]:
        """получение ответов с теста по геймкоду который возврощяет create_test"""
        async def async_test_pass(session: aiohttp.ClientSession, gamecode):
            async with session.get("https://naurok.com.ua/test/join", proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            if qt_logs: qt_logs.emit("info", f"Naurok", f" [{req.status}] [{str(req.url)}]")

            data = {
                "_csrf": soup.find(attrs={"name": "csrf-token"}).get("content"),
                "JoinForm[gamecode]": gamecode,
                "JoinForm[name]": "Test-Finder"
            }

            async with session.post("https://naurok.com.ua/test/join", data=data, proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            session_id = soup.find(class_="{{test.font}}").get("ng-init").split(",")[1]

            async with session.get(f"https://naurok.com.ua/api2/test/sessions/{session_id}", proxy=proxy) as req:
                session_res = await req.json()

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

    def get_answer(self, url: list, proxy=None, qt_logs=None) -> list[dict]:
        """получение полных ответов с конечной сылки которая возврощяется test_pass (Очень похожа на processing_data)"""
        async def async_get_answer(session: aiohttp.ClientSession, url):
            async with session.get(url, proxy=proxy) as req:
                soup = BeautifulSoup(await req.text(), "lxml")

            if qt_logs: qt_logs.emit("info", f"Naurok", f" [{req.status}] [{str(req.url)}]")

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


    def answers(self, url: list, proxy=None, qt_logs=None):
        create_data = self.create_test(url, proxy=proxy, qt_logs=qt_logs)
        pass_data = self.test_pass(create_data, proxy=proxy, qt_logs=qt_logs)
        return self.get_answer(pass_data, proxy=proxy, qt_logs=qt_logs)

class AutoComplite:
    def __init__(self, gamecode: str, name: str):
        self.session = requests.Session()
        self.session.headers.update({"user-agent": UserAgent().random})

        req = self.session.get("https://naurok.com.ua/test/join")
        soup = BeautifulSoup(req.text, "lxml")

        data = {
            "_csrf": soup.find(attrs={"name": "csrf-token"}).get("content"),
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

    def answer(self, queshion, text: list=None, img: list=None):
        q_id = []
        for item in queshion["answers"]:
            if text:
                for t in text:
                    if t == item["text"]:
                        q_id.append(item["id"])

            if img:
                for i in img:
                    if i == item["img"]:
                        q_id.append(item["id"])

        if q_id:
            data = {
                "answer": list(set(q_id)),
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

class Create_Test:
    def __init__(self, name_test: str, subject: int, klass: int, cookies: list[dict], qt_logs=None):
        self.session = requests.Session()
        self.session.cookies.update({i["name"]: i["value"] for i in cookies})
        self.session.headers.update({"user-agent": UserAgent().random})

        req = self.session.get("https://naurok.com.ua/test/create")
        soup = BeautifulSoup(req.text, "lxml")

        if qt_logs: qt_logs.emit("info", f"Naurok", f" [{req.status_code}] [{str(req.url)}]")

        data = {
            '_csrf': soup.find('input', attrs={'name': '_csrf'})["value"],
            'Document[name]': name_test,
            'Document[subject_id]': str(subject),
            'Document[grade_id]': str(klass)
        }

        req = self.session.post("https://naurok.com.ua/test/create", data=data, files={'Document[image]': ('', b'')})
        self.doc_id = req.url.split("/")[-1]
        self.csrf = soup.find('meta', {'name': 'csrf-token'})['content']

    def create_question(self, question: str, answers: dict[str, bool], qt_logs=None):
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
        if qt_logs: qt_logs.emit("info", f"Naurok", f" [{req.status_code}] [{str(req.url)}]")

    def end_create(self, qt_logs=None):
        req = self.session.put(f"https://naurok.com.ua/api/test/documents/{self.doc_id}")

        if qt_logs: qt_logs.emit("info", f"Naurok", f" [{req.status_code}] [{str(req.url)}]")

        return f"https://naurok.com.ua/test/{req.json()["slug"]}.html"


def data_info():
    list_object = [
                "/algebra", "/angliyska-mova", "/astronomiya", "/biologiya", "/vsesvitnya-istoriya", "/geografiya", "/geometriya",
                "/gromadyanska-osvita", "/ekologiya", "/ekonomika", "/etika", "/zarubizhna-literatura", "/zahist-vitchizni", "/informatika",
                "/inshi-inozemni-movi", "/ispanska-mova", "/istoriya-ukra-ni", "/kreslennya", "/literaturne-chitannya", "/lyudina-i-svit", "/matematika",
                "/mistectvo", "/movi-nacionalnih-menshin", "/muzichne-mistectvo", "/navchannya-gramoti", "/nimecka-mova", "/obrazotvorche-mistectvo",
                "/osnovi-zdorov-ya", "/polska-mova", "/pravoznavstvo", "/prirodnichi-nauki", "/prirodoznavstvo", "/tehnologi", "/trudove-navchannya",
                "/ukrainska-literatura", "/ukrainska-mova", "/fizika", "/fizichna-kultura", "/francuzka-mova", "/himiya", "/hudozhnya-kultura", "/ya-doslidzhuyu-svit"
                ]
    return {
            "search": {
                "subject": [list_object, False],
                "klass": [True, False],
                "q": [True, False],
                "storinka": [True, False],
                "proxy": [True, False],
                "cookie": [False, False]},
            "processing_data": {
                "url": ["True", False],
                "proxy": [True, False],
                "cookie": [False, False]},
            "answers": {
                "url": ["True", False],
                "proxy": [True, False],
                "cookie": [True, True]},
            "qt_logs": [True, False]
            }