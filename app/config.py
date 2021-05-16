import os

class BaseConfig:
    # SQLALCHEMY_DATABASE_URI = get_sqlite_uri()
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SECRET_KEY = os.environ['SECRET_KEY']

    SECRET_KEY = os.urandom(64)
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = './.flask_session/'