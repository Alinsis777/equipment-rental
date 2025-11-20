import sqlite3
from faker import Faker

conn = sqlite3.connect('rental.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    price_per_day REAL NOT NULL,
    status TEXT DEFAULT 'available'
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER REFERENCES clients(id),
    equipment_id INTEGER REFERENCES equipment(id),
    date_start TEXT,
    date_end TEXT,
    status TEXT DEFAULT 'active'
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER REFERENCES requests(id),
    amount REAL,
    paid_date TEXT
)
''')
c.execute('''
CREATE TRIGGER IF NOT EXISTS trigger_rent_equipment
AFTER INSERT ON requests
BEGIN
    UPDATE equipment SET status='rented' WHERE id=NEW.equipment_id;
END;
''')
equipment_data = [
    ("Проектор", 1500.0),
    ("Ноутбук", 2000.0),
    ("Камера", 1800.0),
    ("Микрофон", 500.0),
    ("Освещение", 700.0),
]

for name, price in equipment_data:
    c.execute("INSERT OR IGNORE INTO equipment (name, price_per_day) VALUES (?, ?)", (name, price))
fake = Faker()
for _ in range(6):
    c.execute("INSERT INTO clients (name, phone) VALUES (?, ?)", (fake.name(), fake.phone_number()))

conn.commit()
conn.close()
