# invoices-de-challenge
Repository for invoices data engineering challenge.

## Problem description
This challenge consists of a table that stores information related to invoices that customers send and receive between each other, and the idea is to provide an architecture that is scalable and efficient to manage this data.
The table is stored in a RDBMS (the example I'm using on this repository is using Postgres) and the volume is growing fast, and is composed by the following columns:
* invoice id: unique id by invoice
* issue date: the date and time where the invoice was created
* issuer id: customer id that sent the invoice
* receiver id: customer id that received the invoice
* amount: amount to be paid, in USD

### Use cases
Some use cases are:
* Consume one invoice by its id
* Group invoices for the last n months by business id (or customer id)
* Join this table with other sources for analytics purposes (not necessarily structured data)
* Execute a risk model whenever a new invoice is created
The approach for this example should be cloud friendly, and the source data cannot be migrated in the short term.

### Architecture
This is the architecture I have in mind for this scenario:
INSERT IMAGE HERE

#### Approaches to tackle the use cases
##### Consume one invoice by its id
In this case, the fastest and easiest approach would be to index the table by invoice id (in my example it's already indexed since it's a primary key). This way we can speed up the searches with not much effort.

## Requirements:
- Docker compose
- Python3 virtual environment (venv)

## How to create the environment and load the source table:
1. Rename the file [.env.example](.env.example) to `.env` and change the environment variable values
2. Create a new Python3 virtual environment by running `python3 venv .venv`. After that, activate the environment (`source .venv/bin/activate`) and install the required libraries from [requirements.txt](requirements.txt), running `pip install -r requirements.txt`.
3. Set execution permissions to Airflow's [entrypoint file](./airflow/scripts/entrypoint.sh), by running `sudo chmod +x airflow/scripts/entrypoint.sh`
3. Run the docker compose file to create the environment: `docker compose up -d`
4. Edit the python file [populate_tables.py](populate_tables.py) in order to adjust the amount of customers and invoices you want to create. Run the file using the command `python3 ./postgres-scripts/python/populate_tables.py`.

