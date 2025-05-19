import json
from fuzzywuzzy import fuzz

class Scan:
	def __init__(self, multi=None, text=None, data=None):
		self.data = data
		self.text = text
		self.multi = multi

	def tests(self, name=None, answers=None, value=None):
		temp_json = []
		score = {
			"index": None,
			"text": None,
			"score": 0
		}

		for index, item in enumerate(self.data):
			try:
				if item["name_test"] and name:
					fzz_0 = fuzz.WRatio(item["name_test"], self.text)
					if fzz_0 > score["score"]:
						score["index"] = [-1, -1]
						score["text"] = item["name_test"]
						score["score"] = fzz_0

					for index_answers, item_answers in enumerate(item["answers"]):
						if item_answers["text"] and answers:
							fzz_1 = fuzz.WRatio(item_answers["text"], self.text)
							if fzz_1 > score["score"]:
								score["index"] = [index_answers, -1]
								score["text"] = item_answers["text"]
								score["score"] = fzz_1

							for index_value, item_value in enumerate(item_answers["value"]):
								if item_value["text"] and value:
									fzz_2 = fuzz.WRatio(item_value["text"], self.text)
									if fzz_2 > score["score"]:
										score["index"] = [index_answers, index_value]
										score["text"] = item_value["text"]
										score["score"] = fzz_2
			except Exception as e:
				if self.multi: self.multi.put({"type": "logs", "level": "ERROR", "source": "scan", "data": f" [{index}] | [{e}]"})
			item["score"] = score
			temp_json.append(item)

		if self.multi: self.multi.put({"type": "logs", "level": "info", "source": "scan", "data": f""})
		if self.multi: self.multi.put({"type": "scan", "data": temp_json})
		else: return temp_json
