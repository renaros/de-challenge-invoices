#!/usr/bin/env python
"""
This DAG is responsible for reading data from invoices table and transforming the information into parquet files in MinIO.
"""
from datetime import datetime, timedelta

# from pyspark.sql import SparkSession
from airflow.decorators import dag, task
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

    # @task
    # def query_source_table(**context):
    #     """
    #     Function responsible for querying Postgres and generating parquet files
    #     I'm performing all operations on the same file because it's simple and not being used anywhere else,
    #     but ideally we should separate this into a separate pyspark script and run it through SparkOperator.
    #     """

    #     # uses execution date in case we want to backfill previous months
    #     execution_date = datetime.strptime(context['ds'], '%Y-%m-%d')
    #     execution_date_yearmonth_str = execution_date.strftime("%Y-%m-01")

    #     # get postgres information from airflow connection (more secure)
    #     pg_connection_info = BaseHook.get_connection('postgres_de_challenge')
    #     minio_connection_info = BaseHook.get_connection('minio_de_challenge')
        
    #     spark = SparkSession.builder \
    #             .appName("PostgresToMinIO") \
    #             .config("spark.jars.packages", "org.postgresql:postgresql:42.2.24,org.apache.hadoop:hadoop-aws:3.3.4") \
    #             .config("spark.hadoop.fs.s3a.access.key", minio_connection_info.login) \
    #             .config("spark.hadoop.fs.s3a.secret.key", minio_connection_info.password) \
    #             .config("spark.hadoop.fs.s3a.endpoint", f"http://{minio_connection_info.host}:{minio_connection_info.port}") \
    #             .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    #             .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    #             .getOrCreate()

    #     # Get data from source table and store on a PySpark dataframe to be saved in MinIO
    #     query = f"""
    #         with issuers as (
    #             select 	issuer_id as business_id, 
    #                     date_trunc('month', issue_date) as issue_date_yearmonth, 
    #                     sum(amount_usd) as total_amount_issued
    #             from public.invoices
    #             where date_trunc('month', issue_date) = '{execution_date_yearmonth_str}'
    #             group by 1,2
    #         ),
    #         receivers as (
    #             select 	receiver_id as business_id, 
    #                     date_trunc('month', issue_date) as issue_date_yearmonth, 
    #                     sum(amount_usd) as total_amount_received
    #             from public.invoices
    #             where date_trunc('month', issue_date) = '{execution_date_yearmonth_str}'
    #             group by 1,2
    #         )
    #         select 	coalesce(i.business_id, r.business_id) as business_id,
    #                 coalesce(i.issue_date_yearmonth, r.issue_date_yearmonth) as issue_date_yearmonth,
    #                 coalesce(i.total_amount_issued, 0) as total_amount_issued,
    #                 coalesce(r.total_amount_received, 0) as total_amount_received
    #         from issuers i
    #         full join receivers r on i.business_id = r.business_id and i.issue_date_yearmonth = r.issue_date_yearmonth
    #     """
    #     result_df = spark.read \
    #                 .format("jdbc") \
    #                 .option("url", f"jdbc:postgresql://{pg_connection_info.host}:{pg_connection_info.port}/{pg_connection_info.schema}") \
    #                 .option("driver", "org.postgresql.Driver") \
    #                 .option("query", query) \
    #                 .option("user", pg_connection_info.login) \
    #                 .option("password", pg_connection_info.password) \
    #                 .load()
        
    #     # Define partition columns
    #     partition_cols = ["issue_date_yearmonth"]

    #     # Write output to Parquet files in MinIO
    #     output_path = f"s3a://de-challenge/invoice_by_business/{execution_date_yearmonth_str}"
    #     result_df.write.partitionBy(partition_cols).parquet(output_path)

    #     # Stop SparkSession
    #     spark.stop()
    # query_source_table_task = query_source_table()

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
    # start_process_task >> query_source_table_task
    # query_source_table_task >> end_process_task

dag_invoice_by_business()
