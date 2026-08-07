from sqlalchemy.orm import Session

from app import models

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
