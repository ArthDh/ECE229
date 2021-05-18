import os

class BaseConfig:
    DEBUG = True
    ENV = 'development'
    SECRET_KEY = os.urandom(64)
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = './.flask_session/'