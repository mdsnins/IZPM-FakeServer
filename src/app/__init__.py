import datetime

from flask import Flask
from os import urandom

from . import config
from . import database
from . import model
    
from .api import router as api_router

app = Flask(__name__)
app.config["SERVER_NAME"] = config.SERVER_NAME
app.secret_key = urandom(16)

app.register_blueprint(api_router, url_prefix='/v1')


def init_db():
    database.Base.metadata.create_all(bind = database.engine)

def test_db():
    u = model.User()
    u.user_id = "AAAABBBB"
    u.nickname = "테스트"
    u.gender = "male"
    u.country_code = "KR"
    u.prefecture_id = -1
    u.birthday = "20181029"
    membeR_id = 1

    database.db_session.add(u)

    m = model.Mail()
    m.mail_id = "m1"
    m.subject = "테스트 메일"
    m.content = "이건 테스트 메일입니다"
    m.member_id = 1
    m.time = datetime.datetime.now()
    m.datetime = datetime.datetime.now()
    m.is_image = True

    database.db_session.add(m)

    database.db_session.commit()
