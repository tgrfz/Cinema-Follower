import logging

from cinema_follower.db import db
from cinema_follower.models.people import Person
from cinema_follower.models.user import FollowType, UserFollows
from cinema_follower.utils.tmdb import tmdb


def follow_person(current_user, person_id):
    if db.session.get(UserFollows, {'user_id': current_user.id, 'person_id': person_id}):
        logging.warning('Already following person %s', person_id)
        # raise UserWarning(f'Already following person {person_id}')

    person = db.session.get(Person, person_id)
    if not person:
        info = tmdb.person(person_id).details()
        person = Person(info)
        db.session.add(person)
        db.session.commit()
        logging.debug('Added info about %s (%s)', person.name, person_id)

    follow = UserFollows(
        user=current_user,
        person=person,
        follow_type=FollowType.TRACK,
    )
    db.session.add(follow)
    db.session.commit()
    logging.debug('Now following %s (%s)', person.name, person_id)


def unfollow_person(current_user, person_id):
    follow = db.session.get(UserFollows, {'user_id': current_user.id, 'person_id': person_id})
    current_user.follows.remove(follow)
    db.session.commit()
