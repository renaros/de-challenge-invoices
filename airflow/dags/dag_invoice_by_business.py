from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.dummy_operator import DummyOperator
from pyspark.sql import SparkSession
from pyspark.sql.functions import year, month


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

@dag(schedule=None, default_args=default_args, catchup=False, tags=["challenge", "invoices"])
def dag_invoice_by_business():

    start_process_task = DummyOperator(
        task_id="start_process"
    )

    @task
    def query_source_table():
        spark = SparkSession.builder \
                .appName("PostgresToMinIO") \
                .config("spark.jars.packages", "org.postgresql:postgresql:42.2.24") \
                .config("spark.hadoop.fs.s3a.access.key", "admin") \
                .config("spark.hadoop.fs.s3a.secret.key", "admin") \
                .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
                .config("spark.hadoop.fs.s3a.path.style.access", "true") \
                .getOrCreate()
        postgres_url = "jdbc:postgresql://postgres:5432/de_challenge"
        postgres_properties = {
            "user": "de_user",
            "password": "pg123",
            "driver": "org.postgresql.Driver"
        }

        invoices_df = spark.read.jdbc(url=postgres_url, table="invoices", properties=postgres_properties)

        result_df = invoices_df \
                    .withColumn("year_issue_date", year("issue_date")) \
                    .withColumn("month_issue_date", month("issue_date")) \
                    .groupBy("year_issue_date", "month_issue_date", "issuer_id") \
                    .count()
        
        # Define partition columns
        partition_cols = ["year_issue_date", "month_issue_date"]

        # Write output to Parquet files in MinIO
        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = "s3a://de-challenge/invoices_by_business/{date}".format(date=current_date)
        result_df.write.partitionBy(partition_cols).parquet(output_path)

        # Stop SparkSession
        spark.stop()

        
    query_source_table_task = query_source_table()

    end_process_task = DummyOperator(
        task_id="end_process"
    )

    start_process_task >> query_source_table_task
    query_source_table_task >> end_process_task

dag_invoice_by_business()
