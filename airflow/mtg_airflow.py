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
          schedule_interval='*/5 * * * *',
          start_date=datetime(2019, 10, 16), 
          catchup=False,
          dagrun_timeout=timedelta(minutes=1),
          max_active_runs=1)

# Functions ---------------------------------------------------------------------

def check_connection():
    result = requests.get('http://localhost:38383').text
    return result

# Operators ---------------------------------------------------------------------
run_this = BashOperator(
    task_id='run_after_loop',
    bash_command='echo 1',
    dag=dag
)

check_connection_op = PythonOperator(
    task_id="check_connection",
    python_callable=check_connection,
    dag=dag
)



run_this >> check_connection_op