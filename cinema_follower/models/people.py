from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column
from themoviedb import Person as tmdb_Person
from themoviedb.schemas._enums import SizeType

from cinema_follower.db import db

if TYPE_CHECKING:
    from cinema_follower.models.user import UserFollows


NO_PHOTO = 'https://www.themoviedb.org/assets/2/v4/glyphicons/basic/glyphicons-basic-38-picture-grey-c2ebdbb057f2a7614185931650f8cee23fa137b93812ccb132b9df511df1cfac.svg'  # noqa: E501


class Person(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    profile_path: Mapped[str | None] = None

    followers: Mapped[list[UserFollows]] = db.relationship(
        "UserFollows",
        back_populates="person",
    )

    def __init__(self, tmdb_info: tmdb_Person):
        self.id = tmdb_info.id
        self.name = tmdb_info.name
        self.profile_path = tmdb_info.profile_path

    @property
    def url(self) -> str:
        return f'https://www.themoviedb.org/person/{self.id}'

    @property
    def photo(self, size: SizeType = SizeType.w300) -> str:
        if self.profile_path is None:
            return NO_PHOTO
        return f'https://image.tmdb.org/t/p/{size.value}{self.profile_path}'
