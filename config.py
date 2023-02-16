import os

class BaseConfig(object):
    MONGO_URI = os.environ['MONGO_URI']
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']