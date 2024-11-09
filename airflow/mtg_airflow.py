from datetime import datetime
from airflow import DAG

from airflow.operators.python_operator import PythonOperator
from airflow.exceptions import AirflowException

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

# Functions ---------------------------------------------------------------------

def check_connection():
    return "Hallo, Welt!"

# Operators ---------------------------------------------------------------------
check_connection_op = PythonOperator(
    task_id="check_connection",
    python_callable=check_connection,
    dag=dag
)

check_connection_op