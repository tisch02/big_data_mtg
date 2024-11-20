#! /bin/bash
# This file should not be run. Each line should be executed one by one, by hand.

# Start container
docker start hadoop airflow python postgres frontend

# Start processes inside the containers
docker exec -it python bash -c "cd /home/shared/big_data_mtg && python flask_app.py"
# Leave container

docker exec -it frontend bash -c "cd /home/shared/big_data_mtg && python flask_frontend.py"
# Leave container

docker exec -it hadoop bash -c "sudo su hadoop && cd"
start-all.sh
hiveserver2
