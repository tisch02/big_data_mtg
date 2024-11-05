from bs4 import BeautifulSoup


def scrape_card_ids(path: str):
    html_doc: str = ""
    with open(path, "r") as file:
        html_doc = file.read()

    soup = BeautifulSoup(html_doc, 'html.parser')
    rows = soup.find_all("tr", {"class": "cardItem"})
    
    result = [row.find("a").get("href").split("multiverseid=")[1] for row in rows]
    return result
