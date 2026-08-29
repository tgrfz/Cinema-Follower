from cinema_follower.db import rq
from cinema_follower.utils.tmdb import load_followee_movies


def rq_load_followee_movies(person_id):
    rq.queue.enqueue(load_followee_movies, person_id)
