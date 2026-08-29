import logging
from datetime import date

from sqlalchemy.orm import Mapped, mapped_column
from themoviedb import CastMovie, CrewMovie
from themoviedb.schemas._enums import SizeType

from cinema_follower.db import db

EMPTY_POSTER = 'https://www.themoviedb.org/assets/2/v4/glyphicons/basic/glyphicons-basic-38-picture-grey-c2ebdbb057f2a7614185931650f8cee23fa137b93812ccb132b9df511df1cfac.svg'  # noqa: E501


class Title():
    id: Mapped[int] = mapped_column(primary_key=True)
    overview: Mapped[str | None] = None
    vote_average: Mapped[float | None] = None
    poster: Mapped[str | None] = None
    popularity: Mapped[float | None] = None
    last_cache_update: Mapped[date | None] = None

    def __init__(self, title):
        if isinstance(title, CastMovie) or isinstance(title, CrewMovie):
            self.id = title.id
            self.overview = title.overview
            self.vote_average = round(title.vote_average, 1) if title.vote_count > 10 else None
            self.poster = title.poster_url(SizeType.w300) or EMPTY_POSTER
            self.popularity = title.popularity
        else:
            logging.error('Title.__init__: unknown type')  # MAYBE raise?

    def asdict(self) -> dict:
        return {
            'id': self.id,
            'overview': self.overview,
            'vote_average': self.vote_average,
            'poster': self.poster,
            'popularity': self.popularity,
            'last_cache_update': self.last_cache_update,
        }

    @property
    def star_color(self) -> str:
        if self.vote_average is None:
            return 'white'
        rating = int(self.vote_average + 0.5)
        match rating:
            case 10:
                return 'darkgreen'
            case 9:
                return 'darkgreen'
            case 8:
                return 'green'
            case 7:
                return 'yellowgreen'
            case 6:
                return 'gold'
            case 5:
                return 'coral'
            case _:
                return 'red'


class Movie(db.Model, Title):
    name: Mapped[str]
    release_date: Mapped[date | None] = None
    digital_release: Mapped[date | None] = None

    def __init__(self, title):
        Title.__init__(self, title)

        if isinstance(title, CastMovie) or isinstance(title, CrewMovie):
            self.name = title.title
            self.release_date = title.release_date
        else:
            logging.error('Movie.__init__: unknown type')

    def asdict(self) -> dict:
        d = Title.asdict(self)
        d.update({
            'name': self.name,
            'release_date': self.release_date,
            'digital_release': self.digital_release,
        })
        return d

    @property
    def is_released(self) -> bool:
        return not (self.release_date is None or self.release_date > date.today())

    @property
    def is_dig_released(self) -> bool:
        return not (self.digital_release is None or self.digital_release > date.today())

    @property
    def url(self) -> str:
        return f'https://www.themoviedb.org/movie/{self.id}'


# class Tv(db.Model, Title):
#     def __init__(self, title, **additional_info):
#         super().__init__(title)
#         self.name = title.name
#         self.first_air_date = title.first_air_date
#         self.new_season_air_date = additional_info.get('air_date', None)
