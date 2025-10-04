# AI Trainer Backend (FastAPI)

Backend service for the AI Personal Trainer (pose detection + form coaching).

## Local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Docs: http://localhost:8000/docs
