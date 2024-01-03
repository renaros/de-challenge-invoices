# invoices-de-challenge
Repository for invoices data engineering challenge

## Requirements:
- Docker compose
- Python3 virtual environment (venv)

## How to create the environment and load the source table:
1. Rename the file [.env.example](.env.example) to `.env` and change the environment variable values
2. Create a new Python3 virtual environment by running `python3 venv .venv`. After that, activate the environment (`source .venv/bin/activate`) and install the required libraries from [requirements.txt](requirements.txt), running `pip install -r requirements.txt`.
3. Run the docker compose file to create the environment: `docker compose up -d`
4. Edit the python file [populate_tables.py](populate_tables.py) in order to adjust the amount of customers and invoices you want to create. Run the file using the command `python3 ./postgres-scripts/python/populate_tables.py`.