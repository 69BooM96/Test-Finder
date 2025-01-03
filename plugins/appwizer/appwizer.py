import requests
import json

from bs4 import BeautifulSoup

def pprint(a):
    print(json.dumps(a, indent=4, ensure_ascii=False))

class Load_data:
    def __init__(self, cookies=None):
        self.cookies = {item["name"]: item["value"] for item in cookies} if cookies else None

    def get_json(self, url) -> dict:
        req = requests.get(f"https://app.wizer.me/learn/worksheet/{url.split("/")[-1]}")
        return req.json()
    
    def processing_data(self, data: dict) -> dict:
        answers = []
        for item in data["worksheet"]["widgets"]:
            answers_dict = {}
            typy_q = item["name"]
            if typy_q not in ["Reflection", "Discussion", "Link", "Video", "Text", "Draw", "Open Question", "Image"]:
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
                    answers_dict["type"] = "Blanks"
                    answers_dict["value"] = [
                        {
                            "text": item["data"]["blankText"],
                            "img": None,
                            "correctness": None
                        }
                    ]
                
                elif typy_q == "Matching":
                    answers_dict["type"] = "Matching"
                    answers_dict["value"] = [
                        {
                            "text": BeautifulSoup(item["data"]["title"], "lxml").text,
                            "img": None,
                            "correctness": [{
                                "target": {
                                    "text": i["target"]["value"],
                                    "img": None},
                                "match": {
                                    "text": i["match"]["value"],
                                    "img": None
                                    }
                                }
                            for i in item["data"]["pairs"]]
                        }
                    ]
                
                elif typy_q == "Sorting":
                    answers_dict["type"] = "Sorting"
                    
                    answers_dict["value"] = {
                        "text": BeautifulSoup(item["data"]["description"], "lxml").text,
                        "correctness": {
                            i["header"]["text"]: [i2["text"] for i2 in i["items"]]
                            for i in item["groups"]
                        }
                    }

            pprint(answers_dict)
                
                

        return {
            "platform": "appwizer",
            "type_data": "test",
            "url": None,
            "name_test": None,
            "object": None,
            "klass": None,
            "answers": answers
        }
        


if __name__ == "__main__":
    qwe = Load_data()
    a = qwe.get_json("https://app.wizer.me/preview-legacy/F5LX2P")
    qwe.processing_data(a)
