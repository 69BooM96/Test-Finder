import aiohttp
import json

from typing import Type, Callable, Optional, Dict, Any
from threading import Thread

from fake_useragent import UserAgent


async def _on_request_start(session, trace_config_ctx, params, log_func):
    request_data = {
        "event": "request_started",
        "method": params.method,
        "url": str(params.url),
        "headers": dict(params.headers),
        "cookies": {key: value.value for key, value in session.cookie_jar.filter_cookies(params.url).items()}
    }
    if log_func: log_func(json.dumps(request_data, indent=4, ensure_ascii=False))

async def _on_request_end(session, trace_config_ctx, params, log_func):
    response_data = {
        "event": "request_ended",
        "url": str(params.url),
        "status": params.response.status,
        "headers": dict(params.response.headers),
        "cookies": {key: value.value for key, value in session.cookie_jar.filter_cookies(params.url).items()},
        "body": await params.response.text()  # Читаем тело ответа
    }
    if log_func: log_func(json.dumps(response_data, indent=4, ensure_ascii=False))

def async_session(cookies: Optional[Dict[str, str]] = None, headers: Optional[Dict[str, str]] = None, log_func=print):
    def wrappers(funk: Callable):
        async def wrapper(*args, **kwargs):
            trace_config = aiohttp.TraceConfig()
            trace_config.on_request_start.append(lambda *args: _on_request_start(*args, log_func=log_func))
            trace_config.on_request_end.append(lambda *args: _on_request_end(*args, log_func=log_func))

            async with aiohttp.ClientSession(
                headers=headers or {"user-agent": UserAgent().random},
                timeout=aiohttp.ClientTimeout(15),
                cookies=cookies,
                trace_configs=[trace_config]
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


