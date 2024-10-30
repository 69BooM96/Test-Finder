import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup

from modules.decorate import async_session

class Load_data:
	def search(self, subject, storinka=(1,2), proxy=None):
		@async_session(None)
		async def async_search(session: aiohttp.ClientSession, storinka):
			async with session.get(f"https://pomahach.com/cat{subject}/page/{storinka}/", proxy=proxy) as req:
				soup = BeautifulSoup(await req.text(), "lxml")

			return [obj.get("href") for obj in soup.find_all(class_="list-group-item")]
		
		async def run():
			task = [async_search(storinka=item) for item in range(*storinka)]
			return await asyncio.gather(*task)
		
		return sum(asyncio.run(run()), [])
	
	def processing_data(self, url: list, proxy=None):
		@async_session(None)
		async def async_processing_data(session: aiohttp.ClientSession, url):
			async with session.get(url, proxy=proxy) as req:
				soup = BeautifulSoup(await req.text(), "lxml")
				print(url)

			return {
				"platform": "pomahach",
				"type": "quiz" if soup.find(class_="option-marker quiz") else "multiquiz",
				"name_test": soup.find(class_="panel-body").text,

				"answers": [{
					"text": obj.text.strip(),
					"correctness": bool("list-group-item-success" in obj.get("class", []))
				} for obj in soup.find_all(class_="list-group")[1].find_all("li")]}
		
		
		async def run():
			task = [async_processing_data(url) for url in url if url[:30] == "https://pomahach.com/question/"]
			return await asyncio.gather(*task)

		return asyncio.run(run())

def data_info():
	list_object = [
		'/biologiya', '/geografiya', '/himiya', '/istoriya-ukrayini', '/pravoznavstvo', '/ekonomika', 
		'/pdr', '/algebra', '/gigiyena-ta-ekologiya', '/ukrayinska-mova-i-literatura', '/notarius', 
		'/bankivska-sistema', '/zagalna-ta-specialna-hirurgiya', '/viyskova-i-ekstremalna-medicina', '/dilova-ukrayinska-mova', 
		'/kulturologiya', '/angliyska-mova', '/agrohimiya', '/ispanska-mova', '/francuzka-mova', '/imunologiya', 
		'/menedzhment-i-administruvannya', '/pozhezhna-bezpeka', '/osnovi-virobnichoyi-sanitariyi', '/normuvannya-prirodnogo-ta-shtuchnogo-osvitlennya', 
		'/podannya-pershoyi-dolikarskoyi-dopomogi', '/osnovni-zakonodavchi-akti-pro-ohoronu-praci', '/organizaciyni-pitannya-ohoroni-praci', 
		'/ekonomika-praci-y-socialno-trudovi-vidnosini', '/informatika', '/prirodnichi-nauki', '/stomatologiya', '/abdominalna-hirurgiya', 
		'/anesteziologiya-reanimatologiya-intensivna-terapiya-v-hirurgiyi', '/nevidkladna-hirurgiya-v-urologiyi-ta-ginekologiyi', '/onkologiya', 
		'/opiki-i-vidmorozhennya', '/osnovi-travmatologiyi-i-neyrohirurgiyi', '/proktologiya', '/sercevo-sudinnoyi-hirurgiya', '/sudinna-hirurgiya', 
		'/infekciyni-zahvoryuvannya', '/akusherstvo-ta-ginekologiya', '/astronomiya', '/fizika', '/matematika', '/stolici-krayin', 
		'/rozvitok-geografichnih-znan-pro-zemlyu', '/alergologiya', '/anesteziologiya', '/mistectvo', '/sport', '/kosmetologiya', '/muzika', 
		'/istoriya-svitu', '/mifologiya', '/svitova-literatura', '/ekologiya', '/ekonomika-pidpriyemstva', 
		'/mashini-ta-obladnannya-dlya-pererobki-silskogospodarskoyi-produkciyi', '/tehnichniy-servis-v-agropromislovomu-kompleksi', 
		'/ekspluataciya-mashin-i-obladnannya', '/finansoviy-oblik', '/tehnichna-mehanika', '/mashini-i-obladnannya-dlya-tvarinnictva', 
		'/marketing', '/metrologiya-i-standartizaciya', '/zahist-vitchizni', '/oblik-i-audit', '/literaturne-chitannya', '/muzichne-mistectvo', 
		'/lyudina-i-svit', '/etika', '/fizkultura', '/administrativne-pravo', '/marketingova-cinova-politika', '/cinoutvorennya-brendiv', 
		'/derzhavne-regulyuvannya-procesu-cinoutvorennya-v-ukrayini', '/ocinyuvannya-pomilki-i-riziku-v-cinoutvorenni', '/cinoutvorennya-v-mizhnarodnomu-marketingu', 
		'/marketingova-strategiya-cinoutvorennya', '/osoblivosti-doslidzhennya-rinkovoyi-konyunkturi', '/roriguvannya-cini', 
		'/procedura-priynyattya-rishen-schodo-viznachennya-cini', '/metodichni-pidhodi-do-cinoutvorennya-v-sistemi-marketingu', '/faktori-marketingovogo-cinoutvorennya', 
		'/sistema-cin-ta-yih-klasifikaciya', '/cina-yak-instrument-marketingovoyi-cinovoyi-politiki', '/formuvannya-cinovoyi-politiki', '/vvedennya-v-cinoutvorennya', 
		'/logistika-u-rinkoviy-ekonomici', '/klasifikaciya-form-logistichnih-utvoren', '/harakteristika-osnovnih-elementiv-logistiki', 
		'/tehnologichni-procesi-ta-upravlinnya-materialnimi-potokami', '/faktori-formuvannya-logistichnih-sistem', 
		'/upravlinnya-materialnimi-potokami-v-logistichnih-sistemah', '/zagotivelna-logistika', '/sutnist-rozpodilchoyi-logistiki', '/vnutrishnovirobnicha-logistika', 
		'/logistika-skladuvannya', '/transportna-logistika', '/globalizaciya-logistichnih-procesiv', '/groshi-i-kredit', 
		'/finansova-politika-i-finansoviy-mehanizm', '/osnovni-principi-regulyaciyi-fiziologichnih-funkciy', '/gumoralna-regulyaciya-fiziologichnih-funkciy-organizmu', 
		'/biznes-planuvannya-zed-aviaciynogo-pidpriyemstva', '/fiziologiya-centralnoyi-nervovoyi-sistemi', '/fizichna-ta-koloyidna-himiya', '/epidemiologiya', 
		'/endoskopiya', '/normalna-ta-patologichna-anatomiya-topografichna-anatomiya-z-operativnoyu-hirurgiyeyu', '/gistologiya-embriologiya', '/sudova-medicina', 
		'/zarubizhna-literatura', '/medicina', '/biohimiya', '/dermatologiya', '/virusologiya', '/dityacha-hirurgiya', '/gigiyena-ta-ekologiya', 
		'/kliniko-laboratorna-funkcionalna-diagnostika', '/infekciyni-hvorobi-epidemiologiya', '/vnutrishnya-medicina', '/geometriya', '/medichna-genetika', 
		'/neyrohirurgiya', '/otolaringologiya', '/oftalmologiya', '/nevidkladna-dopomoga', '/litnya-praktika', '/onkologiya-radiologiya', '/pediatriya', 
		'/tovaroznavstvo', '/byudzhetna-sistema', '/dilovodstvo', '/kriminologiya', '/gerbologiya', '/ekonomichna-teoriya', 
		'/ekonomika-starodavnogo-svitu', '/ekonomika-antichnosti', '/ekonomika-serednovichchya', '/ekonomika-epohi-pervisnogo-nagromadzhennya-kapitalu', 
		'/ekonomika-v-epohu-vilnoyi-konkurenciyi', '/istoriya-ekonomiki', '/istoriya-mistectv', '/ukrayinska-kultura', '/makroekonomika', '/filosofiya', 
		'/legka-atletika', '/pedagogika-pochatkovoyi-osviti', '/biogeografiya', '/radiobiologiya', '/finansi', '/teoriya-i-metodika-plavannya', 
		'/fizichna-geografiya-materikiv-i-okeaniv', '/dokumentno-informaciyni-komunikaciyi', '/religiya', '/etika-i-estetika', 
		'/istoriya-ukrayinskoyi-literaturi', '/rekreaciyna-geografiya', '/fiziologiya-lyudini-i-tvarin', '/fizika-z-osnovami-biofiziki', 
		'/matematichna-statistika', '/regionalna-ekonomichna-i-socialna-geografiya-svitu', '/ekonomichna-i-socialna-geografiya-ukrayini', 
		'/silskogospodarske-virobnictvo', '/vikova-fiziologiya', '/podatkova-sistema', '/rinok-finansovih-poslug', '/arheologiya', 
		'/elektrichni-mashini-i-aparati', '/politologiya', '/psihologiya', '/analitichna-himiya', '/strahuvannya', '/literaturoznavstvo', 
		'/turizm', '/finansoviy-rinok', '/teoriya-rozmischennya-produktivnih-sil', '/upovnovazhena-osoba-z-publichnih-zakupivel']

	return {"search": {
				"subject": [list_object, True],
				"klass": [False, False],
				"q": [False, False],
				"storinka": [True, False],
				"proxy": [True, False],
				"cookie": [False, False]},
			"processing_data": {"url": ["list", False],
				"proxy": [True, False]}}

def main():
	pomahach = Load_data()
	listik = pomahach.search('/biologiya', storinka=(1,2))
	
	a = pomahach.processing_data(listik)
	for item in range(len(a)):
		with open(f"temp_data/json/index_{item}.json", "w", encoding="utf-8") as file:
			json.dump(a[item], file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
	main()