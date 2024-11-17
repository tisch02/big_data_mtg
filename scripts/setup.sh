#! /bin/bash

# Clone repo
cd ~/ && mkdir shared && cd shared && git clone https://github.com/tisch02/big_data_mtg.git && cd big_data_mtg && git pull

# Create docker network and pull images
docker network create -d bridge bigdatanet && docker pull marcelmittelstaedt/spark_base:latest && docker pull python:3.12.7-bookworm && docker pull marcelmittelstaedt/airflow:latest && docker pull postgres:latest

# Create all containers
docker run -dit --name hadoop -p 8088:8088 -p 9870:9870 -p 9864:9864 -p 10000:10000 -p 8032:8032 -p 8030:8030 -p 8031:8031 -p 9000:9000 -p 8888:8888 --net bigdatanet marcelmittelstaedt/spark_base:latest && docker run -dit --name airflow -p 8080:8080 --net bigdatanet -v ~/shared/big_data_mtg/airflow:/home/airflow/airflow/dags -v ~/shared/big_data_mtg/pyspark:/home/airflow/airflow/python marcelmittelstaedt/airflow:latest && docker run -dit --name python -p 38383:38383 --net bigdatanet -v ~/shared:/home/shared python:3.12.7-bookworm && docker run -dit --name postgres -p 5432:5432 --net bigdatanet -e POSTGRES_PASSWORD=root postgres:latest && docker run -dit --name frontend -p 80:80 -p 443:443 --net bigdatanet -v ~/shared:/home/shared python:3.12.7-bookworm

# Configure user in postgres database by running the following steps after each other
docker exec -it postgres bash -c "psql -h localhost -p 5432 -U postgres"
CREATE DATABASE mtg; CREATE USER big_data WITH ENCRYPTED PASSWORD 'big_data'; GRANT ALL PRIVILEGES ON DATABASE mtg TO big_data; CREATE EXTENSION pg_trgm;
exit

# Install python container and run flask app
docker exec -it python bash -c "cd /home/shared/big_data_mtg && python -m pip install --upgrade pip && python -m pip install -r requirements.txt && python flask_app.py"
# Leave container with: STRG + p and STRG + q

docker exec -it frontend bash -c "cd /home/shared/big_data_mtg && python -m pip install --upgrade pip && python -m pip install -r requirements.txt && python flask_frontend.py"
# Leave container with: STRG + p and STRG + q

# Start hadoop and hive
docker exec -it hadoop bash -c "sudo su hadoop && cd"
start-all.sh 
hiveserver2


# --------------------


# TODO: Allo http/https traffic for VM
# Configure Port 8080 in Firewall http configuration

# Clon GitHub
cd ~/
mkdir shared
cd shared
git clone https://github.com/tisch02/big_data_mtg.git
cd big_data_mtg
git pull


# Remove old
docker rm hadoop
docker rm airflow
docker rm python

# Preperation
docker network create -d bridge bigdatanet

docker pull marcelmittelstaedt/spark_base:latest
docker pull python:3.12.7-bookworm
docker pull marcelmittelstaedt/airflow:latest
docker pull postgres:latest

docker run -dit --name hadoop -p 8088:8088 -p 9870:9870 -p 9864:9864 -p 10000:10000 -p 8032:8032 -p 8030:8030 -p 8031:8031 -p 9000:9000 -p 8888:8888 --net bigdatanet marcelmittelstaedt/spark_base:latest

docker exec -it hadoop bash -c "sudo su hadoop && cd && start-all.sh && hiveserver2"
# http://35.198.76.213:9870

# ----------------------
docker run -dit --name airflow -p 8080:8080 --net bigdatanet -v ~/shared/big_data_mtg/airflow:/home/airflow/airflow/dags -v ~/shared/big_data_mtg/pyspark:/home/airflow/airflow/python marcelmittelstaedt/airflow:latest

docker exec -it airflow bash

cd /home/airflow/airflow/logs/MTG_Crawler/pyspark_prepare_download

# http://35.198.76.213:8080/admin/

# ---------------------
docker run -dit --name python -p 38383:38383 --net bigdatanet -v ~/shared:/home/shared python:3.12.7-bookworm

docker exec -it python bash -c "cd /home/shared/big_data_mtg && python -m pip install -r requirements.txt && python flask_app.py"

# PostgresQL
docker run -dit --name postgres -p 5432:5432 --net bigdatanet -e POSTGRES_PASSWORD=root postgres:latest
docker exec -it postgres bash -c "psql -h localhost -p 5432 -U postgres"

psql -h localhost -p 5432 -U postgres

CREATE DATABASE mtg

CREATE USER big_data WITH ENCRYPTED PASSWORD 'big_data';
GRANT ALL PRIVILEGES ON DATABASE mtg TO big_data;

# ------------------------

docker run -dit --name frontend -p 80:80 -p 443:443 --net bigdatanet -v ~/shared:/home/shared python:3.12.7-bookworm