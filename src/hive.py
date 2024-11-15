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
            Hive.CONN = hive.Connection(host=Hive.IP, port=10000)
        return Hive.CONN
    
    @staticmethod
    def get_version():
        conn = Hive._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT version()")
        return cur.fetchone()[0]
    
    @staticmethod
    def get_sets():
        conn = Hive._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT(set_name) FROM ids")
        return cur.fetchmany()
    