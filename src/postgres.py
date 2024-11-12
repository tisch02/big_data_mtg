import psycopg2
from flask import Response

class PostgresQL():
    CONN = None
    IP = "34.159.43.81"
    
    @staticmethod
    def _get_connection():
        if PostgresQL.CONN is None:
            PostgresQL.CONN = psycopg2.connect(database="mtg", host=PostgresQL.IP, user="big_data", password="big_data", port="5432")
        return PostgresQL.CONN
    
    @staticmethod
    def create_tables():
        try:
            conn = PostgresQL._get_connection()
            cur = conn.cursor()
        
            # Create Schema
            cur.execute("""CREATE SCHEMA IF NOT EXISTS data;""")
            conn.commit()
            
            # Creat tables        
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS data.sets (
                            name VARCHAR(256) PRIMARY KEY,
                            downloaded BOOL
                        );""")
            conn.commit()  
        
            return Response(status=200)
            
        except:
            return Response(status=400)
    
    @staticmethod
    def drop_tables():
        try:
            conn = PostgresQL._get_connection()
            cur = conn.cursor()            
            cur.execute("""DROP TABLE IF EXISTS data.sets;""")
            conn.commit()  
        
            return Response(status=200)
            
        except:
            return Response(status=400)    
    
    @staticmethod
    def store_sets(names: list[str]):
        try:
            conn = PostgresQL._get_connection()
            cur = conn.cursor()
            
            # Get names that are already stored
            cur.execute("""SELECT name FROM data.sets;""")
            set_names = [x[0] for x in cur.fetchall()]            
            
            # Create value array for every name that is not already stored
            values = []
            for name in names:
                if name not in set_names:
                    values.append((name, False))
                    
            # Create a query string for every values
            query = """INSERT INTO data.sets (name, downloaded) VALUES (%s, %s);"""
            
            cur.executemany(query, values)
            conn.commit()  
        
            return Response(response=f"Added {len(values)} new sets to the database.", status=200)
            
        except Exception as error:
            print(error)
            return Response(response=str(error), status=400)