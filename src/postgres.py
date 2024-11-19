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
        
        # Commit changes
        conn.commit()  
        
    @staticmethod
    def store_sets(names: list[str]):
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
    
        return f"Added {len(values)} new sets to the database."
        
    @staticmethod
    def get_set_name():
        conn = PostgresQL._get_connection()
        cur = conn.cursor()

        cur.execute("""SELECT name FROM data.sets WHERE downloaded = false ORDER BY name LIMIT 1;""")
        fetch = cur.fetchone()
        return None if fetch is None else fetch[0]
        
    @staticmethod
    def mark_stored_sets(sets: list[str]):
        conn = PostgresQL._get_connection()
        cur = conn.cursor()
            
        for set in sets:                
            cur.execute("""UPDATE data.sets SET downloaded = true WHERE downloaded = false AND name = %s;""", (set, ))
        conn.commit()
        
    @staticmethod
    def insert_cards(cards_df: pd.DataFrame):        
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
    def downloaded_cards():
        conn = PostgresQL._get_alq_engine().connect() 
        result = pd.read_sql_query("SELECT id, set FROM data.cards", con=conn)
        conn.close()
        return result
    
    # Frontend methods -----------------------------------------------
    
    @staticmethod
    def search_cards(search_str: str, target: str, count: str):        
        # Prepare query based on parameters
        if target in ["name", "artist"]:
            query = f"""
            CREATE EXTENSION IF NOT EXISTS pg_trgm;
            SELECT id, name, type, mana_cost, set, img, SIMILARITY({target}, %s) AS sim FROM data.cards WHERE name != 'ERROR!' ORDER BY sim DESC LIMIT %s;
            """
        
        if target == "text":
            search_str = f"%{search_str}%"
            query = f"""SELECT id, name, type, mana_cost, set, img, '1.0' AS sim FROM data.cards WHERE LOWER(text) LIKE LOWER(%s) AND name != 'ERROR!' LIMIT %s;"""
                
        # Execute query
        conn = PostgresQL._get_connection()
        cur = conn.cursor()
        cur.execute(query, (search_str, count))
        
        # Return as json object
        return [{
            "id": element[0],
            "name": element[1],
            "type": element[2],
            "mana_cost": element[3],
            "set": element[4],
            "img": element[5],
            "sim": element[6]
        } for element in cur.fetchall()]
    
    @staticmethod
    def get_card(id: int):
        # Execute query
        conn = PostgresQL._get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT * FROM data.cards WHERE id = %s LIMIT 1;""", (id, ))
        
        # Fetch element
        element = cur.fetchone()
        if element is None:
            return Response(response=f"No card with id = {id} was found", status=404)
        
        # Return as json object
        return {
            "id": element[0],
            "name": element[1],
            "type": element[2],
            "mana_val": element[3],
            "mana_cost": element[4],
            "set": element[5],
            "card_num": element[6],
            "artist": element[7],
            "text": element[8],
            "story": element[9],
            "url": element[10],
            "img": element[11]
        }
