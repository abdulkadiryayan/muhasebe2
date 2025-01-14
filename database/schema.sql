CREATE TABLE IF NOT EXISTS titles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cash_owners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS construction_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title_id INTEGER,
    cash_owner_id INTEGER,
    date TEXT NOT NULL,
    company_name TEXT,
    construction_group_id INTEGER,
    description TEXT,
    expense REAL,
    payment_received REAL,
    check_received REAL,
    check_given REAL,
    apartment_sale REAL,
    invoice_amount REAL,
    quantity REAL,
    unit_price REAL,
    FOREIGN KEY (title_id) REFERENCES titles (id),
    FOREIGN KEY (cash_owner_id) REFERENCES cash_owners (id),
    FOREIGN KEY (construction_group_id) REFERENCES construction_groups (id)
); 