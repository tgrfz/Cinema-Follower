import logging
import os

from flask import Flask
from flask_login import LoginManager

from cinema_follower.utils.logs import set_logger

try:
    set_logger()
except AttributeError as e:
    logging.error(e)

from cinema_follower.auth import auth as auth_blueprint
from cinema_follower.db import db, rq
from cinema_follower.main import main as main_blueprint


def create_app():
    app = Flask(__name__)

    app.secret_key = os.getenv('CF_SECRET_KEY', default='tgrfz')
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlite.db"

    db.init_app(app)

    # Import all models so SQLAlchemy maps tables
    from cinema_follower.models.people import Person  # noqa: F401
    from cinema_follower.models.titles import Movie  # noqa: F401
    from cinema_follower.models.user import User, UserFollows  # noqa: F401

    with app.app_context():
        db.create_all()

    rq.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'main.index'

    @login_manager.user_loader
    def load_user(user_id):
        logging.method('init.load_user')
        return db.session.get(User, user_id)

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    return app


app = create_app()
