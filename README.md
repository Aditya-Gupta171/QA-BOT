# Dataset Q&A Bot

A beginner-friendly Python application that lets you upload a **Titanic dataset** (CSV or SQLite) and ask natural language questions about it. The backend uses **FastAPI** and Gemini AI, and the frontend is built with **Streamlit**.

---

## 🚀 Features

- Upload CSV or SQLite dataset (Titanic format)
- Ask questions like:
  - What percentage of passengers survived?
  - How many passengers were in first class?
  - What was the average age of passengers who survived?
  - Which gender had a higher survival rate?
- Get instant, human-readable answers
- Clean, modern UI with Montserrat font

---

## 🗂️ Project Structure

```
backend/
│
├── app/
│   ├── __init__.py
│   ├── ai_service.py
│   ├── data_handler.py
│   ├── main.py
│   ├── query_executor.py
│   └── routes.py
│
├── .streamlit/
│   └── config.toml
│
├── train.csv           # Titanic dataset (for demo/testing)
├── frontend.py         # Streamlit frontend
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
├── .env                # Gemini API key (not committed)
├── .gitignore
```

---

## 🧑‍💻 Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/qa-bot.git
cd qa-bot/backend
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API key

Create a `.env` file in the `backend` folder:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Run the FastAPI backend

```bash
uvicorn app.main:app --reload
```
- The API will be available at [http://localhost:8000](http://localhost:8000)
- Docs at [http://localhost:8000/docs](http://localhost:8000/docs)

### 6. Run the Streamlit frontend

Open a new terminal, activate your venv, then:

```bash
streamlit run frontend.py
```
- The app will open at [http://localhost:8501](http://localhost:8501)

---

