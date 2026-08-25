from sqlalchemy.orm import Session
from app import models
from fastapi import HTTPException, status
from sqlalchemy import select

from app.schemas.label_schemas import LabelCreate, LabelUpdate
from app.services.task_service import get_task

# Every new user starts with this fixed set. Users can add their own labels later,
# and these behave exactly the same once created — they are not special-cased.
DEFAULT_LABELS: list[tuple[str, str]] = [
    ("Work", "#3B82F6"),
    ("Personal", "#10B981"),
    ("Urgent", "#EF4444"),
    ("Study", "#8B5CF6"),
    ("Home", "#F59E0B"),
]


def create_default_labels(db: Session, user_id: int) -> list[models.Label]:

    labels = [
        models.Label(label_name=name, label_color=color, user_id=user_id)
        for name, color in DEFAULT_LABELS
    ]
    db.add_all(labels)
    db.flush()
    return labels




def get_labels(db: Session, user: models.User) -> list[models.Label]:
    labels = db.execute(
        select(models.Label).where(
            models.Label.user_id == user.user_id,
        )
    ).scalars().all()




    return list(labels)

def get_owned_label(db: Session, user: models.User, label_id: int) -> models.Label:

    label = db.execute(
        select(models.Label).where(
            models.Label.label_id == label_id,
            models.Label.user_id == user.user_id,
        )
    ).scalars().first()

    if label is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found",
        )

    return label




def create_label(db: Session, user: models.User, label: LabelCreate) -> models.Label:

    _ensure_name_is_free(db, user, label.label_name)

    new_label = models.Label(
        label_name=label.label_name,
        label_color=label.label_color,
        user_id=user.user_id,
    )
    db.add(new_label)
    db.commit()
    db.refresh(new_label)
    return new_label


def update_label(
    db: Session, user: models.User, label_id: int, changes: LabelUpdate
) -> models.Label:

    label = get_owned_label(db, user, label_id)

    updates = changes.model_dump(exclude_unset=True)

    if "label_name" in updates:
        _ensure_name_is_free(db, user, updates["label_name"], exclude_label_id=label_id)

    for field, value in updates.items():
        setattr(label, field, value)

    db.commit()
    db.refresh(label)
    return label


def delete_label(db: Session, user: models.User, label_id: int) -> None:

    label = get_owned_label(db, user, label_id)

    # The ON DELETE CASCADE on task_labels clears the links to any task.
    db.delete(label)
    db.commit()


def add_label_to_task(
    db: Session, user: models.User, task_id: int, label_id: int
) -> models.Task:


    task = get_task(db, user, task_id)
    label = get_owned_label(db, user, label_id)

    if label not in task.labels:  # attaching twice is not an error
        task.labels.append(label)
        db.commit()
        db.refresh(task)

    return task


def remove_label_from_task(
    db: Session, user: models.User, task_id: int, label_id: int
) -> None:

    task = get_task(db, user, task_id)
    label = get_owned_label(db, user, label_id)

    if label not in task.labels:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="That label is not attached to this task",
        )

    task.labels.remove(label)
    db.commit()



def _ensure_name_is_free(
    db: Session, user: models.User, label_name: str, exclude_label_id: int | None = None
) -> None:

    query = select(models.Label).where(
        models.Label.label_name == label_name,
        models.Label.user_id == user.user_id,
    )
    if exclude_label_id is not None:
        query = query.where(models.Label.label_id != exclude_label_id)

    existing_label = db.execute(query).scalars().first()

    if existing_label is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a label with that name",
        )