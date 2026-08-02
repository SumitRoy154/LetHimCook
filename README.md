# 🍳 Let Him Cook!

Let Him Cook! is an agentic AI cooking simulator where multiple specialized AI agents work together to turn a dish request into a full cooking experience. The app plans recipes, checks inventory, purchases missing ingredients, simulates cooking, reviews the result, rewards the user, and stores each workflow step in a database.


---

## ✨ What this project does

- Lets a user enter a dish name and start an AI-driven cooking flow
- Uses multiple agents for planning, inventory checks, shopping decisions, cooking, judging, and rewards
- Tracks wallet balances, inventory, orders, transactions, reviews, and workflow executions
- Provides a polished interactive frontend experience for the cooking journey

---

## 🧠 Core architecture

The application is orchestrated with LangGraph. Each stage shares workflow state and passes execution to the next node.

```text
User Input
  ↓
Planner Agent
  ↓
Inventory / Shopping Logic
  ↓
Cook Agent
  ↓
Judge Agent
  ↓
Reward / Persistence
  ↓
Frontend Results
```

---

## 🤖 Agent roles

- Planner Agent: creates the recipe plan, steps, and ingredients
- Inventory Agent: checks what is already available
- Shopping Logic: buys missing ingredients and updates the wallet
- Cook Agent: simulates the cooking process
- Judge Agent: reviews the final outcome and gives feedback
- Reward Agent: credits coins and saves the result

---

## 🛠️ Tech stack

### Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS
- Framer Motion
- TanStack Query
- Zustand

### Backend
- FastAPI
- Python
- SQLAlchemy
- Alembic
- MySQL
- JWT authentication

### AI / orchestration
- LangGraph
- OpenAI
- Anthropic Claude
- Google Gemini
- Groq

---

## 📁 Project structure

```text
Let Him Cook/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── graph/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/
│   ├── scripts/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── client/
│   ├── server/
│   ├── shared/
│   └── package.json
└── README.md
```

---

## 🗄️ Database

The backend uses MySQL with SQLAlchemy and Alembic migrations.

The app stores data for:
- users
- wallets
- inventory
- orders
- transactions
- reviews
- workflow executions

---

## 🚀 How to clone and run on another device

### 1. Prerequisites

Install the following:
- Git
- Python 3.10+ (recommended 3.12)
- Node.js 20+
- pnpm
- MySQL 8.0+

### 2. Clone the repository

```powershell
git clone <your-repo-url>
cd "LetHimCook"
```

### 3. Backend setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Update the backend environment file with your own values.

Example:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=let_him_cook
DB_USER=root
DB_PASSWORD=your_mysql_password

JWT_SECRET_KEY=your_long_random_secret

OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_key
```

Create the MySQL database:

```sql
CREATE DATABASE let_him_cook;
```

Run the migrations:

```powershell
alembic upgrade head
```

Start the backend:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend docs will be available at:
- http://localhost:8000/docs
- http://localhost:8000/api/health

### 4. Frontend setup

```powershell
cd ../frontend
pnpm install
pnpm dev --host 0.0.0.0 --port 3000
```

Open the app at:
- http://localhost:3000

---

## 🧪 Useful verification commands

From the backend folder:

```powershell
python scripts/verify_db.py
python scripts/test_auth.py
python scripts/test_workflow.py "Egg Roll"
```

From the frontend folder:

```powershell
pnpm exec tsc --noEmit
```

---

## 📌 Notes

- The backend uses MySQL and expects a reachable local database instance.
- AI features require valid API keys for the providers you want to use.
- If you want to run without live model calls, the project structure also supports mock or fallback behavior in parts of the workflow.

---

## 👨‍💻 Author

Built as an agentic AI cooking simulation demonstrating multi-agent orchestration, workflow persistence, and an interactive cooking experience using FastAPI, Next.js, LangGraph, and MySQL.

