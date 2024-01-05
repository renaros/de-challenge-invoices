#!/usr/bin/env python
"""
This script is just to demonstrate a how to consume data from the topic in Kafka
Usage: python3 ./streaming/invoice_consumer.py (assuming that you are on the root folder of the project)
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, from_unixtime, col
from pyspark.sql.types import StringType, StructField, StructType, IntegerType, LongType


## Start a Spark session
spark = SparkSession \
    .builder \
    .appName("KafkaConsumer") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0') \
    .master("local[*]") \
    .getOrCreate()

# Read stream as a dataframe
df = spark.readStream\
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "postgres.public.invoices") \
    .option("startingOffsets", "earliest") \
    .load()

# Set the schema to convert json message into correct datatypes
json_schema = StructType([
        StructField('payload', StructType([
            StructField('after', StructType([
                StructField('invoice_id', IntegerType(), True), \
                StructField('issue_date', LongType(), True), \
                StructField('issuer_id', IntegerType(), True), \
                StructField('receiver_id', IntegerType(), True), \
                StructField('amount_usd', StringType(), True)
            ]))
        ]))
    ])

# Convert some values and keep only relevant columns
df = df.withColumn("value_string", df["value"].cast("string"))
df = df.withColumn("value_parsed", from_json(df["value_string"], json_schema)).select("value_parsed.*")
df = df \
    .withColumn('issue_date_converted', from_unixtime(col("payload.after.issue_date")/1000000)) \
    .select(
        "payload.after.invoice_id", 
        col("payload.after.issue_date").alias('issue_date_unixts'),
        "issue_date_converted",
        "payload.after.issuer_id", 
        "payload.after.receiver_id", 
        "payload.after.amount_usd"
    )

# Write the output to console sink to check the output
writing_df = df.writeStream \
    .format("console") \
    .outputMode("append") \
    .start()
    
# Start the streaming application to run until the following happens
writing_df.awaitTermination()