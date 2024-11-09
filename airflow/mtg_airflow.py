from datetime import datetime
from airflow import DAG

from airflow.operators.python_operator import PythonOperator
from airflow import AirflowException

args = {
    'owner': 'airflow'
}

# Functions ---------------------------------------------------------------------

def check_connection():
    raise AirflowException('Connection not available.')

# Operators ---------------------------------------------------------------------
check_connection_op = PythonOperator(
    task_id="check_connection",
    python_callable=check_connection
)


dag = DAG('MTG_Crawler', 
          default_args=args, 
          description='Crawling and providing MTG card information',
          schedule_interval='*/5 * * * *',
          start_date=datetime(2019, 10, 16), 
          catchup=False, 
          max_active_runs=1)

check_connection_op