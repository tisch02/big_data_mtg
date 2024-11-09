from flask import Flask
from src.scraper import Scraper
from src.hadoop import Hadoop
from src.postgres import PostgresQL

app = Flask(__name__)
IP = "34.89.168.124"

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

if __name__ == '__main__':    
    PostgresQL.IP = IP
    app.run(host="0.0.0.0", port=38383, debug=True)
