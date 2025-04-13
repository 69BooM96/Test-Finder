import aiohttp
from http.cookies import SimpleCookie
from typing import Type, Callable
from threading import Thread
from aiohttp import ClientRequest, ClientResponse
from fake_useragent import UserAgent

class _LoggingRequest(ClientRequest):
    def __init__(self, *args, log_funk=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_funk = log_funk

    async def send(self, conn):
        cookies = {}
        if self.headers.get("Cookie"):
            cookie = SimpleCookie()
            cookie.load(self.headers["Cookie"])
            cookies = {k: v.value for k, v in cookie.items()}
        if self.log_funk: self.log_funk(
            {
                "event": "request_started",
                "method": self.method,
                "url": str(self.url),
                "headers": dict(self.headers),
                "cookies": cookies
            }
        )

        return await super().send(conn)

class _LoggingResponse(ClientResponse):
    def __init__(self, *args, log_funk=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_funk = log_funk

    async def start(self, connection):
        await super().start(connection)

        body = None
        res_type = self.headers.get("Content-Type", "").lower()

        if "json" in res_type:
            body = await self.json()
        elif "text" in res_type:
            body = await self.text()
        elif "image" in res_type:
            body = self.read()
        else:
            body = await self.text()

        cookies = {}
        if self.headers.get("Cookie"):
            cookie = SimpleCookie()
            cookie.load(self.headers["Cookie"])
            cookies = {k: v.value for k, v in cookie.items()}

        if self.log_funk: self.log_funk({
            "event": "request_ended",
            "url": str(self.url),
            "status": self.status,
            "headers": dict(self.headers),
            "cookies": cookies,
            "body": body
        })


def async_session(cookies=None, headers=None, log_func=print):
    def wrappers(funk: Callable):
        async def wrapper(*args, **kwargs):
            async with aiohttp.ClientSession(
                headers=headers or {"user-agent": UserAgent().random},
                timeout=aiohttp.ClientTimeout(15),
                cookies=cookies,
                request_class=lambda *args, **kwargs: _LoggingRequest(*args, log_funk=None, **kwargs),
                response_class=lambda *args, **kwargs: _LoggingResponse(*args, log_funk=None, **kwargs),
            ) as session:
                return await funk(session, *args, **kwargs)

        return wrapper

    return wrappers

def try_except(exp: Type[BaseException], funk=(lambda ex: print(ex))):
    def wrappers(fun):
        def wrapper(*agrs, **kwagrs):
            try:
                return fun(*agrs, **kwagrs)
            except exp as ex:
                funk(ex)
        return wrapper
    return wrappers

def thread(funk):
    def wrapper(*args, **kwargs):
        Thread(target=funk, args=args, kwargs=kwargs).start()
    return wrapper

