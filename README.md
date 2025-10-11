AI Personal Trainer (pose detection + form coaching).

## Local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Docs: http://localhost:8000/docs


Figma Prototype Link: https://www.figma.com/proto/sJKbAUzHt5fEfRWXEreYiu/AI-Personal-Trainer?node-id=0-1&t=C1ZaBED6WkSJmLoS-1

Figma File Link: https://www.figma.com/design/sJKbAUzHt5fEfRWXEreYiu/AI-Personal-Trainer?node-id=0-1&t=C1ZaBED6WkSJmLoS-1 
