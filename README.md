# Big Data MTG Crawler

For task and lecture reference, see: [GitHub Repo](https://github.com/marcelmittelstaedt/BigData/)

## Documentation

As presented in the image below, the whole project is composed of five docker container. Each has its own job:

- The **PostgreSQL container** container contains the end-user database.
- The **Flaks (Frontend) container** functions as a webserver for the web UI and provides a REST API to fetch data from the end-user database.
- The **Hadoop/Hive** container contains raw data that is donwloaded or provides in ETL process.
- The **Flask (Backend) container** exposes a REST API that serves differen purposes. The main task is to parse (donwloaded) HTML pages and extract their information. Additionally, some tasks interact with the end-user database and the Hadoop/Hive container.
- The **Airflow container** manages the whole ETL workflow and trigger actions regarding the Flask (Backend) container, the Hadoop/Hive container and own PySpark transformations.

![image docker structure](./static/img/container_structure.png)

Why use a seperate **Flask (Backend) container** event though the **Airflow container** runs Python as well?

- Airflow runs on the Python version 2.7., which is deprecated since January 2020. To still use up-to-date python packages, the **Flaks (Backend) container** is added, that runs on Python 3.12.

### ETL Explanation

The ETL workflow runs every 10 minutes. With every run, 10 more cards are added to the end-user database which is accessable via the web UI.

### Aiflow DAG overview

Due to the educational purpose, different steps use different techniques, even though all could have been implemented using the same procedure.

#### Backend API

> `/api/test` \
> Tests the PostgrSQL and Hive connection.
>
> **Returns**
>
> - **200**: PostgreSQL and Hive version.
> - **400**: An error occured during the operation.

> `/api/postgres-create` \
> Creates all needed PostgreSQL tables if the don't exist.
>
> **Returns**
>
> - **200**: Queries for creating the tables were successful
> - **400**: An error occured during the operation.

> `/api/store-set-names` \
> Takes the downloaded .html and extracts a list of all set names.
> The list is stored to the PostgreSQL database. Existing elements
> are not overwritten. New elements will be appended
>
> **Returns**
>
> - **200**: Returns a string indicating the number of strings
> that were added to the PostgreSQL
> - **400**: An error occured during the operation.

> `/api/get-set-ids` \
> Gets a set name from the PostgreSQL that is marked as not downloaded.
> Then, it scrapes a list of all card ids from MTG Gatherer.
> These ids are then returned as a tsv.
>
> **Returns**
>
> - **200**: Returns a tsv list with all ids for a given set.
> - **400**: An error occured during the operation.

> `/api/mark-stored-sets` \
> Quries a distinc list of set names which card ids are scraped.
> For each set in this list, the corresponding PostgreSQL entry is also
> markd as downloaded.
>
> **Returns**
>
> - **200**: Returns a comma seperated list of all downloaded set names.
> - **400**: An error occured during the operation.

> `/api/download-cards` \
> Retrieves the list of cards that should be downloaded via Hive.
> Then downloads all cards, extracts the information and
> stores it to the PostgreSQL database.
>
> **Returns**
>
> - **200**: Returns a string indicating the number of scraped cards.
> - **400**: An error occured during the operation.

> `/api/downloaded-cards` \
> Gets a list of all cards that are donwloaded into the PostgreSQL
>
> **Returns**
>
> - **200**: CSV text of all card ids with its set name.
> - **400**: An error occured during the operation.

TBD: List of endpoints

### Job/Transformation description

Explenation of all Airflow DAG steps:

- **create_download_dir** and **clear_download_dir**: Creates an directory in the local airflow filesytem (not HDFS), where downloaded files can be stored before they are moved to their final destination.
- **reate_hdfs_set_names_dir**: HDFS directory for storing a downloaded .html file. This file is later used to scrape a list of all available sets on MTG Gatherer.
- **create_hdfs_ids_dir** + **create_hive_table_ids**: HDFS directory with matching Hive table that contains .tsv files. They hold a list of 
- **reate_hdfs_to_download_dir** + **create_hive_to_download_ids**: 
- **create_hdfs_downloaded_dir** + **create_hive_downloaded_ids**:


### Frontend

#### Frontend API

### Files

All files are present in this repository. When setting up the project, those are provided to the containers by mounting the directories.

- The used Aiflow DAG: `airflow/mtg_airflow.py`
- The PySpark transformation: `pyspark/pyspark_prepare_download.py`
- The DDLs for PostgresQL and HIVE: `ddl/*.sql`. Except for the `ddl/postgres_setup.sql` file, none of those files has to be executed manually.

## Setup and startup

To **setup the project** for the first time, follow and execute the steps listed in `scripts/setup.sh`.

To **start the project** if it is already setup, follow and execute the steps listed in `scripts/startup.sh`.

To **reset the project**, just delte all docker containers and follow the setup instructions.

```bash
# Stop every running container
docker stop hadoop airflow python postgres frontend

# Remove all containers
docker rm hadoop airflow python postgres frontend

# Remove all images (optional)
docker rmi marcelmittelstaedt/spark_base:latest && docker rmi python:3.12.7-bookworm && docker rmi marcelmittelstaedt/airflow:latest && docker rmi postgres:latest
```

### Ports

If running the project, e.g. on a Google-Cloud VM, the following ports have to be exposed:

- 80 (443) for the Web-Frontend

### Get file from HDFS 
curl "http://34e0454c2314:9864/webhdfs/v1/user/hadoop/mtg/sets/set_names.html?op=OPEN&namenoderpcaddress=hadoop:9000&offset=0"
curl "http://34e0454c2314:9864/webhdfs/v1/user/hadoop/mtg/sets/set_names.html?op=OPEN&namenoderpcaddress=34.89.168.124:9000&offset=0"


part-00000-79b743d4-4a38-40d4-b237-2ba3db29778c-c000.csv
curl "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/todownload/_SUCCESS?op=OPEN&namenoderpcaddress=hadoop:9000"
curl "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/todownload/part-00000-79b743d4-4a38-40d4-b237-2ba3db29778c-c000.csv?op=OPEN&namenoderpcaddress=hadoop:9000"
curl "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/todownload/part-00001-79b743d4-4a38-40d4-b237-2ba3db29778c-c000.csv?op=OPEN&namenoderpcaddress=hadoop:9000"
curl "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/todownload/part-00002-79b743d4-4a38-40d4-b237-2ba3db29778c-c000.csv?op=OPEN&namenoderpcaddress=hadoop:9000"
curl "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/todownload/part-00003-79b743d4-4a38-40d4-b237-2ba3db29778c-c000.csv?op=OPEN&namenoderpcaddress=hadoop:9000"


curl "http://35.198.76.213:9864/webhdfs/v1/user/hadoop/mtg/sets/set_names.html?op=OPEN&namenoderpcaddress=35.198.76.213:9000"

http://34.89.168.124/
curl -i -X PUT "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/sets/test.txt?op=CREATE&namenoderpcaddress=hadoop:9000"

curl -i -X PUT "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=CREATE
                    [&overwrite=<true|false>][&blocksize=<LONG>][&replication=<SHORT>]
                    [&permission=<OCTAL>][&buffersize=<INT>]"


curl -i -X DELETE http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/ids/set_ids_230cd64a-88fc-4ef6-a531-e2edcae528d3.tsv?user.name=hadoop&op=DELETE&recursive=true&namenoderpcaddress=hadoop:9000
curl -i -X PUT    "http://hadoop:9864/webhdfs/v1/user/hadoop/mtg/sets/test.txt?op=CREATE&namenoderpcaddress=hadoop:9000"

curl -X GET "http://35.198.76.213:9864/webhdfs/v1/user/hadoop/mtg/todownload?op=LISTSTATUS&recursive=true"
curl -X GET "http://erie1.example.com:50070/webhdfs/v1/user/admin?op=LISTSTATUS&recursive=true"




    