# Task Manager — Backend (FastAPI)

## Setup (run these yourself)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then edit the values (DB URL, JWT secret)
```

## Run

```bash
uvicorn app.main:app --reload
```

- Interactive API docs (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Structure

```
app/main.py       FastAPI app + route registration
app/core/         config (env vars) + security (JWT / password hashing)
app/db/           SQLAlchemy engine, session, and Base
app/models/       ORM models              (Phase 1)
app/schemas/      Pydantic request/response models
app/routers/      API endpoints, grouped by resource
app/services/     business-logic layer    (Phase 4 & 7 rules)
```

## Migrations (Phase 1)

```bash
alembic init alembic                                  # generates the alembic/ folder
# point sqlalchemy.url / env.py at your DATABASE_URL and import Base's metadata, then:
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

## Git (run yourself)

```bash
git init
git add .
git commit -m "Phase 0: backend skeleton"
# create the GitHub repo, then:
git remote add origin <your-repo-url>
git push -u origin main
# add snirN as a collaborator on the repo
```
