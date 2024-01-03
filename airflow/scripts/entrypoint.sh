#!/usr/bin/env bash
# pip install pyspark
# apt install default-jdk

airflow db init
airflow db upgrade

airflow users create -e admin@admin.com -f admin -l admin -p admin -r Admin -u admin 

airflow webserver
