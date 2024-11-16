from pyhive import hive

class Hive():
    CONN = None
    IP = "34.159.43.81"
    
    @staticmethod
    def set_ip(ip: str):
        Hive.IP = ip
    
    @staticmethod
    def _get_connection():
        if Hive.CONN is None:
            Hive.CONN = hive.Connection(host=Hive.IP, port=10000, username="hadoop")
        return Hive.CONN
    
    @staticmethod
    def get_version():
        conn = Hive._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT version()")
        return cur.fetchone()[0]
    
    @staticmethod
    def drop_tables():
        conn = Hive._get_connection()
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS ids PURGE")
        conn.commit()
        return ""
    
    @staticmethod
    def get_sets():
        conn = Hive._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT(set_name) FROM ids")
        return [x[0] for x in cur.fetchall()]
    
    @staticmethod
    def get_download_ids():
        conn = Hive._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM todownload")
        return [x[0] for x in cur.fetchall()]
