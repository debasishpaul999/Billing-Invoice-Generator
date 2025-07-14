from db import connect_db
import random

def add_customer(name, email, phone, address):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO customer (name, email, phone, address) VALUES (?, ?, ?, ?)",
        (name, email, phone, address)
    )
    conn.commit()
    conn.close()

def get_customer():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM customer")
    return cursor.fetchall()

def search_customer(keyword):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM customer WHERE name LIKE ?", ('%' + keyword + '%',))
    return cursor.fetchall()

def create_invoices(customer_id, date_str, items):
    conn = connect_db()
    cursor = conn.cursor()

    invoice_id = random.randint(100000, 999999)

    cursor.execute("INSERT INTO invoice (id, customer_id, date) VALUES (?, ?, ?)",
                   (invoice_id, customer_id, date_str))

    for code, unit, qty, price in items:
        cursor.execute("""
            INSERT INTO invoice_item (invoice_id, code, unit, quantity, price)
            VALUES (?, ?, ?, ?, ?)
        """, (invoice_id, code, unit, qty, price))

    conn.commit()
    conn.close()
    return invoice_id
