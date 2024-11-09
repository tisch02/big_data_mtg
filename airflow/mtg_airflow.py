from datetime import datetime, timedelta
from airflow import DAG

import requests

from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.exceptions import AirflowException

args = {
    'owner': 'airflow'
}

dag = DAG('MTG_Crawler', 
          default_args=args, 
          description='Crawling and providing MTG card information',
          schedule_interval='*/1 * * * *',
          start_date=datetime(2019, 10, 16), 
          catchup=False,
          dagrun_timeout=timedelta(minutes=1),
          max_active_runs=1)

# Operators ---------------------------------------------------------------------
hello_world = BashOperator(
    task_id='run_after_loop',
    bash_command='curl https://localhost:38383',
    dag=dag
)

hello_world