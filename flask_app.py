from datetime import datetime
from flask import Flask, Response
from src.scraper import Scraper
from src.hadoop import Hadoop
from src.postgres import PostgresQL
from src.hive import Hive

app = Flask(__name__)
IP = "34.107.40.189"
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

@app.route("/api/stored-sets")
def stored_sets():
    set_names = Hive.get_sets()
    print(set_names)
    return ""

@app.route("/api/prepare-card-ids")
def prepare_card_ids():
    

    set_name = PostgresQL.get_set_name()    
    df = Scraper.card_ids(set_name)
    
    # set_names = Hive.get_sets()
    
    # Hive.insert_ids("my-url", "my-set", [1, 2, 3])
    
    
    # ----------
    
    # Steps for Airflow
    # Create dir for raw files
    # Create dir for CSV files
    # Create table for CSV files
    # Call API
    
    # Check how many cards are ready for download
    
    # If to few: 
    # - Download web pages
    # - Store the raw files to HDFS
    # - Scrape card IDs
    # - Create CSV
    # - PUT CSV to HDFS tables
    return df.to_csv(index=False)

if __name__ == '__main__':    
    PostgresQL.IP = IP
    app.run(host="0.0.0.0", port=38383, debug=True)
