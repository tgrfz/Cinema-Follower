import logging

from cinema_follower.db import redis_client
from cinema_follower.utils.cache import cache_result_set
from cinema_follower.utils.tmdb import load_followee_movies


@cache_result_set('user:{current_user.id}:movie_feed')
def build_movie_feed(current_user):
    logging.method('utils.feed.build_movie_feed')
    feed = set()
    for fol in current_user.follows:
        if fol.follow_type.value.subscribe:
            movies = load_followee_movies(fol.person_id)
            # filter movies by follow settings
            feed.update(movies.keys())
    return feed


def clear_feed_caches(current_user):
    redis_client.delete(f'user:{current_user.id}:movie_feed')
