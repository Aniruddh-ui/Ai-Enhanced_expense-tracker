# Expense Tracker with AI Agent

A modern, full-stack expense tracker web app built with Flask, SQLite, and Chart.js, featuring an AI-powered financial assistant using Llama 3 (via OpenRouter). Easily add, view, and delete expenses, visualize your spending, and ask natural language questions about your finances.

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/)

## 🌐 Live Demo
> **This app is deployed on [Render](https://render.com/).**
> 
> Visit: https://expense-tracker-vzs0.onrender.com
---

## 🚀 Features
- Add, view, and delete expenses by category, amount, description, and date
- Visualize spending by category with interactive charts
- Get AI-generated financial suggestions based on your expense history
- Ask the AI agent any question about your expenses in natural language
- Responsive, modern UI with animated effects

## 🛠️ Tech Stack
- **Backend:** Python, Flask, SQLite
- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **AI/LLM:** OpenRouter API (Llama 3)
- **Deployment:** Render.com

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 4. Initialize the Database
If not already created, run:
```bash
python create_db.py
```

### 5. Run the Application Locally
```bash
python app.py
```
The app will be available at `http://localhost:10000`

---

## 💡 Usage
- **Add Expense:** Fill in the form and click "Add Expense".
- **View Expenses:** Enter your User ID and click "Get Expenses".
- **AI Suggestion:** Click "Get AI Suggestion" for personalized advice.
- **Ask the AI Agent:** Type a question (e.g., "How much did I spend on food last month?") and click "Ask Agent".
- **Visualize:** Click "Show Chart" to see spending by category.

---

## 📁 Project Structure
```
app.py                # Main Flask app
create_db.py          # Script to initialize the database
expense_tracker.db    # SQLite database file
requirements.txt      # Python dependencies
templates/index.html  # Frontend UI
```

## 🔑 Environment Variables
- `OPENROUTER_API_KEY`: Your API key for OpenRouter (LLM access)

## 📦 Deployment
This app is deployed on [Render](https://render.com/). You can deploy your own instance by clicking the button below:

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/)

---

## 📝 License
MIT

---
**Made with ❤️ by Aniruddh-ui**
