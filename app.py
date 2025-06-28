import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import sqlite3
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Function to establish database connection
def create_db_connection():
    try:
        conn = sqlite3.connect("expense_tracker.db")
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# Initialize the database and create tables if they don't exist
def init_db():
    db = create_db_connection()
    if db:
        cursor = db.cursor()
        # Create user_balance table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_balance (
                user_id INTEGER PRIMARY KEY,
                balance REAL DEFAULT 0
            )
        """)
        db.commit()
        cursor.close()
        db.close()

init_db()

# Function to generate AI suggestion
def generate_ai_suggestion(user_id):
    db = create_db_connection()
    if not db:
        return "Could not connect to DB for AI suggestion."

    cursor = db.cursor()
    try:
        cursor.execute("SELECT category, amount, description FROM expenses WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()

        cursor.execute("SELECT balance FROM user_balance WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        balance = row[0] if row else 0

        if not rows:
            return "No expenses to analyze."

        expense_summary = "\n".join(
            [f"{row[0]} - ₹{row[1]} for {row[2]}" for row in rows]
        )

        prompt = f"""Here are the weekly expenses of a user:
{expense_summary}
The user's current balance is ₹{balance}.
Give a short financial suggestion to the user in bullet points:
- Is spending okay?
- Should they save more?
- Suggest smart ways to invest or reduce spending."""

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "meta-llama/llama-3-8b-instruct",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
        result = response.json()
        suggestion = result['choices'][0]['message']['content']

        return "\n".join([line.strip() for line in suggestion.strip().split("\n") if line.strip()])

    except Exception as e:
        print(f"AI generation error: {e}")
        return "AI suggestion not available."

    finally:
        cursor.close()
        db.close()

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
            VALUES (?, ?, ?, ?, ?)
        """
        values = (data['user_id'], data['category'], data['amount'], data['description'], data['expense_date'])
        cursor.execute(query, values)
        # Subtract from balance
        cursor.execute("INSERT INTO user_balance (user_id, balance) VALUES (?, 0) ON CONFLICT(user_id) DO NOTHING", (data['user_id'],))
        cursor.execute("UPDATE user_balance SET balance = balance - ? WHERE user_id = ?", (data['amount'], data['user_id']))
        db.commit()
        return jsonify({"message": "Expense added successfully!"})

    except sqlite3.Error as err:
        print(f"Error adding expense: {err}")
        return jsonify({"error": "Failed to add expense"}), 500

    finally:
        cursor.close()
        db.close()

# API to add income (increase balance)
@app.route('/add_income', methods=['POST'])
def add_income():
    data = request.json
    user_id = data.get('user_id')
    amount = float(data.get('amount', 0))
    if not user_id or amount <= 0:
        return jsonify({"error": "Invalid input"}), 400
    db = create_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO user_balance (user_id, balance) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?",
                       (user_id, amount, amount))
        db.commit()
        cursor.execute("SELECT balance FROM user_balance WHERE user_id = ?", (user_id,))
        balance = cursor.fetchone()[0]
        return jsonify({"message": "Income added!", "balance": balance})
    finally:
        cursor.close()
        db.close()

# API to get expenses and total
@app.route('/get_expenses/<int:user_id>', methods=['GET'])
def get_expenses(user_id):
    db = create_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("SELECT id, category, amount, description, expense_date FROM expenses WHERE user_id = ?", (user_id,))
        expenses = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT SUM(amount) AS total_expense FROM expenses WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        total_expense = row[0] if row[0] is not None else 0

        return jsonify({
            "expenses": expenses,
            "total_expense": total_expense
        })

    except sqlite3.Error as err:
        print(f"Error fetching expenses: {err}")
        return jsonify({"error": "Failed to fetch expenses"}), 500

    finally:
        cursor.close()
        db.close()

# API to get user balance
@app.route('/get_balance/<int:user_id>', methods=['GET'])
def get_balance(user_id):
    db = create_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = db.cursor()
    try:
        cursor.execute("SELECT balance FROM user_balance WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        balance = row[0] if row else 0
        return jsonify({"balance": balance})
    finally:
        cursor.close()
        db.close()

# New: Delete an expense
@app.route('/delete_expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    db = create_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        db.commit()
        return jsonify({"message": "Expense deleted successfully."})

    except sqlite3.Error as err:
        print(f"Error deleting expense: {err}")
        return jsonify({"error": "Failed to delete expense."}), 500

    finally:
        cursor.close()
        db.close()

# New: Endpoint to get chart data by category
@app.route('/chart_data/<int:user_id>', methods=['GET'])
def chart_data(user_id):
    db = create_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE user_id = ?
            GROUP BY category
        """, (user_id,))

        chart_data = cursor.fetchall()
        result = {row[0]: row[1] for row in chart_data}

        return jsonify(result)

    except sqlite3.Error as err:
        print(f"Error fetching chart data: {err}")
        return jsonify({"error": "Failed to fetch chart data."}), 500

    finally:
        cursor.close()
        db.close()

# AI suggestion only
@app.route('/ai_suggestion/<int:user_id>', methods=['GET'])
def ai_suggestion(user_id):
    suggestion = generate_ai_suggestion(user_id)
    return jsonify({"ai_suggestion": suggestion})
@app.route('/query_agent', methods=['POST'])
def query_agent():
    import re
    data = request.json
    user_id = data.get("user_id")
    user_query = data.get("query", "").lower()

    db = create_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("SELECT category, amount, description, expense_date FROM expenses WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        cursor.execute("SELECT balance FROM user_balance WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        balance = row[0] if row else 0
        if not rows:
            return jsonify({"answer": "No expenses found for the user."})

        # Simple intent detection for forecasting
        if any(word in user_query for word in ["predict", "forecast", "next week", "next month"]):
            forecast_type = "weekly" if "week" in user_query else "monthly"
            n_periods = 1
            match = re.search(r"next (\\d+) (week|month)", user_query)
            if match:
                n_periods = int(match.group(1))
            category = None
            for cat in set(r[0].lower() for r in rows):
                if cat in user_query:
                    category = cat
                    break
            # Call ML model directly
            ml_url = f"/predict_expense/{user_id}?type={forecast_type}&n_periods={n_periods}"
            if category:
                ml_url += f"&category={category}"
            # Use Flask test client to call the ML API internally
            with app.test_client() as client:
                ml_response = client.get(ml_url)
                ml_json = ml_response.get_json()
                prediction_text = f"Prediction: {ml_json.get('message', '')} {ml_json.get('predictions', '')}"
            prompt = f"""User asked: '{user_query}'\nThe forecast for the next period is: {ml_json.get('predictions', '')}.\nThe user's current balance is ₹{balance}.\nPlease explain what this means in simple terms, without inventing or recalculating any numbers. Do not provide any new numbers or daily breakdowns."""
        else:
            data_str = "\n".join([f"{r[0]},{r[1]},{r[2]},{r[3]}" for r in rows])
            prompt = f"""
You are an AI financial assistant. A user has the following expense records:
category, amount, description, date
{data_str}

The user's current balance is ₹{balance}.

Answer this question based on the data above:
'{user_query}'
Give your answer in one paragraph.
"""
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "meta-llama/llama-3-8b-instruct",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        result = response.json()
        answer = result['choices'][0]['message']['content']
        return jsonify({"answer": answer})
    except Exception as e:
        print(f"Query agent error: {e}")
        return jsonify({"answer": "Unable to process your question."})
    finally:
        cursor.close()
        db.close()

# ML Forecasting API
# ...existing code...

@app.route('/predict_expense/<int:user_id>', methods=['GET'])
def predict_expense(user_id):
    forecast_type = request.args.get("type", "weekly")  # weekly or monthly
    category = request.args.get("category", None)       # optional
    n_periods = int(request.args.get("n_periods", 1))   # how many future periods

    db = create_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        query = "SELECT expense_date, amount FROM expenses WHERE user_id = ?"
        params = [user_id]
        if category:
            query += " AND category = ?"
            params.append(category)
        df = pd.read_sql_query(query, db, params=params)

        if df.empty or df['amount'].sum() == 0:
            return jsonify({"predictions": [], "message": "No expenses found for this user/category."})

        # Group by week/month and sum amounts
        df['expense_date'] = pd.to_datetime(df['expense_date'])
        freq = 'W' if forecast_type == "weekly" else 'M'
        df = df.groupby(pd.Grouper(key='expense_date', freq=freq)).sum().reset_index()
        df = df.sort_values('expense_date')
        df['period'] = range(len(df))
        # Remove periods with zero amount (no expenses in that week/month)
        df = df[df['amount'] > 0]
        if len(df) < 4:
            return jsonify({"predictions": [], "message": "Not enough unique weeks/months of data to forecast. Please add more expenses spread across different weeks or months."})

        # Feature engineering: add lag features and rolling mean
        df['lag1'] = df['amount'].shift(1)
        df['lag2'] = df['amount'].shift(2)
        df['rolling_mean3'] = df['amount'].rolling(window=3).mean().shift(1)
        df = df.dropna()
        if len(df) < 2:
            return jsonify({"predictions": [], "message": "Not enough sequential data after feature engineering. Please add more expenses in different weeks/months."})

        features = ['period', 'lag1', 'lag2', 'rolling_mean3']
        X = df[features]
        y = df['amount']

        # Use Ridge regression for better regularization
        from sklearn.linear_model import Ridge
        model = Ridge(alpha=1.0)
        model.fit(X, y)

        # Prepare future periods for prediction
        last_row = df.iloc[-1]
        preds = []
        last_amounts = df['amount'].tolist()[-3:]
        last_rolling = df['rolling_mean3'].iloc[-1]
        max_hist = df['amount'].max()
        min_hist = df['amount'].min()
        for i in range(n_periods):
            lags = [
                last_amounts[-1] if len(last_amounts) > 0 else min_hist,
                last_amounts[-2] if len(last_amounts) > 1 else min_hist,
                last_amounts[-3] if len(last_amounts) > 2 else min_hist
            ]
            features_pred = np.array([[last_row['period'] + i + 1, lags[0], lags[1], last_rolling]])
            pred = model.predict(features_pred)[0]
            # Cap prediction to a reasonable range (0 to 2x max historical)
            pred = max(0, min(round(pred, 2), 2 * max_hist))
            preds.append(pred)
            last_amounts = [pred] + last_amounts[:2]
            last_rolling = np.mean(last_amounts)

        result = [{"period": i + 1, "predicted_amount": p} for i, p in enumerate(preds)]
        period_label = "week" if forecast_type == "weekly" else "month"
        return jsonify({
            "forecast_type": forecast_type,
            "category": category or "All",
            "n_periods": n_periods,
            "predictions": result,
            "message": f"Forecast for next {n_periods} {period_label}(s)."
        })
    except Exception as e:
        print(f"Forecasting error: {e}")
        return jsonify({"error": "Forecasting failed."}), 500
    finally:
        db.close()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
