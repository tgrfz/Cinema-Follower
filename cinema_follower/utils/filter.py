from typing import Iterable

from sqlalchemy import select

from cinema_follower.db import db
from cinema_follower.models.titles import Movie

CARDS_PER_PAGE = 5


def filter_movies(movies: list[int], filter=None, page=None, per_page=CARDS_PER_PAGE) -> Iterable[Movie]:
    stmt = select(Movie).filter(Movie.id.in_(movies))
    stmt = stmt.filter(Movie.release_date)
    stmt = stmt.order_by(Movie.release_date.desc())

    if page:
        return db.paginate(stmt, page=page, per_page=per_page, error_out=False)
    return db.session.execute(stmt).scalars().all()
