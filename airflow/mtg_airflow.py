from datetime import datetime
from airflow import DAG

args = {
    'owner': 'airflow'
}

dag = DAG('MTG_Crawler', 
          default_args=args, 
          description='Crawling and providing MTG card information',
          schedule_interval='*/5 * * * *',
          start_date=datetime(2019, 10, 16), 
          catchup=False, 
          max_active_runs=1)