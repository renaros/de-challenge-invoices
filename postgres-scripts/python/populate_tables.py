import os
import psycopg2
import random
from math import ceil
from faker import Faker
from random import choice
from numpy.random import randint
from datetime import datetime, timedelta
from dotenv import load_dotenv


# Number of customers to be added
num_customers = 10000
num_invoices = 1000000
max_invoices_inserted_per_statement = 10000

def populate_customers(pgconn, faker_obj: Faker) -> None:
    customer_list_str = ','.join([f"('{faker_obj.company()}')" for _ in range(num_customers)])

    cur = pgconn.cursor()
    try:   
        # Generate random customer names and insert into the table
        cur.execute(f"INSERT INTO customers (customer_name) VALUES {customer_list_str};")
        
        pgconn.commit()
        print(f"Successfully inserted {num_customers} customer names into the table.")
    except Exception as e:
        pgconn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()


def populate_invoices(pgconn, faker_obj: Faker) -> None:

    cur = pgconn.cursor()
    try:
        invoices_created = 0
        for batch_idx in range(ceil(num_invoices/max_invoices_inserted_per_statement)):

            # get amount of invoices to be created in this batch
            invoices_to_create = max_invoices_inserted_per_statement
            if batch_idx == ceil(num_invoices/max_invoices_inserted_per_statement) - 1:
                invoices_to_create = num_invoices - invoices_created
            
            # create a list of invoices insert statements to be executed later
            invoices_list = list()
            for _ in range(invoices_to_create):
                # get random timestamp
                issue_date_str = faker_obj.date_time_between(start_date=datetime.now() - timedelta(days=2*365)).strftime('%Y-%m-%d %H:%M:%S')
                # get random issuer / receiver id according to number of customers (they must be different)
                issuer_id = randint(1, num_customers)
                receiver_id = choice(list(set(range(1, num_customers)).difference(set([issuer_id]))))
                # get random amount in US dolars
                amount_usd = random.uniform(0.01, 10000000)
                invoices_list.append(f"(TIMESTAMP '{issue_date_str}', {issuer_id}, {receiver_id}, {amount_usd})")
            invoices_list_str = ','.join(invoices_list)

            cur.execute(f"INSERT INTO invoices (issue_date, issuer_id, receiver_id, amount_usd) VALUES {invoices_list_str};")
            pgconn.commit()
            invoices_created += invoices_to_create

            percentage_complete_str = '{0:.2f}%'.format(invoices_created/num_invoices * 100)
            print(f"Successfully inserted {invoices_to_create} invoices ({invoices_created} out of {num_invoices} - {percentage_complete_str})")
        
    except Exception as e:
        pgconn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()

if __name__ == "__main__":
    
    Faker.seed(0)
    faker_obj = Faker(['en_US'])

    load_dotenv() # load environment variable file

    # PostgreSQL connection details
    pgconn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host="127.0.0.1",
        port="5432"
    )

    populate_customers(pgconn, faker_obj)
    populate_invoices(pgconn, faker_obj)

    pgconn.close()
