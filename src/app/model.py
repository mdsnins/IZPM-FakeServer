from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, desc
from sqlalchemy.orm import relationship, backref

from .database import Base, db_session

class User(Base):
    __tablename__ = "USER"
    
    user_id = Column(String(32), primary_key = True)
    access_token = Column(String(32), unique = False)
    nickname = Column(String(32), unique = False)
    gender = Column(String(8), unique = False)
    country_code = Column(String(2), unique = False)
    prefecture_id = Column(Integer, unique = False)
    birthday = Column(String(8), unique = False)
    member_id = Column(Integer, unique = False)

    member_names = Column(String(180), unique = False)
    member_unreads = Column(String(84), unique = False)
    member_stars = Column(String(84), unique = False)

    reads = relationship('Mail', secondary = "MAIL_READ")
    stars = relationship('Mail', secondary = "MAIL_STAR")
    
    configs = relationship("Config", backref="user")

    m_names = []
    m_unreads = []
    m_stars = []

    def __init__(self):
        self.all_unread_count = 0
        self.star_count = 0

        self.nickname = ""
        self.gender = ""
        self.country_code = ""
        self.prefecture_id = -1
        self.birthday = ""
        self.member_id = 0

        self.member_names = "-||||||||||||"
        self.member_unreads = "0|0|0|0|0|0|0|0|0|0|0|0|0"  # First column is for total
        self.member_stars = "0|0|0|0|0|0|0|0|0|0|0|0|0" # First column is for total

    def change_name(self, member_id, name):
        if not (1 <= member_id and member_id <= 12):
            return -1 # member_id error
        if '|' in name:
            return -2 # name invalid char

        self.m_names[member_id] = name
        self.member_names = '|'.join(self.m_names)

    def read_mail(self, id):
        mail = Mail.query.get(id)
        
        if not mail:
            return -1 # Error

        if mail in self.reads:
            return 0 # Already read

        self.reads.append(mail)
        self.m_unreads[mail.member_id] -= 1
        self.m_unreads[0] -= 1
        self.member_unreads = '|'.join(self.m_unreads)
        db_session.commit()
        return 1 # Successfully processed

    def star_mail(self, id):
        mail = Mail.query.get(id)
        
        if not mail:
            return -1 # Error

        if mail in self.stars:
            return 0 # Already starrerd

        self.stars.append(mail)
        self.m_stars[mail.member_id] += 1
        self.m_stars[0] += 1 
        self.member_stars = '|'.join(self.m_unreads)
        db_session.commit()
        return 1 # Successfully processed

    def unstar_mail(self, id):
        mail = Mail.query.get(id)
        
        if not mail:
            return -1 # Error

        if not mail in self.stars:
            return 0 # not in stars

        self.stars.remove(mail)
        self.m_stars[mail.member_id] -= 1
        self.m_stars[0] -= 1
        self.member_stars = '|'.join(self.m_unreads)
        db_session.commit()
        return 1 # Successfully processed

    def is_read(self, id):
        mail = Mail.query.get(id)
        if not mail:
            return False
        
        return mail in self.reads

    def is_star(self, id):
        mail = Mail.query.get(id)
        if not mail:
            return False
        return mail in self.stars

    def get_config(self, key):
        for c in self.configs:
            if c.key == key:
                return c
        return None

    def get_nickname(self, member_id):
        c = self.get_config("m%d_nick" % member_id)
        if (not c) or (not c.value):
            return self.nickname
        return c.value

class Member(Base):
    __tablename__ = "MEMBER"

    id = Column(Integer, primary_key = True)
    realname_ko = Column(String(12), unique = False)
    realname_th = Column(String(12), unique = False)
    realname_in = Column(String(12), unique = False)
    image_url = Column(String(256), unique = False)

    mails = relationship("Mail", backref="member")

    def __init__(self, id, name, name_global, image_url):
        self.id = id
        self.realname_ko = name
        self.realname_th = name_global
        self.realname_in = name_global
        self.image_url = image_url

class Mail(Base):
    __tablename__ = "MAIL"

    id = Column(Integer, primary_key = True)
    mail_id = Column(String(8), unique = True)
    subject = Column(String(80), unique = False)
    content = Column(String(80), unique = False)
    
    member_id = Column(Integer, ForeignKey("MEMBER.id"))

    time = Column(DateTime, unique = False)
    datetime = Column(DateTime, unique = False)
    is_image = Column(Boolean, unique = False)

class Config(Base):
    __tablename__ = "CONFIG"
    id = Column(Integer, primary_key = True)
    user_id = Column(String(16), ForeignKey("USER.user_id"))
    key = Column(String(32), unique = False)
    value = Column(String, unique = False)

# Association Tables
class MailReads(Base):
    __tablename__ = "MAIL_READ"
    id = Column(Integer, primary_key = True)
    uid = Column(String(32), ForeignKey("USER.user_id"))
    mid = Column(Integer, ForeignKey("MAIL.id"))

class MailStars(Base):
    __tablename__ = "MAIL_STAR"
    id = Column(Integer, primary_key = True)
    uid = Column(String(32), ForeignKey("USER.user_id"))
    mid = Column(Integer, ForeignKey("MAIL.id"))
