# Data Engineering Challenge - Invoices
Repository for invoices data engineering challenge.

## Sections
* [Problem statement](#problem-statement)
* [Use Cases](#use-cases)
    * [Use case 1: Consume one invoice by its ID](#use-case-1-consume-one-invoice-by-its-id)
    * [Use case 2: Group invoices for the last n months by business id (or customer id)](#use-case-2-group-invoices-for-the-last-n-months-by-business-id-or-customer-id)
    * [Use case 3: Join this table with other sources for analytics purposes](#use-case-3-join-this-table-with-other-sources-for-analytics-purposes-not-necessarily-structured-data)
    * [Use case 4: Execute a risk model whenever a new invoice is created](#use-case-4-execute-a-risk-model-whenever-a-new-invoice-is-created)

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

### Code Structure
Explain the structure of your codebase hosted on GitHub. Describe the main components, directories, and files.

### How to Run the Code
Provide step-by-step instructions on how to run your code. Include prerequisites, dependencies, and any configuration needed.

Requirements:
- Docker compose
- Python3 virtual environment (venv)
- Java

Step-by-step:
1. Rename the file [.env.example](.env.example) to `.env` and change the environment variable values
2. Create a new Python3 virtual environment by running `python3 venv .venv`. After that, activate the environment (`source .venv/bin/activate`) and install the required libraries from [requirements.txt](requirements.txt), running `pip install -r requirements.txt`.
3. Set execution permissions to Airflow's [entrypoint file](./airflow/scripts/entrypoint.sh), by running `sudo chmod +x airflow/scripts/entrypoint.sh`
3. Run the docker compose file to create the environment: `docker compose up -d`
4. Edit the python file [populate_tables.py](populate_tables.py) in order to adjust the amount of customers and invoices you want to create. Run the file using the command `python3 ./postgres-scripts/python/populate_tables.py`.

#### Example Commands
Show example commands or code snippets to execute the code.

### Code Explanation
Break down the functionality of your code. Explain the major functions, classes, or modules and their roles in solving the problem.

## Conclusion
Summarize your proposed architecture, highlighting its strengths in addressing the outlined use cases. Reiterate how your code addresses the problem statement effectively.

## Q&A
Q: Why not creating spark containers in the docker composer file?
A: My computer was not being able to handle this amount of containers :)
