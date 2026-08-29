import logging
from datetime import date, timedelta
from typing import Any, Optional

from requests import Session
from sqlalchemy import select, update
from sqlalchemy.orm.exc import StaleDataError
from themoviedb import TMDb

from cinema_follower.db import db
from cinema_follower.models.titles import Movie
from cinema_follower.utils.cache import cache_result_json
from cinema_follower.utils.utils import get_secrets

tmdb = TMDb(key=get_secrets('key_personal'), session=Session())


@cache_result_json('person:{person_id}:movies')
def load_followee_movies(person_id: int) -> dict[int, dict[str, Any]]:
    logging.method('utils.tmdb.load_followee_movies')
    result = tmdb.person(person_id).movie_credits()

    movies = [Movie(m) for m in result.cast]
    credits = {
        m.id: {
            'order': m.order + 1,
            'is_self': m.character.endswith('self'),
            'department': [],
        }
        for m in result.cast
    }

    for m in result.crew:
        if m.id in credits:
            credits[m.id]['department'].append(m.department)
        else:
            credits[m.id] = {
                'order': -1,
                'is_self': False,
                'department': [m.department],
            }
            movies.append(m)

    cache_movies(movies, credits.keys())

    return credits


def cache_movies(movies: list[Movie], mids: set[int]):
    logging.method('utils.tmdb.cache_movies')
    TODAY = date.today()

    db_movies = db.session.execute(
        select(Movie).filter(Movie.id.in_(mids))
    ).scalars().all()
    db_data = {
        m.id: {
            'digital_release': m.digital_release,
            'last_cache_update': m.last_cache_update,
        }
        for m in db_movies
    }

    # if possible - and for the most movies it is - get digital release date from the db avoiding unnessesary API calls
    to_update: list[Movie] = []
    for movie in movies:
        db_dates = db_data.get(movie.id, {})
        if db_dates.get('last_cache_update', None) == TODAY:
            continue

        if (
            not db_dates or (
                db_dates['digital_release'] is None
                and movie.release_date is not None
                and TODAY - movie.release_date <= timedelta(days=730)  # too old to get new date info
            )
        ):
            movie.digital_release = _get_digital_release(tmdb.movie(movie.id).release_dates())
        else:
            movie.digital_release = db_dates['digital_release']

        movie.last_cache_update = TODAY
        to_update.append(movie)

    try:
        db.session.execute(
            update(Movie),
            [m.asdict() for m in to_update]
        )
    except StaleDataError:
        db.session.add_all(to_update)
    db.session.commit()


def _get_digital_release(release_dates) -> Optional[date]:
    dig_releases = {
        dt.release_date.date()
        for result in release_dates.results
        for dt in result.release_dates
        if dt.type in (4, 5)
    }
    if not dig_releases:
        return None
    return min(dig_releases)
