import pyodbc

def connect_db():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-LM8M7EG\\SQLEXPRESS;'
        'DATABASE=invoices;'
        'Trusted_Connection=yes;'
    )

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='customer' AND xtype='U')
    CREATE TABLE customer (
        id INT PRIMARY KEY IDENTITY(1,1),
        name VARCHAR(100),
        email VARCHAR(100),
        phone VARCHAR(20),
        address VARCHAR(255)
    )
    """)

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='invoice' AND xtype='U')
    CREATE TABLE invoice (
        id INT PRIMARY KEY,
        customer_id INT,
        date DATE,
        FOREIGN KEY (customer_id) REFERENCES customer(id)
    )
    """)

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='invoice_item' AND xtype='U')
    CREATE TABLE invoice_item (
        id INT PRIMARY KEY IDENTITY(1,1),
        invoice_id INT,
        code VARCHAR(50),
        unit VARCHAR(50),
        quantity INT,
        price DECIMAL(10,2),
        FOREIGN KEY (invoice_id) REFERENCES invoice(id)
    )
    """)

    conn.commit()
    conn.close()