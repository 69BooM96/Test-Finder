import requests
import json

from bs4 import BeautifulSoup

from modules.plugin_param import *


class Load_data:
    def __init__(self, qt_logs, cookies=None):
        self.qt_logs = qt_logs

    def get_json(self, url, proxy=None):
        a = []
        for url in url:
            req = requests.get(f"https://app.wizer.me/learn/worksheet/{url.split("/")[-1]}", proxy=proxy)

            if self.qt_logs: self.qt_logs.emit("info", f"Naurok", f" [{req.status_code}] [{str(req.url)}]")

            a.append(req.json())
        return a

    def processing_data(self, data: dict) -> dict:
        for data in data:
            answers = []
            for item in data["worksheet"]["widgets"]:
                answers_dict = {}
                typy_q = item["name"]
                answers_dict["type"] = typy_q

                if typy_q == "Multiple Choice":
                    if sum(bool(j.get("checked")) for j in item["data"]["options"]) > 1:
                        answers_dict["type"] = "multiquiz"
                    else:
                        answers_dict["type"] = "quiz"

                    answers_dict["text"] = BeautifulSoup(item["data"]["title"], "lxml").text
                    answers_dict["value"] = [
                        {
                            "text": BeautifulSoup(i["text"], "lxml").text,
                            "img": i.get("imageUrl"),
                            "correctness": bool(i.get("checked"))
                        }
                    for i in item["data"]["options"]
                    ]

                elif typy_q == "Blanks":
                    answers_dict["value"] = [
                        {
                            "text": item["data"]["blankText"],
                            "img": None,
                            "correctness": None
                        }
                    ]

                elif typy_q == "Matching":
                    answers_dict["value"] = [
                        {
                            "text": BeautifulSoup(item["data"]["title"], "lxml").text,
                            "img": None,
                            "correctness": [
                                {
                                "target": {
                                    "text": i["target"]["value"],
                                    "img": None
                                    },
                                "match": {
                                    "text": i["match"]["value"],
                                    "img": None
                                    }
                                }
                            for i in item["data"]["pairs"]]
                        }
                    ]

                elif typy_q == "Sorting":
                    answers_dict["value"] = {
                        "text": BeautifulSoup(item["data"]["description"], "lxml").text,
                        "img": None,
                        "correctness": {
                            BeautifulSoup(i["header"]["text"], "lxml").text: [BeautifulSoup(i2["text"], "lxml").text for i2 in i["items"]]
                            for i in item["data"]["groups"]
                        }
                    }

                #хуйня не робочая баля курва япьярдоле
                elif typy_q == "Open Question":
                    answers_dict["value"] = {
                        "text": BeautifulSoup(item["data"]["description"], "lxml").text,
                        "img": None,
                    }

                elif typy_q == "Draw":
                    answers_dict["value"] = {
                        "text": BeautifulSoup(item["data"]["description"], "lxml").text,
                        "img": "https://app.wizer.me/images/draw/bg-pttrn.jpg",
                    }

                elif typy_q == "Text":
                    answers_dict["value"] = {
                        "text": BeautifulSoup(item["data"]["title"], "lxml").text,
                    }

                elif typy_q == "Video":
                    answers_dict["value"] = {
                        "text": BeautifulSoup(item["data"]["description"], "lxml").text,
                        "img": item["data"]["video"]["thumbnails"]["standard"],
                        "url": item["data"]["video"]["url"]
                    }

                elif typy_q == "Link":
                    answers_dict["value"] = {
                        "text": BeautifulSoup(item["data"]["teacher_description"], "lxml").text,
                        "url": item["data"]["url"]
                    }


                answers.append(answers_dict)


            yield {
                "platform": "appwizer",
                "type_data": "test",
                "url": None,
                "name_test": None,
                "object": None,
                "klass": None,
                "answers": answers
            }


class Main(MainPlugin):
    def __init__(self, interface=None, logs=None, cookies=None):
        super().__init__(interface=interface, logs=logs, cookies=cookies)
        self.appwizer = Load_data(qt_logs=self.logs)

    def get_answer(self, urls=None, proxy=None):
        if not urls:
            raise NotUrlsError

        a = self.appwizer.get_json(urls, proxy=proxy)

        b = list(self.appwizer.processing_data(a))
        self.res_list += b

        return b

if __name__ == '__main__':
    a = Main()
    print(a.get_answer(["https://app.wizer.me/learn/FA4E49"]))