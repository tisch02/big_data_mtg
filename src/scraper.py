from datetime import datetime
from bs4 import BeautifulSoup
import urllib.request
import pandas as pd

from src.postgres import PostgresQL

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
        
        # Return true if there are no cards
        if len(pagination) == 0:
            return True
        
        # Check if last page in pagination. If so, stop loop
        last = str(pagination[-1].text).replace("\xa0", "")
        return last not in [">", ">>"]
    
    @staticmethod
    def _get_card_ids(html_content: str) -> list:
        soup = BeautifulSoup(html_content, 'html.parser')
        rows = soup.find_all("tr", {"class": "cardItem"})
        return [int(row.find("a").get("href").split("multiverseid=")[1].split("&")[0]) for row in rows]
    
    @staticmethod
    def card_ids(set_name):  
        cols = ["id", "insert_date", "set_name"]
        df = pd.DataFrame(columns=cols)
        page_num = 0
        stop = False
        results = []

        # Return empty df if no card ids are to scrape
        if set_name is None:
            return df

        while not stop:
            # Concatenate URL with card search query and page number
            url = f"https://gatherer.wizards.com/Pages/Search/Default.aspx?page={page_num}"
            url += f"&set=[\"{set_name.replace(" ", "+")}\"]"

            # Concatenate unique file name and download page            
            content = Scraper._get_html(url)
            ids = Scraper._get_card_ids(content)
            results.append((url, ids, datetime.now().isoformat()))
            
            # Continue through all pages              
            if Scraper._is_last(content):
                stop = True
            page_num += 1
            
        # Create dataframe        
        for url, ids, date in results:
            append_frame = pd.DataFrame(data={
                "id": ids,
                "insert_date": [str(date)] * len(ids),
                "set_name": [set_name] * len(ids)
            })            
            df = pd.concat([df, append_frame])
        
        return df
    
    @staticmethod
    def _get_row_content(soup: BeautifulSoup, id: str) -> str:
        row = soup.find(id=id)
        div = row.find_all("div", {"class": "value"})[0]
        return div.get_text().replace("\r\n","").strip()
    
    @staticmethod
    def _parse_text_items(soup: BeautifulSoup):
        return "".join([(f"@{e["alt"]}@" if "<img" in str(e) else str(e)) for e in soup])
    
    @staticmethod
    def _get_card_number(soup: BeautifulSoup) -> int | None:
        row = soup.find(id="ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_numberRow")
        if row is None:
            return None
                
        return int(row.find_all("div", {"class": "value"})[0].get_text())
    
    @staticmethod
    def _get_card_text(soup: BeautifulSoup) -> str | None:
        """Scrapes the card text
        """
        # Return none if no text is on the card
        row = soup.find(id="ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_textRow")
        if row is None:
            return None
        
        # Get list text srings
        strings = []
        for row in row.find_all("div", {"class": "cardtextbox"}):
            complete_result = ""
            for e in row:
                if "<i>" in str(e):
                    # parse_italic
                    complete_result += f"<i>{Scraper._parse_text_items(e)}</i>"                    
                else:
                    # parse regular
                    complete_result += f"@{e["alt"]}@" if "<img" in str(e) else str(e)                    

            strings.append(complete_result)

        # Concatenate string with linebreak
        return "\r\n".join(strings)
    
    @staticmethod
    def _get_card_story(soup: BeautifulSoup) -> str | None:
        """Scrapes the flavour text
        """
        # Return none if no story is on the card
        row = soup.find(id="ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_flavorRow")
        if row is None:
            return None
        
        # Get list of story items
        strings = []
        for row in row.find_all("div", {"class": "flavortextbox"}):
            row_str = "".join([str(e) for e in row])
            strings.append(row_str)
            
        # Concatenate string with linebreak
        return "\r\n".join(strings)
    
    @staticmethod
    def _get_card_set(soup: BeautifulSoup) -> str:
        row = soup.find(id="ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_currentSetSymbol").find_all("a")
        return row[1].get_text()
        
    @staticmethod
    def _get_card_mana_val(soup: BeautifulSoup) -> int | None:
        row = soup.find(id="ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_cmcRow")
        if row is None:
            return None
                
        return int(row.find_all("div", {"class": "value"})[0].get_text())
    
    @staticmethod
    def _get_card_artist(soup: BeautifulSoup) -> str | None:    
        row = soup.find(id="ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ArtistCredit")
        return str(row.find_all("a")[0].get_text())
    
    @staticmethod
    def _get_card_image(soup: BeautifulSoup) -> int | None:    
        img = soup.find(id="ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_cardImage")
        return img["src"].replace("../..", "https://gatherer.wizards.com")
    
    @staticmethod
    def _get_card_mana_cost(soup: BeautifulSoup) -> str | None:    
        row = soup.find(id="ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_manaRow")
        if row is None:
            return None

        rows = row.find_all("div", {"class": "value"})[0].find_all("img")
        row_str = "".join([f"@{row["alt"]}@" for row in rows])

        return row_str
    
    @staticmethod
    def cards(ids: list[tuple[int, str]]) -> str:
        cols = ["id", "name", "type", "mana_val", "mana_cost", "card_num", "set", "artist", "text", "story", "url", "img"]
        
        cards = []
        for id, set_name in ids:
            try:
                cards += [pd.DataFrame(data=Scraper.card(id), columns=cols, index=["id"])]
            except Exception as ex:
                print(f"Error for Card-ID: ", id)
                print(ex)
                
                error_data = {
                    "id": id,
                    "name": "ERROR!",
                    "set": set_name
                }
                cards += [pd.DataFrame(data=error_data, columns=cols, index=["id"])]
        
        if len(cards) == 0:
            return 0
        
        df = pd.concat(cards)                
        return len(df) if PostgresQL.insert_cards(df) else 0
    
    @staticmethod
    def card(id: int):
        url = f"https://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid={id}"        
        content = Scraper._get_html(url)
        
        soup = BeautifulSoup(content, 'html.parser')
        return {
            "id": id,
            "name": Scraper._get_row_content(soup, "ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_nameRow"),
            "type": Scraper._get_row_content(soup, "ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_typeRow"),
            "mana_val": Scraper._get_card_mana_val(soup),
            "mana_cost": Scraper._get_card_mana_cost(soup),
            "set": Scraper._get_card_set(soup),
            "card_num": Scraper._get_card_number(soup),
            "artist": Scraper._get_card_artist(soup),
            "text": Scraper._get_card_text(soup),
            "story": Scraper._get_card_story(soup),
            "url": url,
            "img": Scraper._get_card_image(soup)
        }
