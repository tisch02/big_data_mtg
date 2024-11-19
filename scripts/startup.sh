docker start hadoop airflow python postgres frontend
docker exec -it hadoop bash -c "sudo su hadoop && cd"
start-all.sh
hiveserver2

# Exit cotainer with

docker exec -it python bash -c "cd /home/shared/big_data_mtg && python flask_app.py"

docker exec -it frontend bash -c "cd /home/shared/big_data_mtg && python flask_frontend.py"