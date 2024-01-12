#!/usr/bin/env python
"""
This DAG is responsible for reading data from invoices table and transforming the information into parquet files in MinIO.
"""
from datetime import datetime, timedelta

# from pyspark.sql import SparkSession
from airflow.decorators import dag
from airflow.hooks.base import BaseHook
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator


default_args = {
    'owner': 'renaros',
    'depends_on_past': False,
    'start_date': datetime(2024,1,1),
    'email': ['rossi.renato@outlook.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5)
}
dag_documentation_md = "This DAG is responsible for reading data from invoices table and transforming the information into parquet files in MinIO."
minio_connection_info = BaseHook.get_connection('minio_de_challenge')

## DAG ##
@dag(schedule="@daily", default_args=default_args, catchup=False, doc_md=dag_documentation_md, tags=["challenge", "invoices"])

def dag_invoice_by_business():

    start_process_task = DummyOperator(
        task_id="start_process"
    )

    # docker exec -it airflow-webserver airflow tasks test dag_invoice_by_business invoice_by_business_etl '2023-11-01'
    invoice_by_business_etl_task = SparkSubmitOperator(
        task_id="invoice_by_business_etl",
        application="./dags/pyspark_scripts/invoice_by_business_etl.py",
        conn_id="spark_conn",
        application_args=["{{ds}}"],
        conf={
            "spark.driver.maxResultSize": "20g",
            "spark.hadoop.fs.s3a.access.key": minio_connection_info.login,
            "spark.hadoop.fs.s3a.secret.key": minio_connection_info.password,
            "spark.hadoop.fs.s3a.endpoint": f"http://{minio_connection_info.host}:{minio_connection_info.port}",
            "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
            "spark.hadoop.fs.s3a.path.style.access": "true"
        },
        packages="org.postgresql:postgresql:42.2.24,org.apache.hadoop:hadoop-aws:3.3.4"
    )

    end_process_task = DummyOperator(
        task_id="end_process"
    )

    # DAG workflow
    start_process_task >> invoice_by_business_etl_task >> end_process_task

dag_invoice_by_business()
