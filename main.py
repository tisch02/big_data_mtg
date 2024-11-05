from src.webpage_downloader import download_page, donwload_serach_result
from src.scrape_set_names import scrape_set_names
from src.scrape_card_ids import scrape_card_ids

if __name__=="__main__":
    path = download_page(url="https://gatherer.wizards.com/pages/Default.aspx", filename="sets.html", overwrite=False)
    names = scrape_set_names(path=path)[0:1]

    for name in names:
        path_list = donwload_serach_result(name=name, overwrite=False)
        card_ids = []
        for p in path_list:
            card_ids += scrape_card_ids(path=p)

        print(len(card_ids))
