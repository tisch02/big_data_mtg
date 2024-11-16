from datetime import datetime
from flask import Flask, Response
from src.scraper import Scraper
from src.hadoop import Hadoop
from src.postgres import PostgresQL
from src.hive import Hive

app = Flask(__name__)
IP = "35.198.76.213"
Hive.set_ip(IP)
PostgresQL.set_ip(IP)

@app.route("/api/test")
def test():
    try: 
        # Test all connections
        hive_version = Hive.get_version()
        postgres_version = PostgresQL.get_version()
                
        return {
            "hive version": hive_version,
            "postgres_version": postgres_version
        }
    except:
        return Response(status=400)

@app.route("/api/postgres-create")
def postgres_create():
    return PostgresQL.create_tables()

@app.route("/api/postgres-drop")
def postgres_drop():
    return PostgresQL.drop_tables()

@app.route("/api/hive-drop")
def hive_drop():
    return Hive.drop_tables()

@app.route("/api/set-names")
def hadoop_read():
    hdfs = Hadoop(ip=IP)
    path = "/user/hadoop/mtg/sets/set_names.html"
    names = Scraper.sets(hdfs.get_file(path))
    return PostgresQL.store_sets(names)

@app.route("/api/mark-stored-sets")
def stored_sets():
    set_names = Hive.get_sets()
    print(set_names)
    PostgresQL.mark_stored_sets(set_names)
    return ", ".join(set_names)

@app.route("/api/prepare-card-ids")
def prepare_card_ids():
    # TODO: Only return if a certain amount of undownloaded cards is passed
    
    set_name = PostgresQL.get_set_name()
    print(set_name)
    
    if set_name is not None:
        df = Scraper.card_ids(set_name)    
        return df.to_csv(index=False, sep="\t")
    return Response(response="There is no more set to dowload", status=400)

@app.route("/api/download-cards")
def download_cards():
    #ids = Hive.get_download_ids()
    ids = [603042, 182972, 446155, 643407]
       
    if len(ids) == 0:
        return Response(response="There are no cards to scrape", status=400)
        
    count = Scraper.cards(ids)
    
    if count == 0:
        return Response(response="Error while scraping the cards", status=400)
    
    return Response(response=f"Scraped {count} cards ...", status=200)

@app.route("/api/downloaded-cards")
def downloaded_cards():
    df = PostgresQL.downloaded_cards()
    return df.to_csv(index=False, sep=",")

if __name__ == '__main__':    
    PostgresQL.IP = IP
    app.run(host="0.0.0.0", port=38383, debug=True)
