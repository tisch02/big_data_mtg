from datetime import datetime
from airflow import DAG

from airflow.operators.python_operator import PythonOperator
from airflow.decorators import task
from airflow import AirflowException

args = {
    'owner': 'airflow'
}

# Functions ---------------------------------------------------------------------

@task(task_id="check_connection_op")
def check_connection():
    raise AirflowException('Connection not available.')

# Operators ---------------------------------------------------------------------

dag = DAG('MTG_Crawler', 
          default_args=args, 
          description='Crawling and providing MTG card information',
          schedule_interval='*/5 * * * *',
          start_date=datetime(2019, 10, 16), 
          catchup=False, 
          max_active_runs=1)

run_this = check_connection()