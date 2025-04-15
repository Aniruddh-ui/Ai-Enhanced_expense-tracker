import os
import mysql.connector
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

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

# API to get expenses and total
@app.route('/get_expenses/<int:user_id>', methods=['GET'])
def get_expenses(user_id):
    db = create_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT category, amount, description, expense_date FROM expenses WHERE user_id = %s", (user_id,))
        expenses = cursor.fetchall()

        cursor.execute("SELECT SUM(amount) AS total_expense FROM expenses WHERE user_id = %s", (user_id,))
        total_expense = cursor.fetchone()["total_expense"] or 0

        return jsonify({"expenses": expenses, "total_expense": total_expense})

    except mysql.connector.Error as err:
        print(f"Error fetching expenses: {err}")
        return jsonify({"error": "Failed to fetch expenses"}), 500

    finally:
        cursor.close()
        db.close()

# ✅ NEW: AI suggestion based on expenses
@app.route('/ai_suggestion/<int:user_id>', methods=['GET'])
def ai_suggestion(user_id):
    db = create_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT category, amount, description FROM expenses WHERE user_id = %s", (user_id,))
        expenses = cursor.fetchall()

        if not expenses:
            return jsonify({"message": "No expenses found for this user."}), 404

        expense_summary = "\n".join(
            [f"{e['category']} - ₹{e['amount']} for {e['description']}" for e in expenses]
        )

        prompt = f"""Here are the weekly expenses of a user:
{expense_summary}
Give a short financial suggestion to the user: 
- Is spending okay?
- Should they save more?
- Suggest smart ways to invest or reduce spending."""

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "openrouter/llama3-8b",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
        result = response.json()

        suggestion = result['choices'][0]['message']['content']
        return jsonify({"ai_suggestion": suggestion})

    except Exception as e:
        print(f"AI suggestion error: {e}")
        return jsonify({"error": "Failed to generate AI suggestion"}), 500

    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
