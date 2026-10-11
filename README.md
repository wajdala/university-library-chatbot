# 📚 University Library Chatbot

A smart, rule-based chatbot that assists university students and staff with library-related inquiries. Built with **Python** and **Flask** — no external APIs required.

![Status](https://img.shields.io/badge/Status-Completed-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-red)

---

## 🎯 Features

- ✅ Answer questions about library **opening hours**
- ✅ Guide users on **borrowing and returning** books
- ✅ Explain **renewal policies**
- ✅ Help users **search** for books
- ✅ Explain **fines and policies**
- ✅ Provide information about **study rooms, Wi-Fi, printing**
- ✅ **E-Books, Tutoring, Research help**
- ✅ **Case-insensitive matching** (HELLO = hello = Hello)
- ✅ **Fuzzy matching** (handles typos like "helo" → "hello")
- ✅ Clean, responsive **chat UI**
- ✅ **No external APIs needed** — runs entirely locally

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask |
| Frontend | HTML5, CSS3, JavaScript |
| Logic | Keyword Matching + Fuzzy Matching (SequenceMatcher) |

---

## 🚀 Getting Started

### 1. Clone the repository

git clone https://github.com/wajdala/university-library-chatbot.git
cd university-library-chatbot

2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

4. Install dependencies
pip install flask

5. Run the application
python app.py
Open your browser at http://localhost:5000.

🧠 How It Works
The user types a question in the chat UI.
The frontend sends the message to the Flask backend (/api/chat).
The backend normalizes the text (lowercase, remove punctuation).
It matches the message against a knowledge base using:
Exact keyword matching
Fuzzy matching (for typos)
Scoring system (longer keywords = higher weight)
The best matching response is returned.
The chatbot displays the reply to the user.

📂 Project Structure
text
university-library-chatbot/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js

    
💡 Example Questions
"What are the library hours?"
"How do I borrow a book?"
"Can I renew a book?"
"What is the fine for late returns?"
"Do you have study rooms?"
"How can I connect to Wi-Fi?"
"help"



