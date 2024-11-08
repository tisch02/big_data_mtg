
# TODO: Allo http/https traffic for VM
# Configure Port 8080 in Firewall http configuration

# Remove old
docker rm hadoop
docker rm airflow

# Preperation
docker network create -d bridge bigdatanet

docker pull marcelmittelstaedt/spark_base:latest
docker pull marcelmittelstaedt/airflow:latest
docker pull python:3.12.7-bookworm

docker run -dit --name hadoop \
    -p 8088:8088 -p 9870:9870 -p 9864:9864 -p 10000:10000 \
    -p 8032:8032 -p 8030:8030 -p 8031:8031 -p 9000:9000 \
    -p 8888:8888 --net bigdatanet \
    marcelmittelstaedt/spark_base:latest

docker exec -it hadoop bash

sudo su hadoop
cd
start-all.sh
hiveserver2

# ----------------------
docker run -dit --name airflow \
    -p 8080:8080 \
    --net bigdatanet \
    marcelmittelstaedt/airflow:latest

docker exec -it airflow bash
sudo su airflow
cd

# http://34.89.242.208:8080/admin/

# ---------------------
docker run -dit --name python \
    -p 38383:38383 \
    --net bigdatanet \
    python:3.12.7-bookworm

docker exec -it python bash



