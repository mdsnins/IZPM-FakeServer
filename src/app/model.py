from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, desc
from sqlalchemy.orm import relationship, backref

from .database import Base, db_session

class User(Base):
    __tablename__ = "USER"
    
    user_id = Column(String(32), primary_key = True)
    access_token = Column(String(32), unique = False)
    nickname = Column(String(96), unique = False)
    gender = Column(String(8), unique = False)
    country_code = Column(String(2), unique = False)
    prefecture_id = Column(Integer, unique = False)
    birthday = Column(String(8), unique = False)
    member_id = Column(Integer, unique = False)

    member_names = Column(String(480), unique = False)
    member_unreads = Column(String(84), unique = False)
    member_stars = Column(String(84), unique = False)
    member_images = Column(String(84), unique = False)

    mails = relationship('Mail', secondary = "MAIL_AVAIL", lazy = "dynamic")  # User readable mails
    images = relationship('Image', secondary = "IMAGE_AVAIL", lazy = "dynamic") # User viewable images

    reads = relationship('Mail', secondary = "MAIL_READ")
    stars = relationship('Mail', secondary = "MAIL_STAR")
    favorites = relationship('Image', secondary = "IMAGE_FAVORITE", lazy = "dynamic") # User favorite images
    
    configs = relationship("Config", cascade="delete", backref="user")
    
    m_names = []
    m_unreads = []
    m_stars = []
    m_images = []

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
        self.member_images ="-|0|0|0|0|0|0|0|0|0|0|0|0"

    def clear_read(self):
        self.m_unreads = [0] * 13
        for mail in self.mails:
            if mail.member_id > 12:
                continue
            if mail in self.reads:
                continue
            self.m_unreads[mail.member_id] += 1
            self.m_unreads[0] += 1
        self.member_unreads = '|'.join([str(x) for x in self.m_unreads])
        db_session.commit()

    def resolve_images(self):
        self.m_images = [0] * 13
        for mail in self.mails:
            for image in mail.images:
                if image.member_id > 12:
                    continue
                self.m_images[mail.member_id] += 1
                self.images.append(image)
        self.member_images = '|'.join([str(x) for x in self.m_images])
        db_session.commit()

    def change_name(self, member_id, name):
        if not (1 <= member_id and member_id <= 12):
            return -1 # member_id error
        if '|' in name:
            return -2 # name invalid char

        self.m_names[member_id] = name
        self.member_names = '|'.join(self.m_names)
        db_session.commit()
        return 0

    def read_mail(self, id):
        mail = Mail.query.get(id)
        
        if not mail:
            return -1 # Error

        if mail in self.reads:
            return 0 # Already read

        self.reads.append(mail)
        self.m_unreads[mail.member_id] -= 1
        self.m_unreads[0] -= 1
        self.member_unreads = '|'.join([str(x) for x in self.m_unreads])
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
        self.member_stars = '|'.join([str(x) for x in self.m_stars])
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
        self.member_stars = '|'.join([str(x) for x in self.m_stars])
        db_session.commit()
        return 1 # Successfully processed

    def star_image(self, id):
        image = Image.query.get(id)
        
        if not image:
            return -1 # Error

        if image in self.favorites:
            return 0 # Already starrerd

        self.favorites.append(image)
        db_session.commit()
        return 1
        
    def unstar_image(self, id):
        image = Image.query.get(id)
        
        if not image:
            return -1 # Error

        if image in self.favorites:
            return 0 # Already starrerd

        self.favorites.remove(image)
        db_session.commit()
        return 1

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
    
    def is_favorite(self, image):
        if not image:
            return False
        return image in self.favorites

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

    id = Column(Integer, primary_key = True, autoincrement=True)
    realname_ko = Column(String(36), unique = False)
    realname_th = Column(String(36), unique = False)
    realname_in = Column(String(36), unique = False)
    image_url = Column(String(256), unique = False)

    mails = relationship("Mail", cascade="delete", backref="member")
    images = relationship("Image", backref="member", lazy="dynamic")

    def __init__(self, id, name, name_global, image_url):
        self.id = id
        self.realname_ko = name
        self.realname_th = name_global
        self.realname_in = name_global
        self.image_url = image_url

class Mail(Base):
    __tablename__ = "MAIL"

    id = Column(Integer, primary_key = True, autoincrement=True)
    mail_id = Column(String(32), unique = True)
    subject = Column(String(240), unique = False)
    preview = Column(String(240), unique = False)
    content = Column(Text, unique = False)
    
    member_id = Column(Integer, ForeignKey("MEMBER.id"))

    images = relationship("Image", backref="mail", lazy = "dynamic")

    time = Column(DateTime, unique = False)
    datetime = Column(DateTime, unique = False)
    is_image = Column(Boolean, unique = False)

class Image(Base):
    __tablename__ = "IMAGE"

    id = Column(Integer, primary_key = True, autoincrement=True)
    image_url = Column(String(256), unique = False)
    thumbnail_image_url = Column(String(256), unique = False)
    receive_datetime = Column(DateTime, unique = False)

    member_id = Column(Integer, ForeignKey("MEMBER.id"))
    mail_id = Column(Integer, ForeignKey("MAIL.id"))

class Config(Base):
    __tablename__ = "CONFIG"
    id = Column(Integer, primary_key = True, autoincrement=True)
    user_id = Column(String(16), ForeignKey("USER.user_id"))
    key = Column(String(32), unique = False)
    value = Column(String(96), unique = False)

# Association Tables
class MailSubscribes(Base):
    __tablename__ = "MAIL_AVAIL"
    id = Column(Integer, primary_key = True, autoincrement=True)
    uid = Column(String(32), ForeignKey("USER.user_id"))
    mid = Column(Integer, ForeignKey("MAIL.id"))

class ImageSubscribes(Base):
    __tablename__ = "IMAGE_AVAIL"
    id = Column(Integer, primary_key = True, autoincrement=True)
    uid = Column(String(32), ForeignKey("USER.user_id"))
    iid = Column(Integer, ForeignKey("IMAGE.id"))

class MailReads(Base):
    __tablename__ = "MAIL_READ"
    id = Column(Integer, primary_key = True, autoincrement=True)
    uid = Column(String(32), ForeignKey("USER.user_id"))
    mid = Column(Integer, ForeignKey("MAIL.id"))

class MailStars(Base):
    __tablename__ = "MAIL_STAR"
    id = Column(Integer, primary_key = True, autoincrement=True)
    uid = Column(String(32), ForeignKey("USER.user_id"))
    mid = Column(Integer, ForeignKey("MAIL.id"))

class ImageFavorites(Base):
    __tablename__ = "IMAGE_FAVORITE"
    id = Column(Integer, primary_key = True, autoincrement=True)
    uid = Column(String(32), ForeignKey("USER.user_id"))
    iid = Column(Integer, ForeignKey("IMAGE.id"))


