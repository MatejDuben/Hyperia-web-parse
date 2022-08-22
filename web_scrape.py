from bs4 import BeautifulSoup
import requests, re, json


class HyperiaWebScrape:
    def __init__(self):
        self.url = "https://www.hyperia.sk/kariera/"
        self.doc = BeautifulSoup(requests.get(self.url).content,"html.parser") #beautifulsoup document 
        
        self.job_json_data=[]  
        self.job_description_data = []
        self.job_links = []

    #najde vsetky pracovne ponuky na /kariera a ziska url adresu k nim
    def find_all_positions_on_career(self):    
        positions = self.doc.find(name="section", id='positions')
        for elements in positions:
            for pos in elements.find_all("a",class_="arrow-link",href=True):
                self.job_links.append(pos["href"])
        
    #zmeni url adresu bs dokumentu
    def change_url(self, new_url):
        self.url = "https://www.hyperia.sk"+new_url
        self.doc = BeautifulSoup(requests.get(self.url).content,"html.parser")

    #podla ziskanej url pojde na stranku s popoisom o pracovnej ponuke a najde konkretne informacie
    def get_job_description(self):
        hero_section = self.doc.find("section",class_="position-hero")
        job_title = hero_section.find("h1")
        hero_icons = self.doc.find('div',class_='hero-icons')
        job_data_in_paragraph = hero_icons.find_all('p')    #vrati list p tagov v kotrych su potrebne data
        job_position_contact_data = self.doc.find('div',class_='position-contact').find('p')
        temp = []

        #filtrovanie konkretneho slova/cislic a ulozenie do listu
        temp.append(job_title.get_text())
        r_search_country = re.search('(?<=:).*$',str(job_data_in_paragraph[0].get_text()))
        temp.append(r_search_country.group())
        r_search_salary = re.search('\d.+.,- €',str(job_data_in_paragraph[1].get_text()))
        temp.append(r_search_salary.group())
        r_search_type = re.search('(?<=pomeru).*$',str(job_data_in_paragraph[2].get_text()))
        temp.append(r_search_type.group())
        r_search_contact = re.search('([a-zA-z0-9_\-\.])+@([a-zA-z0-9_\-\.])+\.([a-zA-Z]){2,5}',str(job_position_contact_data.get_text()))
        temp.append(r_search_contact.group())

        self.job_description_data.append(temp)

    #ziskane data da do dictionary formatu a transformuje ich do jsonu
    def write_job_data_to_json(self):
        for data in self.job_description_data:
            json_dict = {
                "title": data[0],
                "place": data[1],
                "salary": data[2],
                "contract_type": data[3],
                "contact_email": data[4]
            }

            self.job_json_data.append(json_dict)

        self.job_json_data = json.dumps(self.job_json_data,ensure_ascii=False)

    #metoda ktora spusti program
    def run(self):
        self.find_all_positions_on_career()
        for job_link in self.job_links:
            self.change_url(job_link)
            self.get_job_description()

        self.write_job_data_to_json()


if __name__ == '__main__':
    script = HyperiaWebScrape()
    script.run()

    with open("hyperia-career.json", "w") as f:
        f.write(script.job_json_data)