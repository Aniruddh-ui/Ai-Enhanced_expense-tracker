from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Connect to MySQL Database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="annu@2005",
    database="FinanceTracker"
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
    cursor.execute(f"""
        INSERT INTO Expenses (user_id, category, amount, description, expense_date)
        VALUES ({data['user_id']}, '{data['category']}', {data['amount']}, '{data['description']}', '{data['expense_date']}')
    """)
    db.commit()
    return jsonify({"message": "Expense added successfully!"})

# API to get expenses
@app.route('/get_expenses/<int:user_id>', methods=['GET'])
def get_expenses(user_id):
    cursor.execute(f"SELECT * FROM Expenses WHERE user_id = {user_id}")
    expenses = cursor.fetchall()
    return jsonify({"expenses": expenses})

if __name__ == '__main__':
    app.run(debug=True)

