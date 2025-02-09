import json
import asyncio
import aiohttp

from bs4 import BeautifulSoup

from modules.decorate import async_session
from modules.plugin_param import *


class Load_data:
	def __init__(self, qt_logs=None):
		self.qt_logs = qt_logs

	def search(self, subject, storinka=(1,2), proxy=None):
		async def async_search(session: aiohttp.ClientSession, storinka):
			async with session.get(f"https://pomahach.com/cat{subject}/page/{storinka}/", proxy=proxy) as req:
				soup = BeautifulSoup(await req.text(), "lxml")

				if self.qt_logs: self.qt_logs.emit("info", f"Pomahach", f" [{req.status}] [https://pomahach.com/cat{subject}/page/{storinka}/]")

			return [obj.get("href") for obj in soup.find_all(class_="list-group-item")]

		@async_session(None)
		async def run(session):
			task = [async_search(session, storinka=item) for item in range(*storinka)]
			return await asyncio.gather(*task)
		
		return list(set(item2 for item in asyncio.run(run()) for item2 in item))
	
	def processing_data(self, url: list, proxy=None):
		async def async_processing_data(session: aiohttp.ClientSession, url):
			async with session.get(url, proxy=proxy) as req:
				soup = BeautifulSoup(await req.text(), "lxml")

				if self.qt_logs: self.qt_logs.emit("info", f"Pomahach", f" [{req.status}] [{url}]")

			return {
				"platform": "pomahach",
				"type_data": "test",
				"url": str(req.url),
				"name_test": soup.title.string,
				"object": soup.find_all("meta")[2].get("content").split(".")[0],
				"klass": None,
				"answers": [{
					"type": "quiz" if soup.find(class_="option-marker quiz") else "multiquiz",
					"text": soup.find(class_="panel-body").text,
					"img": None,
					"value": [{
						"text": obj.text.strip(),
						"img": None,
						"correctness": bool("list-group-item-success" in obj.get("class", []))
					} for obj in soup.find_all(class_="list-group")[1].find_all("li")]
				}]}

		@async_session(None)
		async def run(session):
			task = [async_processing_data(session, url) for url in url if url[:30] == "https://pomahach.com/question/"]
			return await asyncio.gather(*task)

		return asyncio.run(run())

class Main(MainPlugin):
	subject = {
		"biologiya": ("/cat/biologiya/", 0),
		"geografiya": ("/cat/geografiya/", 0),
		"himiya": ("/cat/himiya/", 0),
		"istoriya-ukrayini": ("/cat/istoriya-ukrayini/", 0),
		"pravoznavstvo": ("/cat/pravoznavstvo/", 0),
		"ekonomika": ("/cat/ekonomika/", 0),
		"pdr": ("/cat/pdr/", 0),
		"algebra": ("/cat/algebra/", 0),
		"gigiyena-ta-ekologiya": ("/cat/gigiyena-ta-ekologiya/", 0),
		"ukrayinska-mova-i-literatura": ("/cat/ukrayinska-mova-i-literatura/", 0),
		"notarius": ("/cat/notarius/", 0),
		"bankivska-sistema": ("/cat/bankivska-sistema/", 0),
		"zagalna-ta-specialna-hirurgiya": ("/cat/zagalna-ta-specialna-hirurgiya/", 0),
		"viyskova-i-ekstremalna-medicina": ("/cat/viyskova-i-ekstremalna-medicina/", 0),
		"dilova-ukrayinska-mova": ("/cat/dilova-ukrayinska-mova/", 0),
		"kulturologiya": ("/cat/kulturologiya/", 0),
		"angliyska-mova": ("/cat/angliyska-mova/", 0),
		"agrohimiya": ("/cat/agrohimiya/", 0),
		"ispanska-mova": ("/cat/ispanska-mova/", 0),
		"francuzka-mova": ("/cat/francuzka-mova/", 0),
		"imunologiya": ("/cat/imunologiya/", 0),
		"menedzhment-i-administruvannya": ("/cat/menedzhment-i-administruvannya/", 0),
		"pozhezhna-bezpeka": ("/cat/pozhezhna-bezpeka/", 0),
		"osnovi-virobnichoyi-sanitariyi": ("/cat/osnovi-virobnichoyi-sanitariyi/", 0),
		"normuvannya-prirodnogo-ta-shtuchnogo-osvitlennya": ("/cat/normuvannya-prirodnogo-ta-shtuchnogo-osvitlennya/", 0),
		"podannya-pershoyi-dolikarskoyi-dopomogi": ("/cat/podannya-pershoyi-dolikarskoyi-dopomogi/", 0),
		"osnovni-zakonodavchi-akti-pro-ohoronu-praci": ("/cat/osnovni-zakonodavchi-akti-pro-ohoronu-praci/", 0),
		"organizaciyni-pitannya-ohoroni-praci": ("/cat/organizaciyni-pitannya-ohoroni-praci/", 0),
		"ekonomika-praci-y-socialno-trudovi-vidnosini": ("/cat/ekonomika-praci-y-socialno-trudovi-vidnosini/", 0),
		"informatika": ("/cat/informatika/", 0),
		"prirodnichi-nauki": ("/cat/prirodnichi-nauki/", 0),
		"stomatologiya": ("/cat/stomatologiya/", 0),
		"abdominalna-hirurgiya": ("/cat/abdominalna-hirurgiya/", 0),
		"anesteziologiya-reanimatologiya-intensivna-terapiya-v-hirurgiyi": ("/cat/anesteziologiya-reanimatologiya-intensivna-terapiya-v-hirurgiyi/", 0),
		"nevidkladna-hirurgiya-v-urologiyi-ta-ginekologiyi": ("/cat/nevidkladna-hirurgiya-v-urologiyi-ta-ginekologiyi/", 0),
		"onkologiya": ("/cat/onkologiya/", 0),
		"opiki-i-vidmorozhennya": ("/cat/opiki-i-vidmorozhennya/", 0),
		"osnovi-travmatologiyi-i-neyrohirurgiyi": ("/cat/osnovi-travmatologiyi-i-neyrohirurgiyi/", 0),
		"proktologiya": ("/cat/proktologiya/", 0),
		"sercevo-sudinnoyi-hirurgiya": ("/cat/sercevo-sudinnoyi-hirurgiya/", 0),
		"sudinna-hirurgiya": ("/cat/sudinna-hirurgiya/", 0),
		"infekciyni-zahvoryuvannya": ("/cat/infekciyni-zahvoryuvannya/", 0),
		"akusherstvo-ta-ginekologiya": ("/cat/akusherstvo-ta-ginekologiya/", 0),
		"astronomiya": ("/cat/astronomiya/", 0),
		"fizika": ("/cat/fizika/", 0),
		"matematika": ("/cat/matematika/", 0),
		"stolici-krayin": ("/cat/stolici-krayin/", 0),
		"rozvitok-geografichnih-znan-pro-zemlyu": ("/cat/rozvitok-geografichnih-znan-pro-zemlyu/", 0),
		"alergologiya": ("/cat/alergologiya/", 0),
		"anesteziologiya": ("/cat/anesteziologiya/", 0),
		"mistectvo": ("/cat/mistectvo/", 0),
		"sport": ("/cat/sport/", 0),
		"kosmetologiya": ("/cat/kosmetologiya/", 0),
		"muzika": ("/cat/muzika/", 0),
		"istoriya-svitu": ("/cat/istoriya-svitu/", 0),
		"mifologiya": ("/cat/mifologiya/", 0),
		"svitova-literatura": ("/cat/svitova-literatura/", 0),
		"ekologiya": ("/cat/ekologiya/", 0),
		"ekonomika-pidpriyemstva": ("/cat/ekonomika-pidpriyemstva/", 0),
		"mashini-ta-obladnannya-dlya-pererobki-silskogospodarskoyi-produkciyi": ("/cat/mashini-ta-obladnannya-dlya-pererobki-silskogospodarskoyi-produkciyi/", 0),
		"tehnichniy-servis-v-agropromislovomu-kompleksi": ("/cat/tehnichniy-servis-v-agropromislovomu-kompleksi/", 0),
		"ekspluataciya-mashin-i-obladnannya": ("/cat/ekspluataciya-mashin-i-obladnannya/", 0),
		"finansoviy-oblik": ("/cat/finansoviy-oblik/", 0),
		"tehnichna-mehanika": ("/cat/tehnichna-mehanika/", 0),
		"mashini-i-obladnannya-dlya-tvarinnictva": ("/cat/mashini-i-obladnannya-dlya-tvarinnictva/", 0),
		"marketing": ("/cat/marketing/", 0),
		"metrologiya-i-standartizaciya": ("/cat/metrologiya-i-standartizaciya/", 0),
		"zahist-vitchizni": ("/cat/zahist-vitchizni/", 0),
		"oblik-i-audit": ("/cat/oblik-i-audit/", 0),
		"literaturne-chitannya": ("/cat/literaturne-chitannya/", 0),
		"muzichne-mistectvo": ("/cat/muzichne-mistectvo/", 0),
		"lyudina-i-svit": ("/cat/lyudina-i-svit/", 0),
		"etika": ("/cat/etika/", 0),
		"fizkultura": ("/cat/fizkultura/", 0),
		"administrativne-pravo": ("/cat/administrativne-pravo/", 0),
		"marketingova-cinova-politika": ("/cat/marketingova-cinova-politika/", 0),
		"cinoutvorennya-brendiv": ("/cat/cinoutvorennya-brendiv/", 0),
		"derzhavne-regulyuvannya-procesu-cinoutvorennya-v-ukrayini": ("/cat/derzhavne-regulyuvannya-procesu-cinoutvorennya-v-ukrayini/", 0),
		"ocinyuvannya-pomilki-i-riziku-v-cinoutvorenni": ("/cat/ocinyuvannya-pomilki-i-riziku-v-cinoutvorenni/", 0),
		"cinoutvorennya-v-mizhnarodnomu-marketingu": ("/cat/cinoutvorennya-v-mizhnarodnomu-marketingu/", 0),
		"marketingova-strategiya-cinoutvorennya": ("/cat/marketingova-strategiya-cinoutvorennya/", 0),
		"osoblivosti-doslidzhennya-rinkovoyi-konyunkturi": ("/cat/osoblivosti-doslidzhennya-rinkovoyi-konyunkturi/", 0),
		"roriguvannya-cini": ("/cat/roriguvannya-cini/", 0),
		"procedura-priynyattya-rishen-schodo-viznachennya-cini": ("/cat/procedura-priynyattya-rishen-schodo-viznachennya-cini/", 0),
		"metodichni-pidhodi-do-cinoutvorennya-v-sistemi-marketingu": ("/cat/metodichni-pidhodi-do-cinoutvorennya-v-sistemi-marketingu/", 0),
		"faktori-marketingovogo-cinoutvorennya": ("/cat/faktori-marketingovogo-cinoutvorennya/", 0),
		"sistema-cin-ta-yih-klasifikaciya": ("/cat/sistema-cin-ta-yih-klasifikaciya/", 0),
		"cina-yak-instrument-marketingovoyi-cinovoyi-politiki": ("/cat/cina-yak-instrument-marketingovoyi-cinovoyi-politiki/", 0),
		"formuvannya-cinovoyi-politiki": ("/cat/formuvannya-cinovoyi-politiki/", 0),
		"vvedennya-v-cinoutvorennya": ("/cat/vvedennya-v-cinoutvorennya/", 0),
		"logistika-u-rinkoviy-ekonomici": ("/cat/logistika-u-rinkoviy-ekonomici/", 0),
		"klasifikaciya-form-logistichnih-utvoren": ("/cat/klasifikaciya-form-logistichnih-utvoren/", 0),
		"harakteristika-osnovnih-elementiv-logistiki": ("/cat/harakteristika-osnovnih-elementiv-logistiki/", 0),
		"tehnologichni-procesi-ta-upravlinnya-materialnimi-potokami": ("/cat/tehnologichni-procesi-ta-upravlinnya-materialnimi-potokami/", 0),
		"faktori-formuvannya-logistichnih-sistem": ("/cat/faktori-formuvannya-logistichnih-sistem/", 0),
		"upravlinnya-materialnimi-potokami-v-logistichnih-sistemah": ("/cat/upravlinnya-materialnimi-potokami-v-logistichnih-sistemah/", 0),
		"zagotivelna-logistika": ("/cat/zagotivelna-logistika/", 0),
		"sutnist-rozpodilchoyi-logistiki": ("/cat/sutnist-rozpodilchoyi-logistiki/", 0),
		"vnutrishnovirobnicha-logistika": ("/cat/vnutrishnovirobnicha-logistika/", 0),
		"logistika-skladuvannya": ("/cat/logistika-skladuvannya/", 0),
		"transportna-logistika": ("/cat/transportna-logistika/", 0),
		"globalizaciya-logistichnih-procesiv": ("/cat/globalizaciya-logistichnih-procesiv/", 0),
		"groshi-i-kredit": ("/cat/groshi-i-kredit/", 0),
		"finansova-politika-i-finansoviy-mehanizm": ("/cat/finansova-politika-i-finansoviy-mehanizm/", 0),
		"osnovni-principi-regulyaciyi-fiziologichnih-funkciy": ("/cat/osnovni-principi-regulyaciyi-fiziologichnih-funkciy/", 0),
		"gumoralna-regulyaciya-fiziologichnih-funkciy-organizmu": ("/cat/gumoralna-regulyaciya-fiziologichnih-funkciy-organizmu/", 0),
		"biznes-planuvannya-zed-aviaciynogo-pidpriyemstva": ("/cat/biznes-planuvannya-zed-aviaciynogo-pidpriyemstva/", 0),
		"fiziologiya-centralnoyi-nervovoyi-sistemi": ("/cat/fiziologiya-centralnoyi-nervovoyi-sistemi/", 0),
		"fizichna-ta-koloyidna-himiya": ("/cat/fizichna-ta-koloyidna-himiya/", 0),
		"epidemiologiya": ("/cat/epidemiologiya/", 0),
		"endoskopiya": ("/cat/endoskopiya/", 0),
		"normalna-ta-patologichna-anatomiya-topografichna-anatomiya-z-operativnoyu-hirurgiyeyu": ("/cat/normalna-ta-patologichna-anatomiya-topografichna-anatomiya-z-operativnoyu-hirurgiyeyu/", 0),
		"gistologiya-embriologiya": ("/cat/gistologiya-embriologiya/", 0),
		"sudova-medicina": ("/cat/sudova-medicina/", 0),
		"zarubizhna-literatura": ("/cat/zarubizhna-literatura/", 0),
		"medicina": ("/cat/medicina/", 0),
		"biohimiya": ("/cat/biohimiya/", 0),
		"dermatologiya": ("/cat/dermatologiya/", 0),
		"virusologiya": ("/cat/virusologiya/", 0),
		"dityacha-hirurgiya": ("/cat/dityacha-hirurgiya/", 0),
		"kliniko-laboratorna-funkcionalna-diagnostika": ("/cat/kliniko-laboratorna-funkcionalna-diagnostika/", 0),
		"infekciyni-hvorobi-epidemiologiya": ("/cat/infekciyni-hvorobi-epidemiologiya/", 0),
		"vnutrishnya-medicina": ("/cat/vnutrishnya-medicina/", 0),
		"geometriya": ("/cat/geometriya/", 0),
		"medichna-genetika": ("/cat/medichna-genetika/", 0),
		"neyrohirurgiya": ("/cat/neyrohirurgiya/", 0),
		"otolaringologiya": ("/cat/otolaringologiya/", 0),
		"oftalmologiya": ("/cat/oftalmologiya/", 0),
		"nevidkladna-dopomoga": ("/cat/nevidkladna-dopomoga/", 0),
		"litnya-praktika": ("/cat/litnya-praktika/", 0),
		"onkologiya-radiologiya": ("/cat/onkologiya-radiologiya/", 0),
		"pediatriya": ("/cat/pediatriya/", 0),
		"tovaroznavstvo": ("/cat/tovaroznavstvo/", 0),
		"byudzhetna-sistema": ("/cat/byudzhetna-sistema/", 0),
		"dilovodstvo": ("/cat/dilovodstvo/", 0),
		"kriminologiya": ("/cat/kriminologiya/", 0),
		"gerbologiya": ("/cat/gerbologiya/", 0),
		"ekonomichna-teoriya": ("/cat/ekonomichna-teoriya/", 0),
		"ekonomika-starodavnogo-svitu": ("/cat/ekonomika-starodavnogo-svitu/", 0),
		"ekonomika-antichnosti": ("/cat/ekonomika-antichnosti/", 0),
		"ekonomika-serednovichchya": ("/cat/ekonomika-serednovichchya/", 0),
		"ekonomika-epohi-pervisnogo-nagromadzhennya-kapitalu": ("/cat/ekonomika-epohi-pervisnogo-nagromadzhennya-kapitalu/", 0),
		"ekonomika-v-epohu-vilnoyi-konkurenciyi": ("/cat/ekonomika-v-epohu-vilnoyi-konkurenciyi/", 0),
		"istoriya-ekonomiki": ("/cat/istoriya-ekonomiki/", 0),
		"istoriya-mistectv": ("/cat/istoriya-mistectv/", 0),
		"ukrayinska-kultura": ("/cat/ukrayinska-kultura/", 0),
		"makroekonomika": ("/cat/makroekonomika/", 0),
		"filosofiya": ("/cat/filosofiya/", 0),
		"legka-atletika": ("/cat/legka-atletika/", 0),
		"pedagogika-pochatkovoyi-osviti": ("/cat/pedagogika-pochatkovoyi-osviti/", 0),
		"biogeografiya": ("/cat/biogeografiya/", 0),
		"radiobiologiya": ("/cat/radiobiologiya/", 0),
		"finansi": ("/cat/finansi/", 0),
		"teoriya-i-metodika-plavannya": ("/cat/teoriya-i-metodika-plavannya/", 0),
		"fizichna-geografiya-materikiv-i-okeaniv": ("/cat/fizichna-geografiya-materikiv-i-okeaniv/", 0),
		"dokumentno-informaciyni-komunikaciyi": ("/cat/dokumentno-informaciyni-komunikaciyi/", 0),
		"religiya": ("/cat/religiya/", 0),
		"etika-i-estetika": ("/cat/etika-i-estetika/", 0),
		"istoriya-ukrayinskoyi-literaturi": ("/cat/istoriya-ukrayinskoyi-literaturi/", 0),
		"rekreaciyna-geografiya": ("/cat/rekreaciyna-geografiya/", 0),
		"fiziologiya-lyudini-i-tvarin": ("/cat/fiziologiya-lyudini-i-tvarin/", 0),
		"fizika-z-osnovami-biofiziki": ("/cat/fizika-z-osnovami-biofiziki/", 0),
		"matematichna-statistika": ("/cat/matematichna-statistika/", 0),
		"regionalna-ekonomichna-i-socialna-geografiya-svitu": ("/cat/regionalna-ekonomichna-i-socialna-geografiya-svitu/", 0),
		"ekonomichna-i-socialna-geografiya-ukrayini": ("/cat/ekonomichna-i-socialna-geografiya-ukrayini/", 0),
		"silskogospodarske-virobnictvo": ("/cat/silskogospodarske-virobnictvo/", 0),
		"vikova-fiziologiya": ("/cat/vikova-fiziologiya/", 0),
		"podatkova-sistema": ("/cat/podatkova-sistema/", 0),
		"rinok-finansovih-poslug": ("/cat/rinok-finansovih-poslug/", 0),
		"arheologiya": ("/cat/arheologiya/", 0),
		"elektrichni-mashini-i-aparati": ("/cat/elektrichni-mashini-i-aparati/", 0),
		"politologiya": ("/cat/politologiya/", 0),
		"psihologiya": ("/cat/psihologiya/", 0),
		"analitichna-himiya": ("/cat/analitichna-himiya/", 0),
		"strahuvannya": ("/cat/strahuvannya/", 0),
		"literaturoznavstvo": ("/cat/literaturoznavstvo/", 0),
		"turizm": ("/cat/turizm/", 0),
		"finansoviy-rinok": ("/cat/finansoviy-rinok/", 0),
		"teoriya-rozmischennya-produktivnih-sil": ("/cat/teoriya-rozmischennya-produktivnih-sil/", 0),
		"upovnovazhena-osoba-z-publichnih-zakupivel": ("/cat/upovnovazhena-osoba-z-publichnih-zakupivel/", 0)
	}

	def __init__(self, interface, cookies=None):
		super().__init__(interface, cookies=cookies)
		self.pomohach = Load_data(self.qt_logs)

	def search(self, search_query=None, subject=None, grade=None, pagination=(1, 11), proxy=None):
		if not subject:
			raise NotSubjectError

		a = self.pomohach.search(
			subject=subject,
			storinka=pagination
		)
		self.res_list += a
		return a

	def processing_data(self, urls=None, proxy=None):
		return self.pomohach.processing_data(url=urls if urls else self.res_list)