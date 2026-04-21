# RAG Chatbot — Quick Start Guide

## Prerequisites
- Python 3.10
- Node.js 18+

---

## 1. Setup Backend

```powershell
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and edit environment file
copy .env.example .env
# Edit .env with your LLM URL and token
# (or configure via the Settings tab in the UI)

# Start the server
uvicorn main:app --reload --port 8000
```

---

## 2. Setup Frontend

```powershell
cd frontend

# Install packages
npm install

# Start dev server
npm run dev
```

---

## 3. Open the App

Navigate to: **http://localhost:5173**

---

## Workflow
1. Go to **⚙️ Settings** → enter your LLM API URL, token, and model → Save
2. Upload documents (PDF, TXT, DOCX) using the left sidebar
3. Ask questions in the **💬 Chat** tab

---

## Run Tests (Backend)

```powershell
cd backend
.venv\Scripts\activate
pytest tests/ -v
```
