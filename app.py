import os
import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database connection using FreeSQLDatabase.com credentials
db = mysql.connector.connect(
    host="sql12.freesqldatabase.com",  # Replace with your DB host
    user="sql12770307",  # Replace with your DB username
    password="kz9jXxJP75",  # Replace with your DB password
    database="sql12770307"  # Replace with your DB name
)
cursor = db.cursor()

# Homepage Route
@app.route("/")
def home():
    return "Welcome to the Expense Tracker API! Use /add_expense to add an expense or /get_expenses/<user_id> to retrieve expenses."

# API to add expenses
@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.json
    query = """
        INSERT INTO Expenses (user_id, category, amount, description, expense_date)
        VALUES (%s, %s, %s, %s, %s)
    """
    values = (data['user_id'], data['category'], data['amount'], data['description'], data['expense_date'])
    
    cursor.execute(query, values)
    db.commit()
    
    return jsonify({"message": "Expense added successfully!"})

# API to get expenses
@app.route('/get_expenses/<int:user_id>', methods=['GET'])
def get_expenses(user_id):
    cursor.execute("SELECT * FROM Expenses WHERE user_id = %s", (user_id,))
    expenses = cursor.fetchall()
    return jsonify({"expenses": expenses})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)  # Port 10000 for Render



