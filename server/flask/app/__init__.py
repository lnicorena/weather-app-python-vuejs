from flask import Flask
from flask_cors import CORS
from flask_caching import Cache
import sys

# configuration
config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_TYPE": "redis",  # Flask-Caching related configs
    "CACHE_REDIS_HOST": 'redis',
    "CACHE_REDIS_URL": "redis://redis:6379"
}

# instantiate the app
app = Flask(__name__)
# app.config.from_object(__name__)
app.config.from_mapping(config)

cache = Cache(app)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

from app import database
from app import main
