from datetime import datetime, timedelta
from airflow import DAG

from airflow.operators.bash_operator import BashOperator
from airflow.operators.filesystem_operations import CreateDirectoryOperator, ClearDirectoryOperator
from airflow.operators.hdfs_operations import HdfsPutFileOperator, HdfsMkdirFileOperator
from airflow.operators.http_download_operations import HttpDownloadOperator
from airflow.operators.hive_operator import HiveOperator

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

# HiveQL queries ----------------------------------------------------------------

hql_create_ids_list = """
CREATE TABLE IF NOT EXISTS ids(
    set_name STRING,
	url STRING,
    id INT,
    insert STRING
) PARTITIONED BY (set_name) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hadoop/mtg/ids';
"""

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

create_hdfs_ids_dir = HdfsMkdirFileOperator(
    task_id='create_hdfs_set_names_dir',
    directory='/user/hadoop/mtg/ids',
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

postgres_create = BashOperator(
    task_id='postgres_create',
    bash_command='curl http://python:38383/api/postgres-create',
    dag=dag
)

store_set_names = BashOperator(
    task_id='store_set_names',
    bash_command='curl http://python:38383/api/set-names',
    dag=dag
)

create_hive_table_ids = HiveOperator(
    task_id='create_title_ratings_table',
    hql=hql_create_ids_list,
    hive_cli_conn_id='beeline',
    dag=dag)

set_names_flow = create_download_dir >> clear_download_dir >> download_set_names >> create_hdfs_set_names_dir >> hdfs_put_set_names_file
ids_flow = create_hdfs_ids_dir >> create_hive_table_ids

[set_names_flow, postgres_create, ids_flow] >> store_set_names