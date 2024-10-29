import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup

from modules.decorate import async_session

class Load_data:
	def search(self, object, storinka=(1,2), proxy=None):
		@async_session(None)
		async def async_search(session: aiohttp.ClientSession, storinka):
			async with session.get(f"https://pomahach.com{object}/page/{storinka}/", proxy=proxy) as req:
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

			return {
				"platform": "pomahach",
				"type": "quiz" if soup.find(class_="option-marker quiz") else "multiquiz",
				"name_test": soup.find(class_="panel-body").text,

				"answers": [{
					"text": obj.text.strip(),
					"correctness": bool("list-group-item-success" in obj.get("class", []))
				} for obj in soup.find_all(class_="list-group")[1].find_all("li")]}
		
		
		async def run():
			task = [async_processing_data(url) for url in url]
			return await asyncio.gather(*task)

		return asyncio.run(run())

def data_info():
	list_object = [
		'/cat/biologiya/', '/cat/geografiya/', '/cat/himiya/', '/cat/istoriya-ukrayini/', '/cat/pravoznavstvo/', '/cat/ekonomika/', 
		'/cat/pdr/', '/cat/algebra/', '/cat/gigiyena-ta-ekologiya/', '/cat/ukrayinska-mova-i-literatura/', '/cat/notarius/', 
		'/cat/bankivska-sistema/', '/cat/zagalna-ta-specialna-hirurgiya/', '/cat/viyskova-i-ekstremalna-medicina/', '/cat/dilova-ukrayinska-mova/', 
		'/cat/kulturologiya/', '/cat/angliyska-mova/', '/cat/agrohimiya/', '/cat/ispanska-mova/', '/cat/francuzka-mova/', '/cat/imunologiya/', 
		'/cat/menedzhment-i-administruvannya/', '/cat/pozhezhna-bezpeka/', '/cat/osnovi-virobnichoyi-sanitariyi/', '/cat/normuvannya-prirodnogo-ta-shtuchnogo-osvitlennya/', 
		'/cat/podannya-pershoyi-dolikarskoyi-dopomogi/', '/cat/osnovni-zakonodavchi-akti-pro-ohoronu-praci/', '/cat/organizaciyni-pitannya-ohoroni-praci/', 
		'/cat/ekonomika-praci-y-socialno-trudovi-vidnosini/', '/cat/informatika/', '/cat/prirodnichi-nauki/', '/cat/stomatologiya/', '/cat/abdominalna-hirurgiya/', 
		'/cat/anesteziologiya-reanimatologiya-intensivna-terapiya-v-hirurgiyi/', '/cat/nevidkladna-hirurgiya-v-urologiyi-ta-ginekologiyi/', '/cat/onkologiya/', 
		'/cat/opiki-i-vidmorozhennya/', '/cat/osnovi-travmatologiyi-i-neyrohirurgiyi/', '/cat/proktologiya/', '/cat/sercevo-sudinnoyi-hirurgiya/', '/cat/sudinna-hirurgiya/', 
		'/cat/infekciyni-zahvoryuvannya/', '/cat/akusherstvo-ta-ginekologiya/', '/cat/astronomiya/', '/cat/fizika/', '/cat/matematika/', '/cat/stolici-krayin/', 
		'/cat/rozvitok-geografichnih-znan-pro-zemlyu/', '/cat/alergologiya/', '/cat/anesteziologiya/', '/cat/mistectvo/', '/cat/sport/', '/cat/kosmetologiya/', '/cat/muzika/', 
		'/cat/istoriya-svitu/', '/cat/mifologiya/', '/cat/svitova-literatura/', '/cat/ekologiya/', '/cat/ekonomika-pidpriyemstva/', 
		'/cat/mashini-ta-obladnannya-dlya-pererobki-silskogospodarskoyi-produkciyi/', '/cat/tehnichniy-servis-v-agropromislovomu-kompleksi/', 
		'/cat/ekspluataciya-mashin-i-obladnannya/', '/cat/finansoviy-oblik/', '/cat/tehnichna-mehanika/', '/cat/mashini-i-obladnannya-dlya-tvarinnictva/', 
		'/cat/marketing/', '/cat/metrologiya-i-standartizaciya/', '/cat/zahist-vitchizni/', '/cat/oblik-i-audit/', '/cat/literaturne-chitannya/', '/cat/muzichne-mistectvo/', 
		'/cat/lyudina-i-svit/', '/cat/etika/', '/cat/fizkultura/', '/cat/administrativne-pravo/', '/cat/marketingova-cinova-politika/', '/cat/cinoutvorennya-brendiv/', 
		'/cat/derzhavne-regulyuvannya-procesu-cinoutvorennya-v-ukrayini/', '/cat/ocinyuvannya-pomilki-i-riziku-v-cinoutvorenni/', '/cat/cinoutvorennya-v-mizhnarodnomu-marketingu/', 
		'/cat/marketingova-strategiya-cinoutvorennya/', '/cat/osoblivosti-doslidzhennya-rinkovoyi-konyunkturi/', '/cat/roriguvannya-cini/', 
		'/cat/procedura-priynyattya-rishen-schodo-viznachennya-cini/', '/cat/metodichni-pidhodi-do-cinoutvorennya-v-sistemi-marketingu/', '/cat/faktori-marketingovogo-cinoutvorennya/', 
		'/cat/sistema-cin-ta-yih-klasifikaciya/', '/cat/cina-yak-instrument-marketingovoyi-cinovoyi-politiki/', '/cat/formuvannya-cinovoyi-politiki/', '/cat/vvedennya-v-cinoutvorennya/', 
		'/cat/logistika-u-rinkoviy-ekonomici/', '/cat/klasifikaciya-form-logistichnih-utvoren/', '/cat/harakteristika-osnovnih-elementiv-logistiki/', 
		'/cat/tehnologichni-procesi-ta-upravlinnya-materialnimi-potokami/', '/cat/faktori-formuvannya-logistichnih-sistem/', 
		'/cat/upravlinnya-materialnimi-potokami-v-logistichnih-sistemah/', '/cat/zagotivelna-logistika/', '/cat/sutnist-rozpodilchoyi-logistiki/', '/cat/vnutrishnovirobnicha-logistika/', 
		'/cat/logistika-skladuvannya/', '/cat/transportna-logistika/', '/cat/globalizaciya-logistichnih-procesiv/', '/cat/groshi-i-kredit/', 
		'/cat/finansova-politika-i-finansoviy-mehanizm/', '/cat/osnovni-principi-regulyaciyi-fiziologichnih-funkciy/', '/cat/gumoralna-regulyaciya-fiziologichnih-funkciy-organizmu/', 
		'/cat/biznes-planuvannya-zed-aviaciynogo-pidpriyemstva/', '/cat/fiziologiya-centralnoyi-nervovoyi-sistemi/', '/cat/fizichna-ta-koloyidna-himiya/', '/cat/epidemiologiya/', 
		'/cat/endoskopiya/', '/cat/normalna-ta-patologichna-anatomiya-topografichna-anatomiya-z-operativnoyu-hirurgiyeyu/', '/cat/gistologiya-embriologiya/', '/cat/sudova-medicina/', 
		'/cat/zarubizhna-literatura/', '/cat/medicina/', '/cat/biohimiya/', '/cat/dermatologiya/', '/cat/virusologiya/', '/cat/dityacha-hirurgiya/', '/cat/gigiyena-ta-ekologiya/', 
		'/cat/kliniko-laboratorna-funkcionalna-diagnostika/', '/cat/infekciyni-hvorobi-epidemiologiya/', '/cat/vnutrishnya-medicina/', '/cat/geometriya/', '/cat/medichna-genetika/', 
		'/cat/neyrohirurgiya/', '/cat/otolaringologiya/', '/cat/oftalmologiya/', '/cat/nevidkladna-dopomoga/', '/cat/litnya-praktika/', '/cat/onkologiya-radiologiya/', '/cat/pediatriya/', 
		'/cat/tovaroznavstvo/', '/cat/byudzhetna-sistema/', '/cat/dilovodstvo/', '/cat/kriminologiya/', '/cat/gerbologiya/', '/cat/ekonomichna-teoriya/', 
		'/cat/ekonomika-starodavnogo-svitu/', '/cat/ekonomika-antichnosti/', '/cat/ekonomika-serednovichchya/', '/cat/ekonomika-epohi-pervisnogo-nagromadzhennya-kapitalu/', 
		'/cat/ekonomika-v-epohu-vilnoyi-konkurenciyi/', '/cat/istoriya-ekonomiki/', '/cat/istoriya-mistectv/', '/cat/ukrayinska-kultura/', '/cat/makroekonomika/', '/cat/filosofiya/', 
		'/cat/legka-atletika/', '/cat/pedagogika-pochatkovoyi-osviti/', '/cat/biogeografiya/', '/cat/radiobiologiya/', '/cat/finansi/', '/cat/teoriya-i-metodika-plavannya/', 
		'/cat/fizichna-geografiya-materikiv-i-okeaniv/', '/cat/dokumentno-informaciyni-komunikaciyi/', '/cat/religiya/', '/cat/etika-i-estetika/', 
		'/cat/istoriya-ukrayinskoyi-literaturi/', '/cat/rekreaciyna-geografiya/', '/cat/fiziologiya-lyudini-i-tvarin/', '/cat/fizika-z-osnovami-biofiziki/', 
		'/cat/matematichna-statistika/', '/cat/regionalna-ekonomichna-i-socialna-geografiya-svitu/', '/cat/ekonomichna-i-socialna-geografiya-ukrayini/', 
		'/cat/silskogospodarske-virobnictvo/', '/cat/vikova-fiziologiya/', '/cat/podatkova-sistema/', '/cat/rinok-finansovih-poslug/', '/cat/arheologiya/', 
		'/cat/elektrichni-mashini-i-aparati/', '/cat/politologiya/', '/cat/psihologiya/', '/cat/analitichna-himiya/', '/cat/strahuvannya/', '/cat/literaturoznavstvo/', 
		'/cat/turizm/', '/cat/finansoviy-rinok/', '/cat/teoriya-rozmischennya-produktivnih-sil/', '/cat/upovnovazhena-osoba-z-publichnih-zakupivel/']

	return {"search": {"object": list_object,
				"klass": False,
				"q": False,
				"storinka": True,
				"proxy": True},
				"processing_data": {"url": "list"},
				"proxy": True}

def main():
	pomahach = Load_data()
	listik = pomahach.search('/cat/biologiya/', storinka=(1,2))
	
	a = pomahach.processing_data(listik)
	print(a)
	
if __name__ == "__main__":
	main()