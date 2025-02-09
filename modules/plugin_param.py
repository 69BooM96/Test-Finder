class MainPlugin:
    def search(self, search_query, subject, grade, pagination=(1, 11), proxy=None):
        raise NotMetodError("Метод плагина не определен")

    def search_by_url(self, urls, proxy=None):
        raise NotMetodError("Метод плагина не определен")

    def processing_data(self, urls=None, proxy=None):
        raise NotMetodError("Метод плагина не определен")

    def get_answer(self, urls=None, proxy=None):
        raise NotMetodError("Метод плагина не определен")

    def test_build(self, name, subject, grade, *questions):
        raise NotMetodError("Метод плагина не определен")

    def auto_complite(self, user_name, code, point, time):
        raise NotMetodError("Метод плагина не определен")

class NotCookiesError(AttributeError):
    ...

class NotGradeError(AttributeError):
    ...

class NotSubjectError(AttributeError):
    ...

class NotMetodError(NameError):
    ...
