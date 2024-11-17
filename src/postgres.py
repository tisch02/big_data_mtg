import psycopg2
from flask import Response
import pandas as pd
from sqlalchemy import create_engine 

class PostgresQL():
    CONN = None
    ALQ_ENG = None
    
    @staticmethod
    def get_ip() -> str:
        return "postgres"

    @staticmethod
    def _get_connection():        
        if PostgresQL.CONN is None:
            PostgresQL.CONN = psycopg2.connect(database="mtg", host=PostgresQL.get_ip(), user="big_data", password="big_data", port="5432")
        return PostgresQL.CONN
    
    @staticmethod
    def _get_alq_engine():
        if PostgresQL.ALQ_ENG is None:
            con_str = f"postgresql+psycopg2://big_data:big_data@{PostgresQL.get_ip()}:5432/mtg"            
            PostgresQL.ALQ_ENG = create_engine(con_str)     
        return PostgresQL.ALQ_ENG    
    
    @staticmethod
    def get_version():
        conn = PostgresQL._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        return cur.fetchone()[0]
    
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
            
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS data.cards (
                            id INT PRIMARY KEY,
                            name VARCHAR(256),
                            type VARCHAR(256),
                            mana_val INT,
                            mana_cost VARCHAR(256),
                            set VARCHAR(256),
                            card_num INT,
                            artist VARCHAR(256),
                            text TEXT,
                            story TEXT,
                            url VARCHAR(1024),
                            img VARCHAR(1024)
                        );""")
            conn.commit()  
        
            return Response(status=200)
            
        except Exception as ex:
            print(ex)
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
        
    @staticmethod
    def get_set_name() -> str | None:
        try:
            conn = PostgresQL._get_connection()
            cur = conn.cursor()                
            cur.execute("""SELECT name FROM data.sets WHERE downloaded = false ORDER BY name LIMIT 1;""")
            fetch = cur.fetchone()
            return None if fetch is None else fetch[0]
            
        except Exception as error:
            return Response(response=str(error), status=400)
        
    @staticmethod
    def mark_stored_sets(sets: list[str]) -> None:
        try:
            conn = PostgresQL._get_connection()
            cur = conn.cursor()
            
            for set in sets:                
                cur.execute("""UPDATE data.sets SET downloaded = true WHERE downloaded = false AND name = %s;""", (set, ))
            conn.commit()
            
            return Response(status=200)
            
        except Exception as error:            
            return Response(response=str(error), status=400)
        
    @staticmethod
    def insert_cards(cards_df: pd.DataFrame) -> bool:        
        try:            
            conn = PostgresQL._get_alq_engine().connect() 
            cards_df.to_sql(name="cards", schema="data", con=conn, if_exists="append", index=False)
            conn.commit()
            conn.close()
            return True                                          
        except Exception as error:
            print(error)
            return False

    @staticmethod
    def downloaded_cards() -> None:
        conn = PostgresQL._get_alq_engine().connect() 
        result = pd.read_sql_query("SELECT id, set FROM data.cards", con=conn)
        conn.close()
        return result
    
    # Frontend methods -----------------------------------------------
    
    @staticmethod
    def search_cards(search_str: str, count: str):
        
        
        query = """
            CREATE EXTENSION IF NOT EXISTS pg_trgm;
            SELECT id, name, type, mana_cost, set, img, SIMILARITY(name, %s) AS sim FROM data.cards WHERE name != 'ERROR!' ORDER BY sim DESC LIMIT %s;
        """
        
        conn = PostgresQL._get_connection()
        cur = conn.cursor()
        
        cur.execute(query, (search_str, count))
        
        
        return [{
            "id": element[0],
            "name": element[1],
            "type": element[2],
            "mana_cost": element[3],
            "set": element[4],
            "img": element[5],
            "sim": element[6]
        } for element in cur.fetchall()]
        