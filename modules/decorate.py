import aiohttp
from fake_useragent import UserAgent

def async_session(cookies):
	def wrappers(funk):
		async def wrapper(*agrs, **kwagrs):
			try:
				async with aiohttp.ClientSession(headers={"user-agent": UserAgent().random}, timeout=aiohttp.ClientTimeout(15), cookies=cookies) as session:
					return await funk(session, *agrs, **kwagrs)
			except BaseException as ex: return ex 
		return wrapper
	return wrappers


def try_except(exp: BaseException, funk=(lambda ex: print(ex))):
	def wrappers(fun):
		def wrapper(*agrs, **kwagrs):
			try:
				return fun(*agrs, **kwagrs)
			except exp as ex:
				funk(ex)

		return wrapper
	return wrappers



