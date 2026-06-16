# EduPath Agent

EduPath Agent is a Software Cup A3 demo project for personalized learning resource generation with multi-agent coordination.

## Stack

- Backend: FastAPI, SQLAlchemy, MySQL, Pydantic
- Frontend: Vue 3, Vite, TypeScript, Element Plus
- LLM providers: mock for tests/demo, DeepSeek for temporary development, Spark for final competition replacement

## Quick Start

```powershell
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

```powershell
cd frontend
npm install
npm run dev
```

The backend health endpoint is `GET /api/health`.

