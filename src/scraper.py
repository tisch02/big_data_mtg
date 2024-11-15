from bs4 import BeautifulSoup
import urllib.request

class Scraper():
    
    @staticmethod
    def sets(html_str):        
        soup = BeautifulSoup(html_str, 'html.parser')
        select = soup.find(id="ctl00_ctl00_MainContent_Content_SearchControls_setAddText")
        return [option.get("value") for option in select.find_all("option")[1:]]
    
    @staticmethod
    def _get_html(url: str):
        page = urllib.request.urlopen(url) 
        html = page.read().decode("utf8")
        page.close()
        return html
    
    @staticmethod
    def _is_last(html_content: str) -> bool:
        # Scrape content
        soup = BeautifulSoup(html_content, 'html.parser')
        pagination = soup.find_all("div", {"class": "pagingcontrols"})[0].find_all("a")
        
        # Check if last page in pagination. If so, stop loop
        last = str(pagination[-1].text).replace("\xa0", "")
        return last not in [">", ">>"]
    
    @staticmethod
    def _get_card_ids(html_content: str) -> list:
        soup = BeautifulSoup(html_content, 'html.parser')
        rows = soup.find_all("tr", {"class": "cardItem"})
        return [int(row.find("a").get("href").split("multiverseid=")[1]) for row in rows]
    
    @staticmethod
    def card_ids(set_name):                
        page_num = 0
        stop = False
        results = []
    
        while not stop:
            # Concatenate URL with card search query and page number
            url = f"https://gatherer.wizards.com/Pages/Search/Default.aspx?page={page_num}"
            url += f"&set=[\"{set_name.replace(" ", "+")}\"]"            
                    
            # Concatenate unique file name and download page
            filename = f"{set_name.lower().replace(" ", "_")}_{page_num}.html"
            content = Scraper._get_html(url)
            ids = Scraper._get_card_ids(content)
            results.append((filename, ids))
            
            # Continue throug all pages              
            if Scraper._is_last(content):
                stop = True
            page_num += 1
            
        print(results)
        return results
        
        