import sys
from datetime import datetime

from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from airflow.hooks.base import BaseHook


if __name__ == '__main__':        
    
    # get API data for an specific day
    if len(sys.argv) == 1:
        raise Exception("Missing execution date parameter")

    pg_connection_info = BaseHook.get_connection('postgres_de_challenge')

    execution_date = datetime.strptime(sys.argv[1],'%Y-%m-%d')
    execution_date_yearmonth_str = execution_date.strftime('%Y-%m-01')

    spark = SparkSession(SparkContext(conf=SparkConf()).getOrCreate())
    
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
    output_path = f"s3a://de-challenge/invoice_by_business"
    result_df.write.mode("overwrite").partitionBy(partition_cols).parquet(output_path)

    # Stop SparkSession
    spark.stop()
