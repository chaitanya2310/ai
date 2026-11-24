# 🎓 Student Assistant

An AI study assistant built with **CrewAI**, **Ollama**, **FastAPI**, **Streamlit** and **MySQL**. A student asks a question, and the system routes it to the right specialist agent. It also creates course content, MCQ tests, and a progress dashboard. Each student has a login, and their data is kept separate.

## ✨ Features

- **Ask Assistant:** answers questions using specialist agents:
  - **Student Tutor:** explains concepts
  - **Study Planner:** creates study plans and schedules
  - **Quiz Master:** creates practice questions
- **Long-term memory:** remembers past questions per student (Mem0 with ChromaDB) and reuses exact answers from MySQL.
- **Courses:** browse courses and open lessons. Courses are stored in `data/courses.json`, and new courses can be added from the page.
- **MCQ Test:** generates a multiple-choice test on any topic and grades it.
- **Dashboard:** shows questions asked per day, topics studied, quiz scores and weak topics.
- **Login:** students create an account and log in. Passwords are hashed.
- **Input guardrails:** checks questions before they reach the agents.

## 🏗️ Architecture

```
Student (browser)
      │
      ▼
Streamlit UI (ui.py)  ── login, courses, MCQ, dashboard
      │  HTTP POST /ask
      ▼
FastAPI (api.py)
      │
      ├── guardrails_validate  → checks the question
      ├── MySQL memory         → exact answer already saved?
      ├── Mem0 + ChromaDB      → related past memories
      ├── router.py            → chooses Tutor / Planner / Quiz
      ├── CrewAI agents        → runs the chosen specialists (Ollama LLM)
      └── MySQL + Mem0         → saves the answer and the log
```

## 📁 Project Structure

```
student assistent/
├── api.py                  # FastAPI backend (/ask)
├── ui.py                   # Streamlit app (run this file)
├── router.py               # rule-based routing to agents
├── requirements.txt
├── .env                    # your MySQL password (not committed)
├── agents/                 # CrewAI agents (tutor, planner, quiz, ...)
├── tasks/                  # CrewAI tasks
├── app/
│   ├── memory.py           # Mem0 long-term memory
│   ├── database.py         # MySQL exact-answer cache
│   ├── dashboard_db.py     # conversation log and quiz scores
│   ├── test_service.py     # MCQ generation and validation
│   └── mcq_ui.py           # MCQ page
├── courses/                # course pages and course loading
├── dashboard/              # dashboard page
├── login/                  # login and registration
├── styles/                 # style.py and style.css (app theme)
├── guardrails_validate/    # input validation
├── schemas/                # Pydantic models (MCQ quiz format)
├── data/
│   └── courses.json        # course content
└── mem0_db/                # Mem0 vector store (created automatically)
```

> The Streamlit app imports these packages from the project root. Each folder needs an `__init__.py` file, even if it's empty.

## ⚙️ Requirements

- Python 3.10 or newer
- [Ollama](https://ollama.com) running locally
- MySQL 8 (or MariaDB 10.6+)
- Node.js, only if you use MCP servers (optional)

## 📥 Installation

### 1. Clone or copy the project

```bash
cd "student assistent"
```

### 2. Create and activate a virtual environment

```bash
python -m venv sa
sa\Scripts\activate          # Windows
source sa/bin/activate       # macOS / Linux
```

### 3. Install the Python packages

```bash
pip install -r requirements.txt
```

### 4. Set up Ollama models

Install Ollama, then pull the models the project uses:

```bash
ollama pull llama3.2            # agent LLM and Mem0 memory extraction
ollama pull nomic-embed-text    # embeddings for Mem0 memory
```

To use a different model, change the `model=` line in the agent files (for example `ollama/qwen3:4b`).

Check that the models are installed:

```bash
ollama list
```

If you use a cloud model, sign in first with `ollama signin`. Cloud models need an internet connection.

### 5. Create the MySQL database

```sql
CREATE DATABASE student_memory;
```

The app creates these tables automatically on first use:

- `conversation_log` and `quiz_scores` (dashboard)
- `users` (login)

The answer cache table `memory` is **not** created automatically. Create it once:

```sql
USE student_memory;

CREATE TABLE memory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    memory_text VARCHAR(200),
    question TEXT NOT NULL,
    answer LONGTEXT,
    INDEX idx_user_question (user_id, question(100))
);
```

### 6. Create the `.env` file

Copy `.env.example` to `.env` and set your MySQL password:

```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=student_memory
```

## ▶️ Running the Project

The app has two parts, and both must be running. Use two terminals from the project folder.

**Terminal 1: start the API**

```bash
uvicorn api:app --reload
```

The API runs at `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/docs` to test it.

**Terminal 2: start the web app**

```bash
python -m streamlit run ui.py
```

Open the address Streamlit shows (usually `http://localhost:8501`), create an account, and log in.

Keep both terminals open while you use the app. If you change the model name, restart the API, because the agents are created at startup.

## 🧭 Using the App

| Menu item | What it does |
|---|---|
| Ask Assistant | Type a question and press **Ask Assistant**. Examples: `about java`, `7 day python study plan`, `give me a sql quiz` |
| Courses | Click **Open course** to read lessons. Use **➕ Add a new course** to add more |
| MCQ Test | Enter a topic, number of questions and difficulty, then submit your answers |
| Dashboard | Pick a day to see topics and questions. Also shows scores by topic |

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `Cannot reach the API ... WinError 10061` | The API isn't running. Start `uvicorn api:app --reload` first. |
| `API error 500` with `Executor is already running` | Two requests ran at the same time. Wait for the first answer to finish. |
| `model ... not found` (404) | The model name in the agent files doesn't match `ollama list` exactly, including the tag (for example `:latest` or `:cloud`). |
| `Access denied for user 'root'` | Check `MYSQL_PASSWORD` in `.env`, then restart the API. |
| `Style file not found` warning | `styles/style.css` is missing or in the wrong folder. |
| `Attribute "app" not found` | Run `uvicorn api:app` from the project folder, where `api.py` is. |
| Dashboard shows "Cannot connect to MySQL" | Start MySQL, then reload the page. |

## 🔒 Security Notes

- Keep `.env` out of version control. Add it to `.gitignore`.
- Passwords are stored as salted PBKDF2 hashes. They are never saved in plain text.
- The API trusts the username sent by the UI. This is fine on your own computer. Before you deploy it, add token-based authentication to the API.
- Use a read-only MySQL user for any tool that only reads data.

## 🗺️ Future Improvements

- MCP servers for course files and calendar access
- Semantic memory search for the dashboard
- Token-based API authentication
- Docker setup for MySQL, Ollama and the app

## 📄 License

Add your license here, for example MIT.