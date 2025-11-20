import sqlite3

def add_client(conn, name, phone):
    c = conn.cursor()
    c.execute("INSERT INTO clients (name, phone) VALUES (?, ?)", (name, phone))
    conn.commit()

def add_equipment(conn, name):
    c = conn.cursor()
    c.execute("INSERT INTO equipment (name) VALUES (?)", (name,))
    conn.commit()

def create_request(conn, client_id, equipment_id, date_start, date_end):
    c = conn.cursor()
    try:
        conn.execute('BEGIN')
        c.execute("INSERT INTO requests (client_id, equipment_id, date_start, date_end, status) VALUES (?, ?, ?, ?, 'active')", 
                  (client_id, equipment_id, date_start, date_end))
        conn.commit()
    except:
        conn.rollback()

def complete_payment(conn, request_id, amount, paid_date):
    c = conn.cursor()
    try:
        conn.execute('BEGIN')
        c.execute("UPDATE requests SET status='closed' WHERE id=?", (request_id,))
        c.execute("INSERT INTO payments (request_id, amount, paid_date) VALUES (?, ?, ?)", (request_id, amount, paid_date))
        conn.commit()
    except:
        conn.rollback()
