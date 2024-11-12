from flask import Flask
from src.scraper import Scraper
from src.hadoop import Hadoop
from src.postgres import PostgresQL
from src.hive import Hive

app = Flask(__name__)
IP = "34.159.43.81"

@app.route("/api/postgres-create")
def postgres_create():
    return PostgresQL.create_tables()

@app.route("/api/postgres-drop")
def postgres_drop():
    return PostgresQL.drop_tables()

@app.route("/api/set-names")
def hadoop_read():
    hdfs = Hadoop(ip=IP)
    path = "/user/hadoop/mtg/sets/set_names.html"
    names = Scraper.sets(hdfs.get_file(path))    
    return PostgresQL.store_sets(names)

@app.route("/api/prepare-card-ids")
def prepare_card_ids():
    return Hive.get_version()
    
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
    return result

if __name__ == '__main__':    
    PostgresQL.IP = IP
    app.run(host="0.0.0.0", port=38383, debug=True)
