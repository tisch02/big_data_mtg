#! /bin/bash


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

# ----------------------
docker run -dit --name airflow -p 8080:8080 --net bigdatanet -v ~/shared/big_data_mtg/airflow:/home/airflow/airflow/dags marcelmittelstaedt/airflow:latest

docker exec -it airflow bash
sudo su airflow
cd

# http://34.89.168.124:8080/admin/

# ---------------------
docker run -dit --name python \
    -p 38383:38383 \
    --net bigdatanet \
    -v ~/shared:/home/shared \
    python:3.12.7-bookworm

docker exec -it python sh -c "cd /home/shared/big_data_mtg && python -m pip install -r requirements.txt && python flask_app.py"

# PostgresQL
docker run -dit --name postgres -p 5432:5432 --net bigdatanet -e POSTGRES_PASSWORD=root postgres:latest
docker exec -it postgres bash -c "psql -h localhost -p 5432 -U postgres"
psql -h localhost -p 5432 -U postgres

CREATE DATABASE mtg

ALTER USER app with encrypted password 'app';
GRANT ALL privileges on database mtg to app;

CREATE USER big_data WITH ENCRYPTED PASSWORD 'big_data';
GRANT ALL PRIVILEGES ON DATABASE mtg TO big_data;