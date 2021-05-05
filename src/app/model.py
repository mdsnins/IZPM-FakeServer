from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

from .database import Base, db_session

class User(Base):
    __tablename__ = "USER"
    
    id = Column(Integer, primary_key = True)
    user_id = Column(String(32), primary_key = True)
    nickname = Column(String(64), unique = False)
    gender = Column(String(8), unique = False)
    country_code = Column(String(2), unique = False)
    prefecture_id = Column(Integer, unique = False)
    birthday = Column(String(8), unique = False)
    member_id = Column(Integer, unique = False)

    all_unread_count = Column(Integer, unique = False)
    star_count = Column(Integer, unique = False)

    member_names = Column(String(180), unique = False)
    member_unreads = Column(String(84), unique = False)
    member_stars = Column(String(84), unique = False)

    reads = relationship('Mail', secondary = "MAIL_READ")
    stars = relationship('Mail', secondary = "MAIL_STAR")

    m_names = []
    m_unreads = []

    def __init__(self):
        self.all_unread_count = 0
        self.star_count = 0

        self.member_names = "-|장원영|미야와키 사쿠라|조유리|최예나|안유진|야부키 나코|권은비|강혜원|혼다 히토미|김채원|김민주|이채연"
        self.member_unreads = "-1|0|0|0|0|0|0|0|0|0|0|0|0"  # First column is for padding
        self.member_stars = "-1|0|0|0|0|0|0|0|0|0|0|0|0" # First column is for padding

    def read_mail(self, mail_id):
        mail = Mail.query.get(mail_id)
        
        if not mail:
            return -1 # Error

        if mail in self.reads:
            return 0 # Already read

        self.reads.append(mail)
        self.m_unreads[mail.member_id] -= 1
        self.member_unreads = '|'.join(self.m_unreads)
        db_session.commit()
        return 1 # Successfully processed

    def star_mail(self, mail_id):
        mail = Mail.query.get(mail_id)
        
        if not mail:
            return -1 # Error

        if mail in self.stars:
            return 0 # Already starrerd

        self.stars.append(mail)
        self.m_stars[mail.member_id] += 1
        self.member_stars = '|'.join(self.m_unreads)
        db_session.commit()
        return 1 # Successfully processed

    def unstar_mail(self, mail_id):
        mail = Mail.query.get(mail_id)
        
        if not mail:
            return -1 # Error

        if not mail in self.stars:
            return 0 # not in stars

        self.stars.remove(mail)
        self.m_stars[mail.member_id] -= 1
        self.member_stars = '|'.join(self.m_unreads)
        db_session.commit()
        return 1 # Successfully processed

class Mail(Base):
    __tablename__ = "MAIL"

    id = Column(Integer, primary_key = True)
    mail_id = Column(String(8), primary_key = True)
    subject = Column(String(80), unique = False)
    content = Column(String(80), unique = False)
    
    member_id = Column(Integer)

    time = Column(DateTime, unique = False)
    datetime = Column(DateTime, unique = False)
    is_image = Column(Boolean, unique = False)


# Association Tables
class MailReads(Base):
    __tablename__ = "MAIL_READ"
    id = Column(Integer, primary_key = True)
    uid = Column(Integer, ForeignKey("USER.id"))
    mid = Column(Integer, ForeignKey("MAIL.id"))

class MailReads(Base):
    __tablename__ = "MAIL_STAR"
    id = Column(Integer, primary_key = True)
    uid = Column(Integer, ForeignKey("USER.id"))
    mid = Column(Integer, ForeignKey("MAIL.id"))
