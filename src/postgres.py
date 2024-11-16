import psycopg2
from flask import Response
import pandas as pd
from sqlalchemy import create_engine 

class PostgresQL():
    CONN = None
    ALQ_CONN = None
    IP = "postgres"
    
    @staticmethod
    def set_ip(ip: str):
        PostgresQL.IP = ip
    
    @staticmethod
    def _get_connection():
        if PostgresQL.CONN is None:
            PostgresQL.CONN = psycopg2.connect(database="mtg", host=PostgresQL.IP, user="big_data", password="big_data", port="5432")
        return PostgresQL.CONN
    
    @staticmethod
    def _get_alq_connection():
        if PostgresQL.ALQ_CONN is None:
            con_str = f"postgresql+psycopg2://big_data:big_data@{PostgresQL.IP}:5432/mtg"
            db = create_engine(con_str)
            conn = db.connect() 
            PostgresQL.ALQ_CONN = conn
        return PostgresQL.ALQ_CONN    
    
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
            conn = PostgresQL._get_alq_connection()            
            cards_df.to_sql(name="cards", schema="data", con=conn, if_exists="replace", index=False)          
            return True                                          
        except Exception as error:
            print(error)
            return False

    @staticmethod
    def downloaded_cards() -> None:
        conn = PostgresQL._get_alq_connection()
        return pd.read_sql_query("SELECT id FROM data.cards", con=conn)
        