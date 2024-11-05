from bs4 import BeautifulSoup


def scrape_set_names(path: str):
    html_doc: str = ""
    with open(path, "r") as file:
        html_doc = file.read()

    soup = BeautifulSoup(html_doc, 'html.parser')

    select = soup.find(id="ctl00_ctl00_MainContent_Content_SearchControls_setAddText")
    values = [option.get("value") for option in select.find_all("option")[1:]]
    return values
