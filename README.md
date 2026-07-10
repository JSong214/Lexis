# Lexis

Lexis is a React + FastAPI foundation for the vocabulary context-learning MVP described in
[`docs/English Learning AI Agent PRD.md`](docs/English%20Learning%20AI%20Agent%20PRD.md).

## Development

Start the backend:

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

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

The current foundation does not call OpenAI or require an API key.
