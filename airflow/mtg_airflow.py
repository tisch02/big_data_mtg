import uuid

from datetime import datetime, timedelta
from airflow import DAG

from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.operators.dummy_operator import DummyOperator
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
          schedule_interval='*/10 * * * *',
          start_date=datetime(2019, 10, 16), 
          catchup=False,
          dagrun_timeout=timedelta(minutes=9),
          max_active_runs=1)

download_id = str(uuid.uuid4())

# HiveQL queries ----------------------------------------------------------------

hql_create_ids_list = """
CREATE EXTERNAL TABLE IF NOT EXISTS ids(	
    id INT,
    insert_date STRING,
    set_name STRING
) COMMENT 'Card IDs that should be downloaded' ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\t' STORED AS TEXTFILE LOCATION '/user/hadoop/mtg/ids' TBLPROPERTIES ('skip.header.line.count'='1');
"""

hql_to_download_ids = """
CREATE EXTERNAL TABLE IF NOT EXISTS todownload(	
    id INT,    
    set_name STRING
) COMMENT 'Card IDs that are ready for download' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hadoop/mtg/todownload' TBLPROPERTIES ('skip.header.line.count'='1');
"""

hql_downloaded_ids = """
CREATE EXTERNAL TABLE IF NOT EXISTS downloaded(	
    id INT,    
    set_name STRING
) COMMENT 'Card IDs that are already downloaded' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hadoop/mtg/downloaded' TBLPROPERTIES ('skip.header.line.count'='1');
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

# Download

download_set_names = HttpDownloadOperator(
    task_id='download_set_names',
    download_uri='https://gatherer.wizards.com/pages/Default.aspx',
    save_to='/home/airflow/downloads/set_names.html',
    dag=dag,
)

download_set_ids = HttpDownloadOperator(
    task_id='download_set_ids',
    download_uri='http://python:38383/api/get-set-ids',
    save_to=f'/home/airflow/downloads/set_ids.tsv',
    dag=dag,
)

download_downloaded_cards = HttpDownloadOperator(
    task_id='download_downloaded_cards',
    download_uri='http://python:38383/api/downloaded-cards',
    save_to=f'/home/airflow/downloads/downloaded_cards.csv',
    dag=dag,
)

download_to_download_ids = HttpDownloadOperator(
    task_id='download_to_download_ids',
    download_uri='http://python:38383/api/get-to-download-ids?count=20',
    save_to=f'/home/airflow/downloads/to_download.csv',
    dag=dag,
)

# HDFS Mkdir

create_hdfs_set_names_dir = HdfsMkdirFileOperator(
    task_id='create_hdfs_set_names_dir',
    directory='/user/hadoop/mtg/sets',
    hdfs_conn_id='hdfs',
    dag=dag,
)

create_hdfs_ids_dir = HdfsMkdirFileOperator(
    task_id='create_hdfs_ids_dir',
    directory='/user/hadoop/mtg/ids',
    hdfs_conn_id='hdfs',
    dag=dag,
)

create_hdfs_to_download_dir = HdfsMkdirFileOperator(
    task_id='create_hdfs_to_download_dir',
    directory='/user/hadoop/mtg/todownload',
    hdfs_conn_id='hdfs',
    dag=dag,
)

create_hdfs_downloaded_dir = HdfsMkdirFileOperator(
    task_id='create_hdfs_downloaded_dir',
    directory='/user/hadoop/mtg/downloaded',
    hdfs_conn_id='hdfs',
    dag=dag,
)

# HDFS Put

hdfs_put_set_names_file = HdfsPutFileOperator(
    task_id='hdfs_put_set_names_file',
    local_file='/home/airflow/downloads/set_names.html',
    remote_file='/user/hadoop/mtg/sets/set_names.html',
    hdfs_conn_id='hdfs',
    dag=dag,
)

hdfs_put_ids_file = HdfsPutFileOperator(
    task_id='hdfs_put_ids_file',
    local_file=f'/home/airflow/downloads/set_ids.tsv',
    remote_file=f'/user/hadoop/mtg/ids/set_ids_{download_id}.tsv',
    hdfs_conn_id='hdfs',
    dag=dag,
)

hdfs_put_downloaded_cards_file = HdfsPutFileOperator(
    task_id='hdfs_put_downloaded_cards_file',
    local_file=f'/home/airflow/downloads/downloaded_cards.csv',
    remote_file=f'/user/hadoop/mtg/downloaded/cards.csv',
    hdfs_conn_id='hdfs',
    dag=dag,
)

hdfs_put_to_download_ids_file = HdfsPutFileOperator(
    task_id='hdfs_put_to_download_ids_file',
    local_file=f'/home/airflow/downloads/to_download.csv',
    remote_file=f'/user/hadoop/mtg/todownload/to_download.csv',
    hdfs_conn_id='hdfs',
    dag=dag,
)

# Bash / curl

postgres_create = BashOperator(
    task_id='postgres_create',
    bash_command='curl http://python:38383/api/postgres-create',
    dag=dag
)

store_set_names = BashOperator(
    task_id='store_set_names',
    bash_command='curl http://python:38383/api/store-set-names',
    dag=dag
)

mark_downloaded_set_ids = BashOperator(
    task_id='mark_downloaded_set_ids',
    bash_command='curl http://python:38383/api/mark-stored-sets',
    dag=dag
)

download_cards = BashOperator(
    task_id='download_cards',
    bash_command='curl http://python:38383/api/download-cards',
    dag=dag
)

# Hive

create_hive_table_ids = HiveOperator(
    task_id='create_hive_table_ids',
    hql=hql_create_ids_list,
    hive_cli_conn_id='beeline',
    dag=dag
)

create_hive_table_to_download = HiveOperator(
    task_id='create_hive_table_to_download',
    hql=hql_to_download_ids,
    hive_cli_conn_id='beeline',
    dag=dag
)

create_hive_table_downloaded = HiveOperator(
    task_id='create_hive_table_downloaded',
    hql=hql_downloaded_ids,
    hive_cli_conn_id='beeline',
    dag=dag
)

# Spark

# pyspark_prepare_download = SparkSubmitOperator(
#     task_id='pyspark_prepare_download',
#     conn_id='spark',
#     application='/home/airflow/airflow/python/pyspark_prepare_download.py',        
#     executor_memory='3g',
#     num_executors='4',
#     name='spark_prepare_download',
#     verbose=True,
#     application_args=['--hdfs_source_dir', '/user/hadoop/mtg', '--hdfs_target_dir', '/user/hadoop/mtg/todownload', '--count', '10'],
#     dag = dag
# )

# Others

dummy_split = DummyOperator(
    task_id='dummy_split', 
    dag=dag
)

dummy_collect = DummyOperator(
    task_id='dummy_collect', 
    dag=dag
)

# Flow -------------------------------------------------------------

[
    create_download_dir >> clear_download_dir,
    create_hdfs_set_names_dir,
    create_hdfs_ids_dir >> create_hive_table_ids,
    create_hdfs_to_download_dir >> create_hive_table_to_download,
    create_hdfs_downloaded_dir >> create_hive_table_downloaded,
    postgres_create
] >> dummy_split

dummy_split >> download_set_names >> hdfs_put_set_names_file >> store_set_names >> mark_downloaded_set_ids >> download_set_ids >> hdfs_put_ids_file >> dummy_collect
dummy_split >> download_downloaded_cards >> hdfs_put_downloaded_cards_file >> dummy_collect

# dummy_collect >> pyspark_prepare_download >> download_cards
dummy_collect >> download_to_download_ids >> hdfs_put_to_download_ids_file >> download_cards
