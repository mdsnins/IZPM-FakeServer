import json
import random
import datetime
from functools import wraps
from flask import Flask, render_template, request, url_for, redirect, Blueprint, send_from_directory
from sqlalchemy import desc
from . import config
from .model import *
from .database import db_session

router = Blueprint("api", __name__, subdomain = config.API_SUBDOMAIN)

MEMBER_INDEX = [7, 2, 8, 4, 12, 10, 11, 6, 9, 3, 5, 1]
members = []

def error(code, name, message, id = "#B-0000-0000"):
    return json.dumps({
        "error": {
            "data": {
                "id": id,
                "code": code,
                "name": name,
                "message": message
            }
        }
    }, ensure_ascii = False), code, {'Content-Type': 'application/json; charset=UTF-8;'}

def get_user():
    u = User.query.get(request.headers.get("User-Id", ""))
    if not u or u.access_token != request.headers.get("Access-Token", ""):
        return None

    u.m_names   = u.member_names.split('|') # Explode from string value
    u.m_unreads = [int(x) for x in u.member_unreads.split('|')] # Explode from string value
    u.m_stars   = [int(x) for x in u.member_stars.split('|')]
    
    return u

def generate_mails(mails):
    result = []
    user = get_user()
    for mail in mails:
        member = dict(mail.member.__dict__)
        if "_sa_instance_state" in member:
            member.pop("_sa_instance_state", None)
        if "mails" in member:
            member.pop("mails", None)
        t = {
            "member": member,
            "group": {"id":3, "name": "IZ*ONE"},
            "id": mail.mail_id,
            "subject": mail.subject, "subject_ko": mail.subject, "subject_in": mail.subject, "subject_th": mail.subject, 
            "content": mail.content, "content_ko": mail.content, "content_in": mail.content, "content_th": mail.content, 
            "receive_time": mail.time.strftime("%Y/%m/%d %H:%M"),
            "receive_datetime": mail.time.strftime("%Y/%m/%d %H:%M:%S"),
            "detail_url": "{}/{}".format(config.DETAIL_PREFIX, mail.mail_id), "detail_url_ko": "{}/{}".format(config.DETAIL_PREFIX, mail.mail_id), "detail_url_in": "{}/{}".format(config.DETAIL_PREFIX, mail.mail_id), "detail_url_th": "{}/{}".format(config.DETAIL_PREFIX, mail.mail_id), 
            "is_unread": not user.is_read(mail.mail_id),
            "is_star": user.is_read(mail.mail_id), 
            "is_image": mail.is_image
        }
        t["member"]["name"] = user.m_names[mail.member.id]
        result.append(t)
    return result

def generate_json(object):
    return json.dumps(object, ensure_ascii = False), 200, {'Content-Type': 'application/json; charset=UTF-8;'}

def random_alphanumeric(length):
    return ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=length))

# auth require decorator
def require_auth(endpoint):
    @wraps(endpoint)

    def check(*args, **kwargs):
        if not get_user():
            return error(401, "AuthorizationError", "인증 오류")
        else:
            return endpoint(*args, **kwargs)
    
    return check

@router.before_app_first_request
def api_init():
    global members
    members = Member.query.all()

@router.route("/users", methods = ["GET", "POST", "PATCH"])
def users():
    if request.method == "GET" or request.method == "PATCH":
        user = get_user()
        if not user:
            return error(401, "AuthorizationError", "인증 오류")
        if request.method == "PATCH":
            bday = request.form.get("birthday", "")
            ccode = request.form.get("country_code", "")
            pfid = request.form.get("prefecture_id", "-1")
            gender = request.form.get("gender", "")
            member_id = request.form.get("member_id", "")
            nickname = request.form.get("nickname", "")
            
            # PATCH data validation
            try:
                if bday != "":
                    datetime.datetime.strptime(bday, "%Y%m%d") #try parse as datetime
                if ccode != "":
                    if ccode == "JP":
                        pfid = int(pfid)
                        if pfid < 1 or pfid > 47:
                            return error(403, "ValueError", "값 오류")
                    elif ccode in ["KR", "TH", "IN"]:
                        pfid = -1
                    else:
                        return error(403, "ValueError", "값 오류")
                if gender != "" and not gender in ["male", "female"]:
                    return error(403, "ValueError", "값 오류")
                if member_id != "":
                    t = int(member_id)
                    if t < 1 or t > 12:
                        return error(403, "ValueError", "값 오류")
                if len(nickname) > 32:
                    return error(403, "ValueError", "값 오류")
            except Exception as e:
                return error(403, "ValueError")
            
            # data update
            if bday != "" and user.birthday == "": # Birthday shouldn't be able to be updated
                user.birthday = bday 
            if ccode != "":
                user.country_code = ccode
                user.prefecture_id = pfid
            if gender != "":
                user.gender = gender
            if member_id != "":
                user.member_id = member_id
            if nickname != "":
                user.nickname = nickname
            
            db_session.commit()

        return generate_json({
            "user": {
                "id": user.user_id,
                "access_token": user.access_token,
                "nickname": user.nickname,
                "gender": user.gender,
                "country_code": user.country_code,
                "prefecture_id": user.prefecture_id,
                "birthday": user.birthday,
                "member_id": user.member_id
            }
        })

    elif request.method == "POST":
        u = User()
        u.user_id = random_alphanumeric(12)
        u.access_token = random_alphanumeric(24)
        db_session.add(u)
        db_session.commit()

        return generate_json({
            "user": {
                "id": u.user_id,
                "access_token": u.access_token
            }
        })
    else:
        return error(405, "RequestError", "요청 오류")

@router.route("/application_settings", methods = ["GET", "PATCH"])
def application_settings():
    return generate_json({
        "application_settings": {
            "is_mail_notice": False,
            "is_vibration": False,
            "is_sound": False
        }
    })

@router.route("/informations")
@require_auth
def informations():
    #TODO: implement information management from admin console, not important for now
    return generate_json({
        "informations": []
    })

@router.route("/inbox")
@require_auth
def inbox():
    is_information = request.args.get("is_information")
    #drop group_id; not used in IZ*ONE PM
    is_star = request.args.get("is_star", "0")
    is_unread = request.args.get("is_unread", "0")
    member_id = request.args.get("member_id", "0") # 0 for everyone
    user = get_user()
    page = request.args.get("page", "0")

    try:
        page = int(page)
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    try:
        member_id = int(member_id)
        if member_id < 0 or member_id > 12:
            member_id = 0
    except ValueError:
        member_id = 0

    mails = []
    
    if member_id == 0:
        mails = Mail.query.order_by(desc(Mail.datetime)).all()
    else:
        mails = member[member_id].mails
    
    if is_star != "0" and is_star != "false":
        mails = [m for m in mails if user.is_star(m.id)]
    if is_unread != "0" and is_star != "false":
        mails = [m for m in mails if not user.is_read(m.id)]
    
    total = len(mails)
    mails = mails[(page - 1)*20:page*20]
    return generate_json({
        "mail_count": len(mails),
        "page": page,
        "has_next_page": page*20 < total,
        "unread_count": user.m_unreads[member_id],
        "star_count": user.m_stars[member_id],
        "mails": generate_mails(mails)
    })

@router.route("/menu")
@require_auth
def menu():
    user = get_user()
    return generate_json({
        "all_unread_count": user.m_unreads[0],
        "notification_unread_count": 0,
        "unread_count": user.m_unreads[0],
        "star_count": 0,
        "read_later_count": 0,
        "receiving_members": [{
            "unread_count": user.m_unreads[0],
            "group": {
                "id": 1,
                "name": "설정 중"
            },
            "team_members": [{
                "team_name": "IZ*ONE",
                "members": [
                    {
                        "member": {
                            "id": i,
                            "name": user.m_names[i],
                            "image_url": members[i].image_url
                        },
                        "unread_count": user.m_unreads[i]
                    } for i in MEMBER_INDEX
                ]
            }]
        }],
    })

@router.route("/menu_informations")
@require_auth
def menu_informations():
    return generate_json({})

@router.route("/members")
def join_members():
    return generate_json({
        "group_count": 1,
        "all_members": [{
            "group":{
                "id": 3,
                "name": "IZ*ONE"
            },
            "team_members": [{
                "team_name": "IZ*ONE",
                "members": [
                    {
                        "id": i,
                        "name": members[i].realname_ko,
                        "image_url": members[i].image_url
                    } for i in MEMBER_INDEX
                ]
            }]
        }]
    })

@router.route("/countries")
def join_countries():
    return '{"countries":{"IN":{"name":"인도네시아","prefecture_list":{}},"TH":{"name":"태국","prefecture_list":{}},"KR":{"name":"대한민국","prefecture_list":{}},"JP":{"name":"일본","prefecture_list":{"1":"홋카이도","2":"아오모리켄","3":"이와테켄","4":"미야기켄","5":"아키타켄","6":"야마가타켄","7":"후쿠시마켄","8":"이바라키켄","9":"토치기켄","10":"군마켄","11":"사이타마켄","12":"치바켄","13":"도쿄도","14":"가나가와켄","15":"니가타켄","16":"도야마켄","17":"이시카와켄","18":"후쿠이켄","19":"야마나시켄","20":"나가노켄","21":"기후켄","22":"시즈오카켄","23":"아이치켄","24":"미에켄","25":"시가켄","26":"교토부","27":"오사카부","28":"효고켄","29":"나라켄","30":"와카야마켄","31":"돗토리켄","32":"시마네켄","33":"오카야마켄","34":"히로시마켄","35":"야마구치켄","36":"도쿠시마켄","37":"가가와켄","38":"에히메켄","39":"고치켄","40":"후쿠오카켄","41":"사가켄","42":"나가사키켄","43":"구마모토켄","44":"오이타켄","45":"미야자키켄","46":"가고시마켄","47":"오키나와켄"}}},"sort":["JP","KR","TH","IN"]}', 200, {"Content-Type": "application/json"}
