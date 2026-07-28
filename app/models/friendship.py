from enum import Enum, auto

from sqlalchemy import CheckConstraint, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FriendshipStatus(Enum):
    PENDING = auto()
    ACCEPTED = auto()


class Friendship(Base):


    __tablename__ = "friendships"

    requester_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    addressee_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    status: Mapped[FriendshipStatus] = mapped_column(
        SQLEnum(FriendshipStatus), default=FriendshipStatus.PENDING, index=True
    )

    __table_args__ = (
        CheckConstraint(
            "requester_id <> addressee_id", name="ck_friendships_no_self_friendship"
        ),
    )
