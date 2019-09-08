import os
from dotenv import load_dotenv

class Config(object):
    load_dotenv()
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.urandom(24)
    FLASK_DEBUG=1

    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    GOOGLE_ANALYTICS_TRACK_ID = os.getenv("GOOGLE_ANALYTICS_TRACK_ID")

    BASIC_AUTH_USERNAME = "basic"
    BASIC_AUTH_PASSWORD = "basic"

    #Database
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    