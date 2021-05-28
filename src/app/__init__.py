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
app.config["UPLOAD_FOLDER"] = "/tmp"
app.config["MAX_CONTENT_LENGTH"] = 2.5 * 1024 * 1024
app.secret_key = urandom(16)

app.register_blueprint(api_router, url_prefix='/v1')
app.register_blueprint(web_router)


def init_db():
    database.Base.metadata.create_all(bind = database.engine)
    
    database.db_session.add(model.Member(0, "", "", ""))
    database.db_session.add(model.Member(1, "장원영", "JANG WON YOUNG", config.PROFILE_PREFIX + "/1.jpg"))
    database.db_session.add(model.Member(2, "미야와키 사쿠라", "MIYAWAKI SAKURA", config.PROFILE_PREFIX + "/2.jpg"))
    database.db_session.add(model.Member(3, "조유리", "JO YU RI", config.PROFILE_PREFIX + "/3.jpg"))
    database.db_session.add(model.Member(4, "최예나", "CHOI YE NA", config.PROFILE_PREFIX + "/4.jpg"))
    database.db_session.add(model.Member(5, "안유진", "AN YU JIN", config.PROFILE_PREFIX + "/5.jpg"))
    database.db_session.add(model.Member(6, "야부키 나코", "YABUKI NAKO", config.PROFILE_PREFIX + "/6.jpg"))
    database.db_session.add(model.Member(7, "권은비", "KWON EUN BI", config.PROFILE_PREFIX + "/7.jpg"))
    database.db_session.add(model.Member(8, "강혜원", "KANG HYE WON", config.PROFILE_PREFIX + "/8.jpg"))
    database.db_session.add(model.Member(9, "혼다 히토미", "HONDA HITOMI", config.PROFILE_PREFIX + "/9.jpg"))
    database.db_session.add(model.Member(10, "김채원", "KIM CHAE WON", config.PROFILE_PREFIX + "/10.jpg"))
    database.db_session.add(model.Member(11, "김민주", "KIM MIN JU", config.PROFILE_PREFIX + "/11.jpg"))
    database.db_session.add(model.Member(12, "이채연", "LEE CHAE YEON", config.PROFILE_PREFIX + "/12.jpg"))

    #database.db_session.add(model.Member(13, "평행우주 프로젝트", "IZ PU PROJECT", config.PROFILE_PREFIX + "/pu.jpg"))
    database.db_session.add(model.Member(13, "설정", "SETTINGS", config.PROFILE_PREFIX + "/settings.png"))

    database.db_session.commit()
    
    #pu = model.Member.query.all()[13]
    settings = model.Member.query.all()[13]

    m = model.Mail()
    m.mail_id = "config/member_name"
    m.subject = "멤버별 닉네임 설정"
    m.preview = "멤버별 수신 별명 설정은 여기서 해주세요."
    m.content = "멤버별 수신 별명 설정은 여기서 해주세요."
    m.time = datetime.datetime.strptime("2018/10/29 00:00", "%Y/%m/%d %H:%M")
    m.datetime = datetime.datetime.strptime("2018/10/29 00:00", "%Y/%m/%d %H:%M")
    m.is_image = False
    m.member_id = 13

    settings.mails.append(m)
    database.db_session.add(m)
    database.db_session.commit()

    m = model.Mail()
    m.mail_id = "config/common"
    m.subject = "일반 설정"
    m.preview = "조사 자동 변경, 번역 버튼 활성화 등의 설정"
    m.content = "조사 자동 변경, 번역 버튼 활성화 등의 설정"
    m.time = datetime.datetime.strptime("2018/10/29 00:00", "%Y/%m/%d %H:%M")
    m.datetime = datetime.datetime.strptime("2018/10/29 00:00", "%Y/%m/%d %H:%M")
    m.is_image = False
    m.member_id = 13

    settings.mails.append(m)
    database.db_session.add(m)
    database.db_session.commit()

    m = model.Mail()
    m.mail_id = "config/restore"
    m.subject = "백업 불러오기"
    m.preview = "서비스 이용을 위해 pm.json을 등록해주세요."
    m.content = "서비스 이용을 위해 pm.json을 등록해주세요."
    m.time = datetime.datetime.strptime("2018/10/29 00:00", "%Y/%m/%d %H:%M")
    m.datetime = datetime.datetime.strptime("2018/10/29 00:00", "%Y/%m/%d %H:%M")
    m.is_image = False
    m.member_id = 13

    settings.mails.append(m)
    database.db_session.add(m)
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
        m.preview = mail["preview"][:80]
        m.content = mail["body"]
        m.time = datetime.datetime.strptime(mail["time"], "%Y/%m/%d %H:%M")
        m.datetime = datetime.datetime.strptime(mail["time"], "%Y/%m/%d %H:%M")
        m.is_image = mail["image"]
        m.member_id = m_dict[mail["member"]]

        members[m_dict[mail["member"]]].mails.append(m)
         
        database.db_session.add(m)
    database.db_session.commit()

def load_img(img_data):
    members = model.Member.query.all()
    for image in img_data:
        i = model.Image()
        
        i.image_url = image["image_url"]
        i.thumbnail_image_url = image["thumbnail_image_url"]
        
        m = model.Mail.query.filter(model.Mail.mail_id == image["mail_id"]).first()
        if not m:
            database.db_session.rollback()
            print("?")
            break
        
        i.mail_id = m.id
        i.member_id = m.member_id
        i.receive_datetime = m.time

        m.images.append(i)
        m.member.images.append(i)

        database.db_session.add(i)
    database.db_session.commit()


def test_db():
    u = model.User()
    u.user_id = "AAAABBBBCCCCDDDD"
    u.access_token = "ABCDABCDABCDABCD"
    u.nickname = "테스트"
    u.gender = "male"
    u.country_code = "KR"
    u.prefecture_id = -1
    u.birthday = "20181029"
    u.member_id = 1

    database.db_session.add(u)
    database.db_session.commit()

def all_pm(user):
    user.mails = []
    for m in model.Mail.query.all():
        user.mails.append(m)
    user.clear_read()
    database.db_session.commit()

def init():
    api_init()
