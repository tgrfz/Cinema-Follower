import logging

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from cinema_follower.utils.feed import build_movie_feed, clear_feed_caches
from cinema_follower.utils.filter import filter_movies
from cinema_follower.utils.people import follow_person, unfollow_person
from cinema_follower.utils.rq_jobs import rq_load_followee_movies

CONTEXT_BASE = {
    "navbar_items": [
        {'name': "Movies", "route": "main.movies"},
        {'name': "TVs", "route": "main.index"},
        {'name': "Digital releases", "route": "main.index"},
        {'name': "Following", "route": "main.people"},
    ],
}


main = Blueprint('main', __name__)


@main.route('/')
def index():
    logging.method('main.index')
    context = {
        **CONTEXT_BASE,
        'current_user': current_user,
    }
    print(current_user)
    return render_template('index.html', **context)


@main.route('/movies')
@login_required
def movies():
    logging.method('main.movies')

    # TODO show text if no follows hence no movies
    feed = build_movie_feed(current_user)
    movie_list = filter_movies(feed, page=1)

    context = {
        **CONTEXT_BASE,
        'current_user': current_user,
        'movie_list': movie_list,
        'page': 1,
    }
    return render_template('movies/movies.html', **context)


@main.route("/movies/load")
@login_required
def movies_load():
    logging.method('main.movies_load')
    page = request.args.get("page", 1, type=int)
    feed = build_movie_feed(current_user)
    movie_batch = filter_movies(feed, page=page)
    return render_template("movies/_movie_cards_batch.html", movie_batch=movie_batch)


@main.route('/movies/filter', methods=['POST'])
@login_required
def apply_movie_filter():
    logging.method('main.apply_movie_filter')
    return redirect(url_for('main.movies'))


@main.route('/people')
@login_required
def people():
    logging.method('main.people')
    follows_list = current_user.get_follows()  # TODO show text if no follows
    context = {
        **CONTEXT_BASE,
        'current_user': current_user,
        'follows': follows_list,
    }
    return render_template('people.html', **context)


@main.route('/people/add', methods=['POST'])
@login_required
def people_add():
    logging.method('main.people_add')

    id = request.form.get("add_person_id")
    try:
        follow_person(current_user, person_id=id)
        rq_load_followee_movies(id)
        clear_feed_caches(current_user)
    except Exception as e:
        logging.error(repr(e))

    return redirect(url_for('main.people'))


@main.route('/people/remove/<int:id>', methods=['POST'])
@login_required
def people_remove(id):
    logging.method('main.people_remove')
    unfollow_person(current_user, id)
    clear_feed_caches(current_user)
    return redirect(url_for('main.people'))
