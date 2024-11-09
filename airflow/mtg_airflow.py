from datetime import datetime, timedelta
from airflow import DAG

import requests

from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.exceptions import AirflowException
from airflow.operators.filesystem_operations import CreateDirectoryOperator, ClearDirectoryOperator
from airflow.operators.http_download_operations import HttpDownloadOperator

args = {
    'owner': 'airflow'
}

dag = DAG('MTG_Crawler', 
          default_args=args, 
          description='Crawling and providing MTG card information',
          schedule_interval='*/2 * * * *',
          start_date=datetime(2019, 10, 16), 
          catchup=False,
          dagrun_timeout=timedelta(minutes=1),
          max_active_runs=1)

# Operators ---------------------------------------------------------------------
create_download_dir = CreateDirectoryOperator(
    task_id='create_download_dir',
    path='/home/airflow',
    directory='downloads',
    dag=dag,
)

clear_download_dir = ClearDirectoryOperator(
    task_id='clear_download_dir',
    directory='/home/airflow/downloads',
    pattern='*',
    dag=dag,
)

download_set_names = HttpDownloadOperator(
    task_id='download_set_names',
    download_uri='https://gatherer.wizards.com/pages/Default.aspx',
    save_to='/home/airflow/downloads/set_names.html',
    dag=dag,
)

create_hdfs_set_names_dir = HdfsMkdirFileOperator(
    task_id='create_hdfs_set_names_dir',
    directory='/user/hadoop/mtg/sets',
    hdfs_conn_id='hdfs',
    dag=dag,
)

hdfs_put_set_names_file = HdfsPutFileOperator(
    task_id='hdfs_put_set_names_file',
    local_file='/home/airflow/downloads/set_names.html',
    remote_file='/user/hadoop/mtg/sets/set_names.html',
    hdfs_conn_id='hdfs',
    dag=dag,
)

hello_world = BashOperator(
    task_id='hello_world',
    bash_command='curl http://python:38383/',
    dag=dag
)

hello_world >> create_download_dir >> clear_download_dir >> download_set_names >> create_hdfs_set_names_dir >> hdfs_put_set_names_file