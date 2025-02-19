import aiohttp

from typing import Type
from threading import Thread

from fake_useragent import UserAgent


def async_session(cookies=None, headers=None):
	def wrappers(funk):
		async def wrapper(*agrs, **kwagrs):
			async with aiohttp.ClientSession(
					headers=headers or {"user-agent": UserAgent().random},
					timeout=aiohttp.ClientTimeout(15),
					cookies=cookies) as session:
				return await funk(session, *agrs, **kwagrs)
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
		Thread(target=funk, args=args, kwargs=kwargs, daemon=True).start()
	return wrapper


