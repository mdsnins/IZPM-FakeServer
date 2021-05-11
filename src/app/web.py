from flask import Flask, render_template, request, url_for, redirect, Blueprint, send_from_directory, send_file
from . import config
from .model import *
from .tool import *

router = Blueprint("web", __name__, subdomain = config.WEB_SUBDOMAIN, template_folder = "static/web")
members = []

def get_user(user_id = "", access_token = ""):
    u = User.query.get(request.headers.get("User-Id", user_id))
    if not u or u.access_token != request.headers.get("Access-Token", access_token):
        return None

    u.m_names   = u.member_names.split('|') # Explode from string value
    u.m_unreads = [int(x) for x in u.member_unreads.split('|')] # Explode from string value
    u.m_stars   = [int(x) for x in u.member_stars.split('|')]
    
    return u

# Static files
@router.route("/css/<path:path>")
def getcss(path):
    return send_from_directory("static/css", path)

@router.route("/js/<path:path>")
def getjs(path):
    return send_from_directory("static/js", path)

# About static pages
@router.route("/pages/kiyaku")
def kiyaku():
    return send_file("static/web/kiyaku.html")
    
@router.route("/pages/privacy")
def privacy():
    return send_file("static/web/privacy.html")

@router.route("/pages/tutorial")
def tutorial():
    return send_file("static/web/tutorial.html")

# Config page
@router.route("/mail/config/<cid>")
def user_config(cid):
    user = get_user()
    if not user:
        return error(401, "AuthorizationError", "인증 오류")

    if cid == "m_nick":
        m_nick = ['']
        for i in range(1, 13):
            c = user.get_config("m%d_nick" % i)
            m_nick.append(c.value if c is not None else "")
        return render_template("config/member_name.html", m_nick = m_nick, user_id = request.headers.get("User-Id"), access_token = request.headers.get("Access-Token"))
    elif cid == "common":
        configs = {}
        
        ppos = user.get_config("ppos")
        translate = user.get_config("translate")
        
        configs["ppos"] = ppos.value if ppos else None
        configs["translate"] = translate.value if translate else None

        return render_template("config/common.html", configs = configs, user_id = request.headers.get("User-Id"), access_token = request.headers.get("Access-Token"))
        
# Mail
@router.route("/mail/<mid>")
def inbox_read(mid):
    user = get_user()
    if not user:
        return error(401, "AuthorizationError", "인증 오류")

    mail = Mail.query.filter_by(mail_id = mid).one()
    if not mail:
        return error(401, "MailError", "접근 오류")

    f = open('app/static/web/mail/%s.html' % mail.mail_id, "r")
    body = f.read()
    f.close()

    ppos = user.get_config("ppos")
    ppos = ppos.value if ppos else "0"

    print(body)
    return resolve_name(body, user.get_nickname(mail.member.id), ppos == "1")

# Support Extensions
@router.route("/config/<key>", methods = ["GET", "POST"])
def new_config(key):
    u = get_user(request.args.get("u", ""), request.args.get("t", ""))
    if not u:
        return error(401, "AuthorizationError", "인증 오류")
    v = request.form.get("value", "")
    c = u.get_config(key)

    if request.method == "POST":    
        if c:
            c.value = v
            db_session.commit()
            return generate_json({"code": 200, "msg": "success"})

        c = Config()
        c.key = key
        c.value = v
        u.configs.append(c)

        db_session.add(c)
        db_session.commit()
        return generate_json({"code": 200, "msg": "success"})
    else:
        if c:
            return generate_json({"code": 200, "result": c.value})
        else:
            return generate_json({"code": 200, "result": ""})

@router.route("/config/<key>/remove", methods = ["POST"])
def remove_config(key):
    u = get_user()
    if not u:
        return error(401, "AuthorizationError", "인증 오류")
    c = u.get_config(key)
    if not c:
        return generate_json({"code": 200, "msg": "success"})
        
    db_session.delete(c)
    db_session.commit()
    return generate_json({"code": 200, "msg": "success"})