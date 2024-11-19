from datetime import datetime
from flask import Flask, Response
from src.scraper import Scraper
from src.hadoop import Hadoop
from src.postgres import PostgresQL
from src.hive import Hive

app = Flask(__name__)
IP = "127.0.0.1"

@app.route("/api/test")
def test():
    """Tests the PostgrSQL and Hive connection."""
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
    """Creates all needed PostgreSQL tables if the don't exist"""
    try:
        PostgresQL.create_tables()
        return Response(status=200)
    except:
        return Response(status=400) 

@app.route("/api/store-set-names")
def store_set_names():
    """Stores all set names into PostgreSQL"""
    try:
        hdfs = Hadoop()
        path = "/user/hadoop/mtg/sets/set_names.html"
        names = Scraper.sets(hdfs.get_file(path))
        result = PostgresQL.store_sets(names)
        return Response(response=result, status=200)    
    except:
        return Response(status=400)
    

@app.route("/api/mark-stored-sets")
def mark_stored_sets():
    """Marks all sets in the PostgreSQL which names are in the Hive table"""
    try:
        set_names = Hive.get_sets()    
        PostgresQL.mark_stored_sets(set_names)
        result = ", ".join(set_names)
        return Response(response=result, status=200)    
    except:
        return Response(status=400)
    
@app.route("/api/get-set-ids")
def get_set_ids():
    """Scapres a list of card ids for a set."""
    try:
        set_name = PostgresQL.get_set_name()
        df = Scraper.card_ids(set_name)    
        return df.to_csv(index=False, sep="\t")
    except:
        return Response(status=400)

@app.route("/api/download-cards")
def download_cards():
    """Dowloads and stores iformation of all cards that should be downloaded."""
    ids = Hive.get_download_ids()
       
    if len(ids) == 0:
        return Response(response="There are no cards to scrape", status=400)
        
    count = Scraper.cards(ids)
    
    if count == 0:
        return Response(response="Error while scraping the cards", status=400)
    
    return Response(response=f"Scraped {count} cards ...", status=200)

@app.route("/api/downloaded-cards")
def downloaded_cards():
    """Gets a list of all cards that are downloaded."""
    try:
        df = PostgresQL.downloaded_cards()
        df = df.rename(columns={"set": "set_name"})
        return df.to_csv(index=False, sep=",")
    except:
        return Response(status=400)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=38383, debug=True)
