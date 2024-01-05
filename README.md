# Data Engineering Challenge - Invoices
Repository for invoices data engineering challenge.

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
* [Conclusion](#conclusion)

## Problem Statement
This challenge consists of a table that stores information related to invoices that customers send and receive between each other, and the idea is to provide an architecture that is scalable and efficient to manage this data.
The table is stored in a RDBMS (for this exercise I'm using Postgres) and the volume is growing fast. The structure uses the following columns:
* _invoice id_: unique id by invoice
* _issue date_: the date and time where the invoice was created
* _issuer id_: customer id that sent the invoice
* _receiver id_: customer id that received the invoice
* _amount_: amount to be paid, in USD

## Use Cases
Some use cases for this table are:

### Use Case 1: Consume one invoice by its ID
Here I'm splitting into short, medium and long term solutions since migration is not possible on the short term.

#### Proposed Architecture
* _Short-term_: In this case, the fastest and easiest approach would be to just index the table by invoice id. This way we can speed up the searches with not much effort and using the original architecture.
* _Medium/long-term_: Additionally, we could implement a caching layer like Redis or Memcached to enhance performance by storing frequently accessed invoices in memory.
We also could consider migrating this table to distributed database systems - such as Amazon DynamoDB - in order to have better scalability.

### Use Case 2: Group invoices for the last n months by business id (or customer id)
For this scenario I'm assuming a analytics approach, updating the stats on a schedule (batching).

#### Proposed Architecture
-

### Use Case 3: Join this table with other sources for analytics purposes (not necessarily structured data)
-

#### Proposed Architecture
-

### Use Case 4: Execute a risk model whenever a new invoice is created
-

#### Proposed Architecture
-

## Solution Overview
-

### Code Structure
Explain the structure of your codebase hosted on GitHub. Describe the main components, directories, and files.

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
-

#### How to test stream data (Postgres -> Debezium -> Kafka -> Consumer)
1. Run the command below to setup Debezium. This will create the Kafka topic `postgres.public.invoices` automatically after any record gets inserted into the invoices table.
`curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:9090/connectors/ -d @debezium/pg-source-config.json`
2. Run the command below in Postgres to insert mockup clients into the customers table:
`insert into public.customers (customer_name) values ('A'), ('B');`
3. Run the insert script below in Postgres to insert a new invoice into the table, which will create the topic if it is not created already.
`insert into public.invoices (issuer_id, receiver_id, amount_usd) values (1, 2, 999.90);`
4. Check if your topic was created by running in your terminal (locally):
`docker exec -it kafka ./bin/kafka-topics.sh --bootstrap-server=kafka:9092 --list --exclude-internal`
5. You can also check the number of messages in your Kafka topic by running:
`docker exec -it kafka ./bin/kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list kafka:9092 --topic postgres.public.invoices | awk -F  ":" '{sum += $3} END {print "Result: "sum}'`
6. Last step is to run the consumer script to observe the streaming happening in real time.
`python3 ./streaming/invoice_consumer.py`
After running the command above, run another inserts in Postgrees to check the messages arriving into the consumer.

### Code Explanation
Break down the functionality of your code. Explain the major functions, classes, or modules and their roles in solving the problem.

## Conclusion
Summarize your proposed architecture, highlighting its strengths in addressing the outlined use cases. Reiterate how your code addresses the problem statement effectively.

## Q&A
Q: Why not creating spark containers in the docker composer file?
A: My computer was not being able to handle this amount of containers :)
