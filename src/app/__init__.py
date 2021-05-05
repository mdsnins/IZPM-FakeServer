from flask import Flask
from os import urandom

from . import config
from . import database

from .api import router as api_router

app = Flask(__name__)
app.config["SERVER_NAME"] = config.SERVER_NAME
app.secret_key = urandom(16)

app.register_blueprint(api_router, url_prefix='/v1')


def init_db():
    from . import model
    database.Base.metadata.create_all(bind = database.engine)