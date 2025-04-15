import sqlite3

conn = sqlite3.connect("expense_tracker.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    category TEXT,
    amount REAL,
    description TEXT,
    expense_date TEXT
)
""")

conn.commit()
conn.close()
print("Database and table created successfully!")
