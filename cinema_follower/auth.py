import logging
from datetime import timedelta

import flask
import google.oauth2.credentials
import google_auth_oauthlib.flow
from flask_login import login_required, login_user, logout_user
from googleapiclient.discovery import build
from oauthlib.oauth2.rfc6749.errors import AccessDeniedError

from cinema_follower.db import db
from cinema_follower.models.user import User
from cinema_follower.utils.utils import get_secrets

GOOGLE_APP = get_secrets('google')
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid',
]

auth = flask.Blueprint('auth', __name__)


@auth.route('/login')
def login():
    logging.method('auth.login')
    flow = google_auth_oauthlib.flow.Flow.from_client_config(GOOGLE_APP, scopes=SCOPES)
    flow.redirect_uri = flask.url_for('auth.callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
    )
    flask.session['state'] = state
    logging.debug(authorization_url)
    return flask.redirect(authorization_url)


@auth.route("/login/callback")
def callback():
    logging.method('auth.callback')
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_config(GOOGLE_APP, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('auth.callback', _external=True)

    authorization_response = flask.request.url
    try:
        flow.fetch_token(authorization_response=authorization_response)
    except AccessDeniedError:
        logging.info('Access denied')
        return flask.redirect('/')

    credentials = flow.credentials
    flask.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'granted_scopes': credentials.granted_scopes,
    }

    credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
    oauth2_client = build('oauth2', 'v2', credentials=credentials)
    user_info = oauth2_client.userinfo().get().execute()

    user = db.session.get(User, user_info['id'])
    if not user:
        user = User(
            id=user_info['id'],
            email=user_info['email'],
            name=user_info['name'],
            profile_pic=user_info['picture'],
            token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_uri=credentials.token_uri,
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
        )
        db.session.add(user)
        db.session.commit()

    login_user(user, remember=True, duration=timedelta(365))

    return flask.redirect('/')


@auth.route('/logout')
@login_required
def logout():
    logging.method('auth.logout')
    logout_user()
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return flask.redirect('/')
