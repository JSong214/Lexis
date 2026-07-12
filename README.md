# Lexis

Lexis is a React + FastAPI foundation for the vocabulary context-learning MVP described in
[`docs/English Learning AI Agent PRD.md`](docs/English%20Learning%20AI%20Agent%20PRD.md).

## Development

Start PostgreSQL:

```powershell
docker compose up -d db
```

Start the backend:

```powershell
cd backend
Copy-Item .env.example .env # first run only
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend stores password hashes and opaque server-side sessions in PostgreSQL.
Registration and login set an `HttpOnly`, `SameSite=Lax` cookie; the frontend
restores the session through `GET /api/v1/auth/me`.

Start the frontend in another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api/*` requests to FastAPI on
`http://127.0.0.1:8000`.

## Checks

```powershell
cd backend
uv run pytest
uv run ruff check .

cd ../frontend
npm run lint
npm run build
```

The current authentication slice does not call an LLM. OpenRouter configuration
will be added with the lesson-generation slice.
