docker start hadoop airflow python postgres
docker exec -it hadoop bash -c "sudo su hadoop && cd"
    start-all.sh
    hiveserver2

# Exit cotainer with