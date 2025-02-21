class MainPlugin:
    subject = {}
    grade = {}
    def __init__(self, interface, logs=None, cookies=None):
        self.interface = interface
        self.logs = logs
        self.cookies = cookies
        self.res_list = []


    def search(self, search_query, subject, grade, pagination=(1, 11), proxy=None):
        raise NotMetodError("Метод плагина не определен")

    def search_by_url(self, urls, proxy=None):
        raise NotMetodError("Метод плагина не определен")

    def processing_data(self, urls=None, proxy=None):
        raise NotMetodError("Метод плагина не определен")

    def get_answer(self, urls=None, proxy=None):
        raise NotMetodError("Метод плагина не определен")

    def test_build(self, name, subject, grade, questions, proxy=None):
        raise NotMetodError("Метод плагина не определен")


class NotGradeError(AttributeError):
    def __init__(self, *args):
        super().__init__("Не указан атрибут метода \"Grade\"")

class NotSubjectError(AttributeError):
    def __init__(self, *args):
        super().__init__("Не указан атрибут метода \"Subject\"")

class NotUrlsError(AttributeError):
    def __init__(self, *args):
        super().__init__("Не указан атрибут метода \"Urls\"")


class MainAutoComplite:
    def __init__(self, code: str=None, name: str=None, cookies=None):
        if not code:    raise NotCodeError
        if not name:    raise NotUserNameError

    def var(self):
        raise NotMetodError

    def answer(self, queshion, index_answer: list):
        raise NotMetodError

    def end(self):
        raise NotMetodError


class NotUserNameError(AttributeError):
    def __init__(self, *args):
        super().__init__("Не указан атрибут метода \"UserName\"")

class NotCodeError(AttributeError):
    def __init__(self, *args):
        super().__init__("Не указан атрибут метода \"Code\"")


class Searcher:
    def __init__(self, interface, logs=None, cookies=None):
        self.interface = interface
        self.logs = logs
        self.cookies = cookies
        self.res_list = []

    def search(self, search_query, site, pagination=(1,11), proxy=None):
        raise NotMetodError






class NotCookiesError(AttributeError):
    def __init__(self, *args):
        super().__init__("Не указан атрибут метода \"Cookies\"")

class NotMetodError(NameError):
    def __init__(self, *args):
        super().__init__("Метод плагина не определен")
