import json
from flask import Flask, render_template, request, url_for, redirect, Blueprint, send_from_directory
from sqlalchemy import desc
from . import config
from .model import *

router = Blueprint("api", __name__, subdomain = config.API_SUBDOMAIN)
members = []

def api_init():
    global members
    members = Member.query.all()

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
    }, ensure_ascii = False), code, {'Content-Type': 'application/json'}

def get_user():
    u = User.query.get(request.headers.get("User-Id", ""))
    if not u:
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

@router.before_request
def auth_header():
    if not get_user():
        return error(401, "AuthorizationError", "인증 오류")

@router.route("/users", methods = ["GET", "POST"])
def users():
    user = get_user()
    return json.dumps({
        "user": {
            "id": user.user_id,
            "access_token": "000000000000000000000000",
            "nickname": user.nickname,
            "gender": user.gender,
            "country_code": user.country_code,
            "prefecture_id": user.prefecture_id,
            "birthday": user.birthday,
            "member_id": user.member_id
        }
    }), 200, {'Content-Type': 'application/json'}

@router.route("/application_settings")
def application_settings():
    return json.dumps({
        "application_settings": {
            "is_mail_notice": False,
            "is_vibration": False,
            "is_sound": False
        }
    }, ensure_ascii = False), 200, {'Content-Type': 'application/json'}

@router.route("/informations")
def informations():
    #TODO: implement information management from admin console, not important for now
    return json.dumps({
        "informations": []
    }, ensure_ascii = False), 200, {'Content-Type': 'application/json'}

@router.route("/inbox")
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
    return json.dumps({
        "mail_count": len(mails),
        "page": page,
        "has_next_page": page*20 < total,
        "unread_count": user.m_unreads[member_id],
        "star_count": user.m_stars[member_id],
        "mails": generate_mails(mails)
    }, ensure_ascii = False), 200, {'Content-Type': 'application/json'}

@router.route("/menu")
def menu():
    user = get_user()
    return json.dumps({
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
                "members": [{
                    "member": {
                        "id": 7,
                        "name": user.m_names[7],
                        "image_url": members[7].image_url
                    },
                    "unread_count": user.m_unreads[7]
                }, {
                    "member": {
                        "id": 2,
                        "name": user.m_names[2],
                        "image_url": members[2].image_url
                    },
                    "unread_count": user.m_unreads[2]
                }, {
                    "member": {
                        "id": 8,
                        "name": user.m_names[8],
                        "image_url": members[8].image_url
                    },
                    "unread_count": user.m_unreads[8]
                }, {
                    "member": {
                        "id": 4,
                        "name": user.m_names[4],
                        "image_url": members[4].image_url
                    },
                    "unread_count": user.m_unreads[4]
                }, {
                    "member": {
                        "id": 12,
                        "name": user.m_names[12],
                        "image_url": members[12].image_url
                    },
                    "unread_count": user.m_unreads[12]
                }, {
                    "member": {
                        "id": 10,
                        "name": user.m_names[10],
                        "image_url": members[10].image_url
                    },
                    "unread_count": user.m_unreads[10]
                }, {
                    "member": {
                        "id": 11,
                        "name": user.m_names[11],
                        "image_url": members[11].image_url
                    },
                    "unread_count": user.m_unreads[11]
                }, {
                    "member": {
                        "id": 7,
                        "name": user.m_names[7],
                        "image_url": members[7].image_url
                    },
                    "unread_count": user.m_unreads[7]
                }, {
                    "member": {
                        "id": 6,
                        "name": user.m_names[6],
                        "image_url": members[6].image_url
                    },
                    "unread_count": user.m_unreads[6]
                }, {
                    "member": {
                        "id": 9,
                        "name": user.m_names[9],
                        "image_url": members[9].image_url
                    },
                    "unread_count": user.m_unreads[9]
                }, {
                    "member": {
                        "id": 3,
                        "name": user.m_names[3],
                        "image_url": members[3].image_url
                    },
                    "unread_count": user.m_unreads[3]
                }, {
                    "member": {
                        "id": 5,
                        "name": user.m_names[5],
                        "image_url": members[5].image_url
                    },
                    "unread_count": user.m_unreads[5]
                }, {
                    "member": {
                        "id": 1,
                        "name": user.m_names[1],
                        "image_url": members[1].image_url
                    },
                    "unread_count": user.m_unreads[1]
                }]
            }]
        }],
    }, ensure_ascii = False), 200, {'Content-Type': 'application/json'}

@router.route("/menu_informations")
def menu_informations():
    return json.dumps({}, ensure_ascii = False), 200, {'Content-Type': 'application/json'}
