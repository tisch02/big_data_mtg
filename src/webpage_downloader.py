import os
import urllib.request

from bs4 import BeautifulSoup

def download_page(url: str, filename: str, overwrite:bool = False) -> str:
    # Create dir if it not already exists
    dir_path = os.path.join(os.getcwd(), "data")
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    # Download file
    path = os.path.join(dir_path, filename)
    if overwrite or not os.path.exists(path):
        urllib.request.urlretrieve(url, path)

    # Return path of the written file
    return path

def donwload_serach_result(name: str, overwrite: bool = False) -> str:

    page_num = 0
    stop = False
    path_list = []
    
    while not stop:
        # Concatenate URL with card search query and page number
        url = "https://gatherer.wizards.com/Pages/Search/Default.aspx?set="
        url += f"[\"{name.replace(" ", "+")}\"]"
        url += f"&page={page_num}"
        
        # Concatenate unique file name
        filename = f"{name.lower().replace(" ", "_")}_{page_num}.html"

        # Donwload page
        path = download_page(url, filename)
        path_list.append(path)

        # Create soup from downloaded content    
        with open(path, "r") as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            pagination = soup.find_all("div", {"class": "pagingcontrols"})[0].find_all("a")

            # Check if last page in pagination. If so, stop loop
            last = str(pagination[-1].text).replace("\xa0", "")
            if last not in [">", ">>"]:
                stop = True

        page_num += 1
    return path_list
