from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from cinema_follower.db import db

if TYPE_CHECKING:
    from cinema_follower.models.people import Person


@dataclass
class FollowProps:
    color: str
    subscribe: bool


class FollowType(Enum):
    TRACK = FollowProps('red', True)
    HIGHLIGHT = FollowProps('black', False)
    NONE = FollowProps('gray', False)

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    profile_pic: Mapped[str]
    token: Mapped[str]
    refresh_token: Mapped[str]
    token_uri: Mapped[str]
    client_id: Mapped[str]
    client_secret: Mapped[str]

    follows: Mapped[list[UserFollows]] = db.relationship(
        "UserFollows",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def get_follows(self, ftypes=list(FollowType)) -> dict:
        return [
            {'person': f.person, 'type': f.follow_type}
            for f in self.follows
            if f.follow_type in ftypes
        ]


class UserFollows(db.Model):
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'), primary_key=True)
    person_id: Mapped[str] = mapped_column(ForeignKey('person.id'), primary_key=True)
    follow_type: Mapped[FollowType]

    user: Mapped[User] = db.relationship(
        "User",
        back_populates="follows",
    )

    person: Mapped[Person] = db.relationship(
        "Person",
        back_populates="followers",
    )

    @property
    def highlight_color(self) -> str:
        return self.follow_type.value.color
