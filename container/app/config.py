import os
from app.secrets import Secrets


class Configuration:
    SQLALCHEMY_DATABASE_URI = Secrets.SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.urandom(24)
    DEBUG = True
    MSEARCH_INDEX_NAME = 'index_search'
    # simple,whoosh,elaticsearch, default is simple
    MSEARCH_BACKEND = 'simple'
    # auto create or update index
    MSEARCH_ENABLE = True
