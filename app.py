import os
import mysql.connector
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Function to establish database connection
def create_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "sql12.freesqldatabase.com"),
            user=os.getenv("DB_USER", "sql12770307"),
            password=os.getenv("DB_PASSWORD", "kz9jXxJP75"),
            database=os.getenv("DB_NAME", "sql12770307")
        )
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# Serve index.html
@app.route("/")
def home():
    return render_template("index.html")

# API to add expenses
@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.json
    db = create_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = db.cursor()
    
    try:
        query = """
            INSERT INTO expenses (user_id, category, amount, description, expense_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (data['user_id'], data['category'], data['amount'], data['description'], data['expense_date'])
        cursor.execute(query, values)
        db.commit()
        return jsonify({"message": "Expense added successfully!"})

    except mysql.connector.Error as err:
        print(f"Error adding expense: {err}")
        return jsonify({"error": "Failed to add expense"}), 500

    finally:
        cursor.close()
        db.close()

# API to get expenses
@app.route('/get_expenses/<int:user_id>', methods=['GET'])
def get_expenses(user_id):
    db = create_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = db.cursor()

    try:
        cursor.execute("SELECT * FROM expenses WHERE user_id = %s", (user_id,))
        expenses = cursor.fetchall()
        return jsonify({"expenses": expenses})

    except mysql.connector.Error as err:
        print(f"Error fetching expenses: {err}")
        return jsonify({"error": "Failed to fetch expenses"}), 500

    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)





