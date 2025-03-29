import os
import mysql.connector
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Database connection using FreeSQLDatabase.com credentials
db = mysql.connector.connect(
    host=os.getenv("DB_HOST", "sql12.freesqldatabase.com"),  # Default value for local testing
    user=os.getenv("DB_USER", "sql12770307"),
    password=os.getenv("DB_PASSWORD", "kz9jXxJP75"),
    database=os.getenv("DB_NAME", "sql12770307")
)
cursor = db.cursor()

# Serve index.html
@app.route("/")
def home():
    return render_template("index.html")

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
    app.run(host='0.0.0.0', port=10000, debug=True)  # Debug mode enabled for local testing




