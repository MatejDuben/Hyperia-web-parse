from bs4 import BeautifulSoup
import requests, re, json


class HyperiaWebScrape:
    def __init__(self):
        self.url = "https://www.hyperia.sk/kariera/"
        self.doc = BeautifulSoup(requests.get(self.url).content,"html.parser") #beautifulsoup document 
        
        self.job_description_data = []
        self.job_links = []

    #najde vsetky pracovne ponuky na /kariera a ziska url adresu k nim
    def find_all_positions_on_career(self):    
        positions = self.doc.find(name="section", id='positions')
        for elements in positions:
            for pos in elements.find_all("a",class_="arrow-link",href=True):
                self.job_links.append(pos["href"])
        
    #zmeni url adresu bs dokumentu
    def change_url(self, new_url:str):
        self.url = "https://www.hyperia.sk"+new_url
        self.doc = BeautifulSoup(requests.get(self.url).content,"html.parser")

    #podla ziskanej url pojde na stranku s popoisom o pracovnej ponuke a najde konkretne informacie
    def get_job_description(self):
        hero_section = self.doc.find("section",class_="position-hero")
        job_title = hero_section.find("h1").get_text()
        hero_icons = self.doc.find('div',class_='hero-icons')
        job_data_in_paragraph = hero_icons.find_all('p')    #vrati list p tagov v kotrych su potrebne data
        job_position_contact = self.doc.find('div',class_='position-contact').find('p').get_text()

        def r_search(regex:str,data:str):
            return re.search(regex,data).group()

        specific_job_description_data = [
            job_title,
            r_search("(?<=:).*$",job_data_in_paragraph[0].get_text()),
            r_search("\d(.*?)€",job_data_in_paragraph[1].get_text()),
            r_search("(?<=pomeru).*$",job_data_in_paragraph[2].get_text()),
            r_search("([a-zA-z0-9_\-\.])+@([a-zA-z0-9_\-\.])+\.([a-zA-Z]){2,5}",job_position_contact),
        ]

        self.job_description_data.append(specific_job_description_data)


    def get_job_data(self):
        return self.job_description_data

    #metoda ktora spusti program
    def run(self):
        self.find_all_positions_on_career()
        for job_link in self.job_links:
            self.change_url(job_link)
            self.get_job_description()

class ListToJson():
    def __init__(self,raw_data:list):
        self.raw_data = raw_data
        self.job_json_data = []
    
    def convert(self):
        for data in self.raw_data:
            json_dict = {
                "title": data[0],
                "place": data[1],
                "salary": data[2],
                "contract_type": data[3],
                "contact_email": data[4]
            }

            self.job_json_data.append(json_dict)

        self.job_json_data = json.dumps(self.job_json_data,ensure_ascii=False)

        return self.job_json_data



if __name__ == '__main__':
    scraping_script = HyperiaWebScrape()
    scraping_script.run()

    jobs_data_list = scraping_script.get_job_data()
    jobs_data_json = ListToJson(jobs_data_list).convert()

    with open("hyperia-career.json", "w") as f:
        f.write(jobs_data_json)