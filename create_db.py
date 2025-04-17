import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database path from .env or use default
db_path = os.getenv("DB_PATH", "expense_tracker.db")

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the expenses table
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
print(f"Database and table created successfully at {db_path}!")
