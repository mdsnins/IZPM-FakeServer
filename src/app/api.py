import json
from flask import Flask, render_template, session, request, url_for, redirect, Blueprint, send_from_directory
import .config

router = Blueprint("api", __name__)
members = [
    {},
    {"id": 1, "realname_ko": "장원영", "realname_th": "JANG WON YOUNG", "realname_in": "JANG WON YOUNG", "image_url": config.IMAGE_PREFIX + "/1.jpg"},
    {"id": 2, "realname_ko": "미야와키 사쿠라", "realname_th": "MIYAWAKI SAKURA", "realname_in": "MIYAWAKI SAKURA", "image_url": config.IMAGE_PREFIX + "/2.jpg"},
    {"id": 3, "realname_ko": "조유리", "realname_th": "JO YU RI", "realname_in": "JO YU RI", "image_url": config.IMAGE_PREFIX + "/3.jpg"},
    {"id": 4, "realname_ko": "최예나", "realname_th": "CHOI YE NA", "realname_in": "CHOI YE NA", "image_url": config.IMAGE_PREFIX + "/4.jpg"},
    {"id": 5, "realname_ko": "안유진", "realname_th": "AN YU JIN", "realname_in": "AN YU JIN", "image_url": config.IMAGE_PREFIX + "/5.jpg"},
    {"id": 6, "realname_ko": "야부키 나코", "realname_th": "YABUKI NAKO", "realname_in": "YABUKI NAKO", "image_url": config.IMAGE_PREFIX + "/6.jpg"},
    {"id": 7, "realname_ko": "권은비", "realname_th": "KWON EUN BI", "realname_in": "KWON EUN BI", "image_url": config.IMAGE_PREFIX + "/7.jpg"},
    {"id": 8, "realname_ko": "강혜원", "realname_th": "KANG HYE WON", "realname_in": "KANG HYE WON", "image_url": config.IMAGE_PREFIX + "/8.jpg"},
    {"id": 9, "realname_ko": "혼다 히토미", "realname_th": "HONDA HITOMI", "realname_in": "HONDA HITOMI", "image_url": config.IMAGE_PREFIX + "/9.jpg"},
    {"id": 10, "realname_ko": "김채원", "realname_th": "KIM CHAE WON", "realname_in": "KIM CHAE WON", "image_url": config.IMAGE_PREFIX + "/10.jpg"},
    {"id": 11, "realname_ko": "김민주", "realname_th": "KIM MIN JU", "realname_in": "KIM MIN JU", "image_url": config.IMAGE_PREFIX + "/11.jpg"},
    {"id": 12, "realname_ko": "이채연", "realname_th": "LEE CHAE YEON", "realname_in": "LEE CHAE YEON", "image_url": config.IMAGE_PREFIX + "/12.jpg"},
]

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
    }), code

def generate_mails(mails):
    result = []
    for mail in mails:
        t = {
            "member": members[mail.member_id],
            "group": {"id":3, "name": "IZ*ONE"},
            "id": mail.mail_id,
            "subject": mail.subject, "subject_ko": mail.subject, "subject_in": mail.subject, "subject_th": mail.subject, 
            "content": mail.content, "content_ko": mail.content, "content_in": mail.content, "content_th": mail.content, 
            "receive_time": mail.time,
            "receive_datetime": mail.datetime,
            "detail_url": "{}/{}".format(config.DETAIL_PREFIX, mail.mail_id), "detail_url_ko": "{}/{}".format(config.DETAIL_PREFIX, mail.mail_id), "detail_url_in": "{}/{}".format(config.DETAIL_PREFIX, mail.mail_id), "detail_url_th": "{}/{}".format(config.DETAIL_PREFIX, mail.mail_id), 
            "is_unread": not session["user"].is_read(mail.mail_id),
            "is_star": session["user"].is_read(mail.mail_id), 
            "is_image": mail.is_image
        }
        t["member"]["name"] = session["user"].m_names[mail.member_id]
        result.append(t)
    return result

@router.before_request
def auth_header():
    session["user_id"] = request.headers.get("User-Id", "")
    if session["user"].user_id != session["user_id"]:
        session["user"] = User.query.get(user_id)
    
    if not session["user_id"] or not session["user"]:
        error(401, "AuthorizationError", "인증 오류")

    session["user"].m_names   = session["user"].member_names.split('|') # Explode from string value
    session["user"].m_unreads = [int(x) for x in session["user"].member_unreads.split('|')] # Explode from string value

@router.route("/users")
def users():
    return json.dumps({
        "user": {
            "id": session["user"].user_id,
            "access_token": "000000000000000000000000",
            "nickname": session["user"].nickname,
            "gender": session["user"].gender,
            "country_code": session["user"].country_code,
            "prefecture_id": session["user"].prefecture_id,
            "birthday": session["user"].birthday,
            "member_id": session["user"].member_id
        }
    })

@router.route("/application_settings")
def application_settings():
    return json.dumps({
        "application_settings": {
            "is_mail_notice": False,
            "is_vibration": False,
            "is_sound": False
        }
    })

@router.route("/informations")
def informations():
    #TODO: implement information management from admin console, not important for now
    return json.dumps({
        "informations": []
    })

@router.route("/inbox")
def inbox():
    is_information = request.args.get("is_information")
    is_star = request.args.get("is_star")
    is_unread = request.args.get("is_unread")
    page = request.args.get("page")
    try:
        page = int(page)
        if page < 1:
            page = 1
    except ValueError:
        page = 1


    mails = Mail.query.order_by(desc(mail.mail_id)).paginate(page, 20, False)

    #TODO: processing mail data
    return json.dumps({
        "mail_count": 20,
        "page": page,
        "has_next_page": len(mails) == 20,
        "unread_count": session["user"].all_unread_count, #Unread count and star count should be managed in User model
        "star_count": session["user"].star_count,
        "mails": generate_mails(mails)
    })

@router.route("/menu")
def menu():
    return json.dumps({
        "all_unread_count": session["user"].all_unread_count,
        "notification_unread_count": session["user"].notification_unread_count,
        "unread_count": session["user"].all_unread_count,
        "star_count": 0,
        "read_later_count": 0,
        "receiving_members": [{
            "unread_count": session["user"].all_unread_count,
            "group": {
                "id": 1,
                "name": "설정 중"
            },
            "team_members": [{
                "team_name": "IZ*ONE",
                "members": [{
                    "member": {
                        "id": 7,
                        "name": session["user"].m_names[7],
                        "image_url": members[7]["image_url"]
                    },
                    "unread_count": session["user"].m_unreads[7]
                }, {
                    "member": {
                        "id": 2,
                        "name": session["user"].m_names[2],
                        "image_url": members[2]["image_url"]
                    },
                    "unread_count": session["user"].m_unreads[2]
                }, {
                    "member": {
                        "id": 8,
                        "name": session["user"].m_names[8],
                        "image_url": members[8]["image_url"]
                    },
                    "unread_count": session["user"].m_unreads[8]
                }, {
                    "member": {
                        "id": 4,
                        "name": session["user"].m_names[4],
                        "image_url": members[4]["image_url"]
                    },
                    "unread_count": session["user"].m_unreads[4]
                }, {
                    "member": {
                        "id": 12,
                        "name": session["user"].m_names[12],
                        "image_url": members[12]["image_url"]
                    },
                    "unread_count": session["user"].m_unreads[12]
                }, {
                    "member": {
                        "id": 10,
                        "name": session["user"].m_names[10],
                        "image_url": members[10]["image_url"]
                    },
                    "unread_count": session["user"].m_unreads[10]
                }, {
                    "member": {
                        "id": 11,
                        "name": session["user"].m_names[11],
                        "image_url": members[11]["image_url"]
                    },
                    "unread_count": session["user"].m_unreads[11]
                }, {
                    "member": {
                        "id": 7,
                        "name": session["user"].m_names[7],
                        "image_url": members[7]["image_url"]
                    },
                    "unread_count": session["user"].m_unreads[7]
                }, {
                    "member": {
                        "id": 6,
                        "name": session["user"].m_names[6],
                        "image_url": members[6]["image_url"]
                    },
                    "unread_count": session["user"].m_unreads[6]
                }, {
                    "member": {
                        "id": 9,
                        "name": session["user"].m_names[9],
                        "image_url": members[9]["image_url"]
                    },
                    "unread_count": session["user"].m_unreads[9]
                }, {
                    "member": {
                        "id": 3,
                        "name": session["user"].m_names[3],
                        "image_url": members[3]["image_url"]
                    },
                    "unread_count": session["user"].m_unreads[3]
                }, {
                    "member": {
                        "id": 5,
                        "name": session["user"].m_names[5],
                        "image_url": members[5]["image_url"]
                    },
                    "unread_count": session["user"].m_unreads[5]
                }, {
                    "member": {
                        "id": 1,
                        "name": session["user"].m_names[1],
                        "image_url": members[1]["image_url"]
                    },
                    "unread_count": session["user"].m_unreads[1]
                }]
            }]
        }],
    })