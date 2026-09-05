# Task Manager — Backend

REST API for a collaborative task-management system: tasks and subtasks, task
dependencies, labels, friendships and task sharing, behind JWT authentication.

Built with FastAPI, SQLAlchemy and PostgreSQL. The React client lives in a
separate repository.

## Requirements

- Python 3.12+
- PostgreSQL 14+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create the database, then add a `.env` file in the repository root:

```
DATABASE_URL=postgresql://user:password@localhost:5432/your_database
JWT_SECRET=some-long-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:5173
```

`CORS_ORIGINS` is the comma-separated list of sites allowed to call the API; it
defaults to the Vite dev server, so it can be left out locally. `.env.example`
holds the same set of keys.

Apply the migrations and start the server:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

The API runs on `http://localhost:8000`. Interactive docs are at `/docs`.

## Deployment

`render.yaml` is a Render Blueprint describing the whole system — the Postgres
database, this API, and the frontend static site from its own repository — so
one Blueprint brings all three up and points them at each other.

Render supplies `DATABASE_URL` from the managed database and generates
`JWT_SECRET`; the frontend's build command reads the API's hostname from the
Blueprint and bakes it into the bundle. The one value that has to be typed is
`CORS_ORIGINS`, which is the frontend's own URL — the two services each need the
other's address, so one end of that pair cannot be resolved automatically.

The API runs migrations on boot (`alembic upgrade head` precedes `uvicorn`),
so a newly created database arrives at the current schema on the first deploy.

## Project layout

A request flows `routers/ -> schemas/ -> services/ -> models/ -> database`.
Each folder has one responsibility:

| Path | Holds |
|---|---|
| `app/main.py` | app creation, CORS, router registration |
| `app/core/` | settings, password hashing, JWT, auth dependency |
| `app/db/` | declarative base, engine and session dependency |
| `app/models/` | SQLAlchemy models, one per table |
| `app/schemas/` | Pydantic request and response models |
| `app/routers/` | endpoints grouped by resource |
| `app/services/` | business rules — the domain logic lives here, not in routers |
| `alembic/` | migrations |

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/register` | create an account (also seeds the default labels) |
| POST | `/auth/login` | exchange username and password for a JWT |
| GET | `/auth/me` | the current user |
| GET/POST | `/tasks` | list every visible task / create one |
| GET/PATCH/DELETE | `/tasks/{id}` | read, update, delete a task |
| GET/POST/DELETE | `/tasks/{id}/blockers/{blockerId}` | manage dependencies |
| POST/DELETE | `/tasks/{id}/labels/{labelId}` | attach or detach a label |
| GET/POST/DELETE | `/tasks/{id}/shares` | manage who a task is shared with |
| GET/POST | `/labels` | list or create labels |
| PATCH/DELETE | `/labels/{id}` | rename, recolour or delete a label |
| GET | `/friendships` | approved friends |
| GET | `/friendships/pending` | requests awaiting your approval |
| POST | `/friendships/request` | send a friend request |
| PATCH | `/friendships/{requesterId}` | approve or deny a request |
| DELETE | `/friendships/{friendId}` | remove a friend |

Every route except register and login expects an `Authorization: Bearer <token>`
header.

## Domain rules

**Tasks.** A task and a subtask are the same entity; a subtask points at its
parent through `parent_task_id` and has exactly one parent. A task's parent is
fixed at creation. Deleting a task deletes its whole subtree. Status is one of
`To Do`, `Done`, `Cancelled`. Completing a task records `done_date`; cancelling
one cascades `Cancelled` to every subtask and accepts an optional
`cancel_reason`, which is cleared again if the task leaves that status.

**Blocking is derived, never stored.** A task is blocked when a task it depends
on is still `To Do`, or when a task above it is blocked — so blocked state runs
down the subtask tree, and finishing a dependency unblocks everything below it
with no writes at all. `is_blocked` is computed per request and returned on
every task response.

Two rules follow from that and are enforced on every path that could break
them: a blocked task cannot be set to `Done`, and a task cannot be `Done` while
anything in its subtree is still `To Do`. That means a dependency cannot be
reopened while something that depends on it is done, and an unfinished
dependency cannot be added to a task that is already done — either would leave
a task done and blocked at the same time.

**Labels.** Every user is given a default set at registration and can create
more. Labels belong to a user, so two people sharing a task each label it for
themselves and each sees only their own.

**Friendships and sharing.** Friendships are a request/approve pair. The task
creator is its owner; only the owner can share a root task, and only with an
approved friend. Shared users get full management rights, and everything they
change — new subtasks included — is visible to everyone the task is shared
with. Deleting differs by role: an owner deleting removes the task for
everyone, while a shared user deleting only leaves the share. A friend cannot
be removed while a task is still shared between the two of you.
