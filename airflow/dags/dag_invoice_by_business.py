import logging
from datetime import datetime, timedelta

from pyspark.sql import SparkSession
from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook
from airflow.operators.dummy_operator import DummyOperator


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
logger = logging.getLogger(__name__)

@dag(schedule=None, default_args=default_args, catchup=False, tags=["challenge", "invoices"])
def dag_invoice_by_business():

    start_process_task = DummyOperator(
        task_id="start_process"
    )

    @task
    def test():
        pg_connection_info = BaseHook.get_connection('postgres_de_challenge')
        logger.info(pg_connection_info.__dict__)
        minio_connection_info = BaseHook.get_connection('minio_de_challenge')
        logger.info(minio_connection_info.__dict__)
    test_task = test()

    @task
    def query_source_table(**context):

        # uses execution date in case we want to backfill previous months
        execution_date = datetime.strptime(context['ds'], '%Y-%m-%d')
        execution_date_yearmonth_str = execution_date.strftime("%Y-%m-01")

        # get postgres information from airflow connection (more secure)
        pg_connection_info = BaseHook.get_connection('postgres_de_challenge')
        minio_connection_info = BaseHook.get_connection('minio_de_challenge')
        
        spark = SparkSession.builder \
                .appName("PostgresToMinIO") \
                .config("spark.jars.packages", "org.postgresql:postgresql:42.2.24,org.apache.hadoop:hadoop-aws:3.3.4") \
                .config("spark.hadoop.fs.s3a.access.key", minio_connection_info.login) \
                .config("spark.hadoop.fs.s3a.secret.key", minio_connection_info.password) \
                .config("spark.hadoop.fs.s3a.endpoint", f"http://{minio_connection_info.host}:{minio_connection_info.port}") \
                .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
                .config("spark.hadoop.fs.s3a.path.style.access", "true") \
                .getOrCreate()

        # Get data from source table and store on a PySpark dataframe to be saved in MinIO
        query = f"""
            with issuers as (
                select 	issuer_id as business_id, 
                        date_trunc('month', issue_date) as issue_date_yearmonth, 
                        sum(amount_usd) as total_amount_issued
                from public.invoices
                where date_trunc('month', issue_date) = '{execution_date_yearmonth_str}'
                group by 1,2
            ),
            receivers as (
                select 	receiver_id as business_id, 
                        date_trunc('month', issue_date) as issue_date_yearmonth, 
                        sum(amount_usd) as total_amount_received
                from public.invoices
                where date_trunc('month', issue_date) = '{execution_date_yearmonth_str}'
                group by 1,2
            )
            select 	coalesce(i.business_id, r.business_id) as business_id,
                    coalesce(i.issue_date_yearmonth, r.issue_date_yearmonth) as issue_date_yearmonth,
                    coalesce(i.total_amount_issued, 0) as total_amount_issued,
                    coalesce(r.total_amount_received, 0) as total_amount_received
            from issuers i
            full join receivers r on i.business_id = r.business_id and i.issue_date_yearmonth = r.issue_date_yearmonth
        """
        result_df = spark.read \
                    .format("jdbc") \
                    .option("url", f"jdbc:postgresql://{pg_connection_info.host}:{pg_connection_info.port}/{pg_connection_info.schema}") \
                    .option("driver", "org.postgresql.Driver") \
                    .option("query", query) \
                    .option("user", pg_connection_info.login) \
                    .option("password", pg_connection_info.password) \
                    .load()
        
        # Define partition columns
        partition_cols = ["issue_date_yearmonth"]

        # Write output to Parquet files in MinIO
        output_path = f"s3a://de-challenge/invoice_by_business/{execution_date_yearmonth_str}"
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
