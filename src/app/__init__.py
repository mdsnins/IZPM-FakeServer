import datetime

from flask import Flask
from os import urandom

from . import config
from . import database
from . import model
    
from .api import router as api_router, api_init
from .web import router as web_router

app = Flask(__name__)
app.config["SERVER_NAME"] = config.SERVER_NAME
app.secret_key = urandom(16)

app.register_blueprint(api_router, url_prefix='/v1')
app.register_blueprint(web_router)


def init_db():
    database.Base.metadata.create_all(bind = database.engine)
    
    database.db_session.add(model.Member(0, "", "", ""))
    database.db_session.add(model.Member(1, "장원영", "JANG WON YOUNG", config.IMAGE_PREFIX + "/1.jpg"))
    database.db_session.add(model.Member(2, "미야와키 사쿠라", "MIYAWAKI SAKURA", config.IMAGE_PREFIX + "/2.jpg"))
    database.db_session.add(model.Member(3, "조유리", "JO YU RI", config.IMAGE_PREFIX + "/3.jpg"))
    database.db_session.add(model.Member(4, "최예나", "CHOI YE NA", config.IMAGE_PREFIX + "/4.jpg"))
    database.db_session.add(model.Member(5, "안유진", "AN YU JIN", config.IMAGE_PREFIX + "/5.jpg"))
    database.db_session.add(model.Member(6, "야부키 나코", "YABUKI NAKO", config.IMAGE_PREFIX + "/6.jpg"))
    database.db_session.add(model.Member(7, "권은비", "KWON EUN BI", config.IMAGE_PREFIX + "/7.jpg"))
    database.db_session.add(model.Member(8, "강혜원", "KANG HYE WON", config.IMAGE_PREFIX + "/8.jpg"))
    database.db_session.add(model.Member(9, "혼다 히토미", "HONDA HITOMI", config.IMAGE_PREFIX + "/19.jpg"))
    database.db_session.add(model.Member(10, "김채원", "KIM CHAE WON", config.IMAGE_PREFIX + "/10.jpg"))
    database.db_session.add(model.Member(11, "김민주", "KIM MIN JU", config.IMAGE_PREFIX + "/11.jpg"))
    database.db_session.add(model.Member(12, "이채연", "LEE CHAE YEON", config.IMAGE_PREFIX + "/12.jpg"))
    
    database.db_session.commit()

def load_pm(pm_data):
    members = model.Member.query.all()
    m_dict = {
        "장원영":1, "미야와키 사쿠라":2, "조유리":3, "최예나":4, "안유진": 5, "야부키 나코":6,
        "권은비":7, "강혜원":8, "혼다 히토미":9, "김채원":10, "김민주":11, "이채연":12,
        "チャン・ウォニョン":1, "宮脇咲良":2, "チョ・ユリ":3, "チェ・イェナ":4, "アン・ユジン":5, "矢吹奈子":6,
        "クォン・ウンビ":7, "カン・へウォン":8, "本田仁美":9, "キム・チェウォン":10, "キム・ミンジュ":11, "イ・チェヨン":12,
    }
    for mail in pm_data:
        if mail["member"] == "운영팀":
            continue
        m = model.Mail()
        m.mail_id = mail["id"]
        m.subject = mail["subject"]
        m.content = mail["preview"][:80]
        m.time = datetime.datetime.strptime(mail["time"], "%Y/%m/%d %H:%M")
        m.datetime = datetime.datetime.strptime(mail["time"], "%Y/%m/%d %H:%M")
        m.is_image = mail["image"]
        m.member_id = m_dict[mail["member"]]

        members[m_dict[mail["member"]]].mails.append(m)
         
        database.db_session.add(m)
    database.db_session.commit()
        

def test_db():
    u = model.User()
    u.user_id = "AAAABBBB"
    u.nickname = "테스트"
    u.gender = "male"
    u.country_code = "KR"
    u.prefecture_id = -1
    u.birthday = "20181029"
    u.member_id = 1

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

def init():
    api_init()
