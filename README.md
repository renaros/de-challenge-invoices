# Data Engineering Challenge - Invoices
Repository for invoices - data engineering challenge.

## Sections
* [Problem statement](#problem-statement)
* [Use Cases](#use-cases)
    * [Use case 1: Consume one invoice by its ID](#use-case-1-consume-one-invoice-by-its-id)
    * [Use case 2: Group invoices for the last n months by business id (or customer id)](#use-case-2-group-invoices-for-the-last-n-months-by-business-id-or-customer-id)
    * [Use case 3: Join this table with other sources for analytics purposes](#use-case-3-join-this-table-with-other-sources-for-analytics-purposes-not-necessarily-structured-data)
    * [Use case 4: Execute a risk model whenever a new invoice is created](#use-case-4-execute-a-risk-model-whenever-a-new-invoice-is-created)
* [Solution Overview](#solution-overview)
    * [Code Structure](#code-structure)
    * [How to run the code](#how-to-run-the-code)
* [Challenges during development](#challenges-during-the-development)

## Problem Statement
This financial company facilitates client interactions through transactions, recorded in the system as invoices. 
These invoices are currently stored in a traditional transactional RDBMS table. However, the volume is growing rapidly, posing complexities in managing distinct use cases within the company.
The invoice table has the following attributes:
* _invoice id_: unique id by invoice.
* _issue date_: the date and time where the invoice was created.
* _issuer id_: customer id that sent the invoice.
* _receiver id_: customer id that received the invoice.
* _amount_: amount to be paid, in USD.

The challenge is to define an architecture that addresses scalability issues and cover all use cases listed below in the next section.
Key considerations include:
* The data source cannot be migrated to another technology in the short-term.
* Solution performance is very relevant.
* The information that needs to be joined with the source data is diverse and not necessarily structured.
* The proposed solution must be deployable and maintainable in the cloud, though not necessarily cloud-native.

## Use Cases
Some use cases for this table are:

### Use Case 1: Consume one invoice by its ID
Migrating the entire source data is not possible on the short-term, so the idea is to implement a 2 step approach:

#### Proposed Architecture
* _Short-term_: In this case, the fastest and easiest action would be to just index the table by invoice id. This way we can speed up the searches using the original architecture, without investing much effort. Additionally, we could implement a caching layer like Redis or Memcached to enhance performance by storing frequently accessed invoices in memory.
* _Medium/long-term_: Consider migrating this table to distributed database systems - such as Amazon DynamoDB - in order to have better scalability.

### Use Case 2: Group invoices for the last n months by business id (or customer id)
In this scenario, I am considering an analytics use case focused on updating statistics on a scheduled basis.

#### Proposed Architecture
Here I suggest an orchestrator like Airflow to run the jobs on a schedule, Spark for processing, MinIO (or S3) as the storage layer and Hive (or Redshift Spectrum) to query the output. 
The pipeline in Airflow would be responsible for:
* Querying the source table (that can be a replica to not impact the production table).
* Apply the necessary transformations (in my example I'm developing the logic directly in the query)
* Using PySpark the results are exported to parquet files and stored in MinIO, partitioned by month and business id. 
The advantage of this approach is that parquet files can be read by Redshift Spectrum for analytics purposes (ad-hoc analysis and dashboards).
Thinking in a cloud environment, the same result could be obtained using Airflow hosted on EC2 or AWS Glue for orchestration, Spark instances in AWS, S3 for storage and Redshift Spectrum for Data Lake / Warehousing (or its equivalent in other cloud providers).

### Use Case 3: Join this table with other sources for analytics purposes (not necessarily structured data)
I'm assuming other sources could use ETL processes to store information into a Redshift instance or using S3 to store unstructured data.

#### Proposed Architecture
As described before in use case 2, using files hosted in S3 with Redshift Spectrum and structured tables in Redshift allows us to join structured and unstructured tables together, making it possible to provide better insights from data.

### Use Case 4: Execute a risk model whenever a new invoice is created
The sooner we run risk models on the invoices, the better it is to prevent fraud and strange behaviors. Therefore, the best approach here would be using some kind of streaming near real time approach.

#### Proposed Architecture
The solution I developed is using a Kafka topic to manage the messages from invoice and Debezium for CDC (change data capture).
Using this approach we are able to stream each insert in the table and consume this information by executing an algorithm for the risk model.
There are some extra advantages with this approach, for example:
* Performing extra tasks besides running the risk model, such as notifying the client about status change or updating analytics KPIs near real time
* Can be easily hosted in the cloud, using Amazon MSK or alternatives such as Amazon Kinesis.
* Highly scalable and available

### Final architecture overview
Here is an overview about the proposed architecture:
![Proposed architecture](https://github.com/renaros/de-challenge-invoices/blob/main/readme_images/proposed-architecture.jpg)

## Solution Overview
The solution I developed in this repository aims to implement and be a proof of concept about some of the ideas proposed in the use cases section.

### Code Structure
* Environment related files:
    * [docker-compose.yaml](docker-compose.yaml): Main docker compose file, containing the setup for this environment.
    * [Dockerfile_Airflow](Dockerfile_Airflow) and [Dockerfile_Postgres](Dockerfile_Postgres): Dockerfiles to build images for Airflow and Postgres.
    * [.env.example](.env.example) and [./debezium/pg-source-config.json.example](debezium/pg-source-config.json.example): Configuration files for environment / Debezium. See the section [How to create the environment](#how-to-create-the-environment) for more information about how to use these files.
    * [./airflow/scripts/entrypoint.sh](airflow/scripts/entrypoint.sh): Bash script that runs on the Airflow container after it gets created, basically creates an admin user and starts the service.
    * [./postgres-scripts/sql/create_tables.sql](postgres-scripts/sql/create_tables.sql): SQL script that runs on Postgres right after the container gets created
* Data engineering related files:
    * [./airflow/dags/dag_invoice_by_business.py](airflow/dags/dag_invoice_by_business.py): DAG responsible for querying Postgres and generating parquet files in MinIO to be used in analytics.
    * [./streaming/invoice_consumer.py](streaming/invoice_consumer.py): Python script that simulates a consumer for data streamed in Kafka.

### How to Run the Code

#### Requirements:
* [Docker compose](https://docs.docker.com/compose/install/)
* [Python3 virtual environment (venv)](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)
* Java (I'm using OpenJDK 11.0.21)

#### How to create the environment:
1. Rename the file [.env.example](.env.example) to `.env` and change the values accordingly
2. Rename the file [pg-source-config.json.example](./debezium/pg-source-config.json.example) to `pg-source-config.json` and change the values accordingly
3. Create a new Python3 virtual environment by running `python3 venv .venv`. After that, activate the environment (`source .venv/bin/activate`) and install the required libraries from [requirements.txt](requirements.txt), running `pip install -r requirements.txt`.
4. Set execution permissions to Airflow's [entrypoint file](./airflow/scripts/entrypoint.sh), by running `sudo chmod +x airflow/scripts/entrypoint.sh`
5. Run the docker compose file to create the environment: `docker compose up -d` (or `docker-compose up -d` depending on your docker compose version)
 
#### How to insert mockup data into source tables in Postgres
Edit the python file [populate_tables.py](populate_tables.py) in order to adjust the amount of customers and invoices you want to create. Run the file using the command `python3 ./postgres-scripts/python/populate_tables.py`.

#### How to test batching process (Postgres -> Airflow -> Pyspark -> MinIO)
Before running the steps below, please make sure to run the script to insert mockup data into source tables, otherwise there will be no data to be exported to MinIO.
1. Open your Airflow instance by accessing [http://localhost:8080](http://localhost:8080) in your browser. Use the credentials user: `admin` and password: `admin` to access the home page (you can change this user if you want, just edit the file [./airflow/scripts/entrypoint.sh](airflow/scripts/entrypoint.sh)).
2. Start the DAG [./airflow/dags/dag_invoice_by_business.py](airflow/dags/dag_invoice_by_business.py) by accessing the [http://localhost:8080/dags/dag_invoice_by_business/grid](DAG detail link) and then clicking the toggle button on the top left.

![Activate DAG](https://github.com/renaros/de-challenge-invoices/blob/main/readme_images/airflow-activate-dag.jpg)

3. Wait until all steps are green.

![Airflow all green](https://github.com/renaros/de-challenge-invoices/blob/main/readme_images/airflow-all-green.jpg)

4. Access your MinIO instance using the link [http://localhost:9091](http://localhost:9091), providing your credentials (that should be set in your `.env` file). Access your [http://localhost:9001/browser/de-challenge](bucket details) and you should see a folder `invoice_by_business`. Inside this folder you should see another folder with the current month and the parquet file inside it.

![Minio folder](https://github.com/renaros/de-challenge-invoices/blob/main/readme_images/minio-folder.jpg)

5. If you want to reprocess / backfill a particular month, you can run the command in your local console (outside any container):
`docker exec -it airflow-webserver airflow tasks test dag_invoice_by_business query_source_table 'YYYY-MM-01'`
It will create a new folder in the de_challenge bucket in MinIO with the exported information.

#### How to test stream data (Postgres -> Debezium -> Kafka -> Consumer)
1. Run the command below to set up Debezium. This will create the Kafka topic `postgres.public.invoices` automatically after any record gets inserted into the invoices table.
`curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:9090/connectors/ -d @debezium/pg-source-config.json`
2. Run the command below in Postgres to insert mockup clients into the customers table:
`insert into public.customers (customer_name) values ('A'), ('B');`
3. Run the insert script below in Postgres to insert a new invoice into the table, which will create the topic if it is not created already.
`insert into public.invoices (issuer_id, receiver_id, amount_usd) values (1, 2, 999.90);`
4. Check if your topic was created by running in your terminal (locally):
`docker exec -it kafka ./bin/kafka-topics.sh --bootstrap-server=kafka:9092 --list --exclude-internal`

![Kafka topic created](https://github.com/renaros/de-challenge-invoices/blob/main/readme_images/kafka-topic-created.jpg)

5. You can also check the number of messages in your Kafka topic by running:
`docker exec -it kafka ./bin/kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list kafka:9092 --topic postgres.public.invoices | awk -F  ":" '{sum += $3} END {print "Result: "sum}'`
6. Last step is to run the consumer script to observe the streaming happening in real time.
`python3 ./streaming/invoice_consumer.py`
After running the command above, run another insert statement in Postgres to check the messages arriving into the consumer. Use `CTRL+C` to stop the program.

![Kafka streamed insert](https://github.com/renaros/de-challenge-invoices/blob/main/readme_images/kafka-inserted.jpg)

## Challenges during the development
* I could not use separate Spark containers in the docker compose file because my computer was not able to handle it :)
* It took me some time to make Airflow communicate to MinIO, the environment variables were not working properly. After lots of trial and error it finally worked, and I could use the environment variables for everything and no manual adjustments were needed.
* Debezium was very challenging to make it work, the library was not loading, then the wal_level had to be set to logical instead of replication and only after that it worked.
* Parsing the Kafka message was also challenging, decimal values are transformed into bytes by default in Debezium and it required lots of trial and error to fix that. In the end I changed the configuration to transform decimals to string and it worked like a charm. Besides that, issue_date was failing conversion because it is in unix timestamp but microseconds, and the function to convert it in PySpark uses seconds as a reference.


