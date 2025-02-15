import requests

import os
import time
import json
import importlib
import traceback

from bs4 import BeautifulSoup
from .plugin_param import *


class PluginStart:
    def __init__(self, plName=None, qtLogs=None, qtProgress=None):
        self.plName = plName
        self.qtLogs = qtLogs
        self.qtProgress = qtProgress
        self.big_start_time = time.perf_counter()
        self.progress_pl = 0
        self.progress_index = 0
        self.info_pl = []

    def load_info(self, type_pl=None, **kwargs):
        if self.plName:
            self.plugins_list = [self.plName]
        else:
            self.plugins_list = [name for name in os.listdir("plugins")]

        self.progress_pl = 42 // len(self.plugins_list)
        self.progress_index = 0
        self.info_pl = []

        for pl_index, pl_name in enumerate(self.plugins_list):
            self.info_pl.append({"name": pl_name})
            self.progress_index += self.progress_pl
            if self.qtLogs: self.qtLogs.emit("INFO", f"Plugin", f" [{pl_index + 1}]/[{len(self.plugins_list)}] [{pl_name}] [start]")
            if self.qtProgress: self.qtProgress.emit(self.progress_index)

            try:
                with open(f"plugins/{pl_name}/metadata.json", "r", encoding="utf-8") as metadata:
                    mt_data = json.load(metadata)

                if mt_data['status'] != "works":
                    continue
                plugin = importlib.import_module(f"plugins.{pl_name}.{mt_data['file']}")

                if mt_data['type'] == "search":
                    if type_pl == "search":
                        try:
                            data_info = plugin.Main.subject
                            kwagrs_pl = {}

                            if data_info.get("subject") and data_info["subject"].get("opportunity") and kwargs.get("subject"):
                                kwagrs_pl["subject"] = kwargs["subject"]

                            if data_info.get("klass") and data_info["klass"].get("opportunity") and kwargs.get("klass"):
                                kwagrs_pl["klass"] = kwargs["klass"]

                            if data_info.get("q") and data_info["q"].get("opportunity") and kwargs.get("q"):
                                kwagrs_pl["q"] = kwargs["q"]

                            if data_info.get("storinka") and data_info["storinka"].get("opportunity") and kwargs.get("storinka"):
                                kwagrs_pl["storinka"] = kwargs["storinka"]

                            if data_info.get("proxy") and data_info["proxy"].get("opportunity") and kwargs.get("proxy"):
                                kwagrs_pl["proxy"] = kwargs["proxy"]

                            if data_info.get("cookie") and data_info["cookie"].get("opportunity") and kwargs.get("cookie"):
                                kwagrs_pl["cookie"] = kwargs["cookie"]

                            if (data_info.get("subject") and not data_info["subject"].get("required") and not kwargs["subject"] or
                                    data_info.get("klass") and not data_info["klass"].get("required") and not kwargs["klass"] or
                                    data_info.get("q") and not data_info["q"].get("required") and not kwargs["q"] or
                                    data_info.get("storinka") and not data_info["storinka"].get("required") and not kwargs["storinka"] or
                                    data_info.get("proxy") and not data_info["proxy"].get("required") and not kwargs["proxy"]):
                                self.info_pl[pl_index]["search"] = {"work": False, "cookie": False}
                            else:
                                self.info_pl[pl_index]["search"] = {"work": True, "cookie": (data_info.get("cookie") and data_info["cookie"].get("required"))}
                        except:
                            self.info_pl[pl_index]["search"] = {"work": False, "cookie": False}
                            traceback.print_exc()

                    if type_pl == "processing":
                        try:
                            data_info = plugin.Load_data.PROCESSING_DATA

                            kwagrs_pl = {}

                            if data_info.get("url") and data_info["url"].get("opportunity") and kwargs.get("url"):       kwagrs_pl["url"] = kwargs["url"]
                            if data_info.get("proxy") and data_info["proxy"].get("opportunity") and kwargs.get("proxy"):   kwagrs_pl["proxy"] = kwargs["proxy"]
                            if data_info.get("cookie") and data_info["cookie"].get("opportunity") and kwargs.get("cookie"): kwagrs_pl["cookie"] = kwargs["cookie"]

                            if (data_info.get("subject") and not data_info["url"].get("required") and not kwargs["url"] or
                                    data_info.get("proxy") and not data_info["proxy"].get("required") and not kwargs["proxy"]):
                                self.info_pl[pl_index]["processing"] = {"work": False, "cookie": False}
                            else:
                                self.info_pl[pl_index]["processing"] = {"work": True, "cookie": (data_info.get("cookie") and data_info["cookie"].get("required"))}
                        except:
                            self.info_pl[pl_index]["processing"] = {"work": False, "cookie": False}
                            traceback.print_exc()

                    if type_pl == "answers":
                        try:
                            data_info = plugin.Load_data.ANSWERS

                            kwagrs_pl = {}

                            if data_info.get("url") and data_info["url"].get("opportunity") and kwargs.get("url"):       kwagrs_pl["url"] = kwargs["url"]
                            if data_info.get("proxy") and data_info["proxy"].get("opportunity") and kwargs.get("proxy"):   kwagrs_pl["proxy"] = kwargs["proxy"]
                            if data_info.get("cookie") and data_info["cookie"].get("opportunity") and kwargs.get("cookie"): kwagrs_pl["cookie"] = kwargs["cookie"]

                            if (data_info.get("url") and data_info["url"].get("required") and not kwargs["url"] or
                                    data_info.get("cookie") and data_info["cookie"].get("required") and not kwargs["cookie"]):
                                self.info_pl[pl_index]["answers"] = {"work": False, "cookie": False}
                            else:
                                self.info_pl[pl_index]["answers"] = {"work": True, "cookie": (data_info.get("cookie") and data_info["cookie"].get("required"))}
                        except:
                            self.info_pl[pl_index]["answers"] = {"work": False, "cookie": False}
                            traceback.print_exc()

                    if type_pl == "qtLogs":
                        try:
                            data_info = plugin.Load_data.QT_LOGS

                            kwagrs_pl = {}

                            if data_info.get("opportunity") and kwargs.get("qtLogs"): kwagrs_pl["qtLogs"] = kwargs["qtLogs"]

                            if data_info.get("required") and kwargs["qtLogs"]:
                                self.info_pl[pl_index]["qtLogs"] = {"work": True, "cookie": (data_info.get("cookie") and data_info["cookie"].get("required"))}
                        except:
                            self.info_pl[pl_index]["qtLogs"] = {"work": False, "cookie": False}
                            traceback.print_exc()
            except:
                traceback.print_exc()

    def search_data(self, search_query, subject, grade, pagination=(1,11), proxy=None):
        qwer = self.load_info()

    def processing_data(self, index_session=None, list_urls=None, proxy=None):
        ...

    def answers_data(self, index_session=None, index_json=None, list_urls=None, proxy=None):
        ...

    def create_data(self):
        ...

    def wiki_data(self):
        try:
            req = requests.get("https://ru.wikipedia.org/wiki/Python")
            soup = BeautifulSoup(req.text, "lxml")
            b = [
                soup.find(class_="mw-page-title-main").text,
                soup.find(class_="mw-content-ltr mw-parser-output").find("p").text.strip().replace("\xa0", ""),
                "https:" + str(soup.find("img", class_="mw-file-element").get("src") if soup.find("img", class_="mw-file-element") else None)
            ]

            print(b)
        except BaseException as e:
            print(e)


if __name__ == "__main__":
     plugin = PluginStart().load_info(subject="/algebra", klass=8)
     plugin.search_data()