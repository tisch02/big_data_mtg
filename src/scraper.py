from bs4 import BeautifulSoup


class Scraper():
    
    @staticmethod
    def sets(html_str):        
        soup = BeautifulSoup(html_str, 'html.parser')
        select = soup.find(id="ctl00_ctl00_MainContent_Content_SearchControls_setAddText")
        return [option.get("value") for option in select.find_all("option")[1:]]
    