import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from time import perf_counter


def async_session(funk):
	async def wrapper(*agrs, **kwagrs):
		try:
			async with aiohttp.ClientSession(headers={"user-agent": UserAgent().random}, timeout=aiohttp.ClientTimeout(15)) as session:
				return await funk(session, *agrs, **kwagrs)
		except BaseException as ex: return ex
	return wrapper

class Load_data:
	тебе ебало разбить тупой дебил