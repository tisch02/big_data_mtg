from pyhive import hive
import pandas as pd

class Hive():

    @staticmethod
    def get_ip():
        return "hadoop"
    
    @staticmethod
    def _get_connection():
        return hive.Connection(host=Hive.get_ip(), port=10000, username="hadoop")
    
    @staticmethod
    def get_version():
        conn = Hive._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT version()")
        result = cur.fetchone()[0]        
        conn.close()
        return result
    
    @staticmethod
    def get_sets():
        conn = Hive._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT(set_name) FROM ids")
        result = [x[0] for x in cur.fetchall()]
        conn.close()
        return result
    
    @staticmethod
    def get_download_ids():
        conn = Hive._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, set_name FROM todownload")
        result = [(x[0], x[1]) for x in cur.fetchall()]     
        conn.close()
        return result
    
    def get_to_todownload_ids(count: int):
        conn = Hive._get_connection()
        cur = conn.cursor()        
        cur.execute("""SELECT ids.id, ids.set_name FROM ids WHERE ids.id NOT IN (SELECT downloaded.id FROM downloaded) LIMIT %s""", (count, ))
        cols = ["id", "set_name"]        
        result = [pd.DataFrame(data={"id": x[0], "set_name": x[1]}, columns=cols, index=["id"]) for x in cur.fetchall()]
        conn.close()
        return pd.concat(result)
