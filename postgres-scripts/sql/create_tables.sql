CREATE TABLE customers(
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY,
    customer_name VARCHAR(255) NOT NULL,
    PRIMARY KEY(customer_id)
);

CREATE TABLE invoices (
    invoice_id BIGINT GENERATED ALWAYS AS IDENTITY,
    issue_date TIMESTAMP NOT NULL DEFAULT NOW(),
    issuer_id BIGINT,
    receiver_id BIGINT,
    amount_usd DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_issuer_id FOREIGN KEY(issuer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_receiver_id FOREIGN KEY(receiver_id) REFERENCES customers(customer_id),
    PRIMARY KEY(invoice_id)
);