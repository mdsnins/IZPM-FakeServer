import base64
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
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

    if cid == "member_name":
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
    elif cid == "restore":
        cipher = AES.new(config.CRYPTO_KEY, AES.MODE_ECB)
        payload = (str(int(time.time())) + "|" + request.headers.get("User-Id") + "|" + request.headers.get("Access-Token")).encode()
        payload = cipher.encrypt(pad(payload, 16))
        payload = base64.b64encode(payload).decode().replace("+", ".")
        link = url_for("web.user_register", _external = True) + "?token=" + payload
        return render_template("config/restore.html", link = link)

@router.route("/register", methods = ["GET", "POST"])
def user_register():
    token = request.args.get("token", "")
    if token == "":
        return render_template("config/restore_register.html", err = "잘못된 접근입니다.")

    cipher = AES.new(config.CRYPTO_KEY, AES.MODE_ECB)
    uid, at = "", ""
    try:
        payload = base64.b64decode(token.replace(".", "+"))
        payload = unpad(cipher.decrypt(payload), 16).decode()
        pt = payload.split("|") 

        ts = int(pt[0])
        if time.time() - ts > 1800:
            return render_template("config/restore_register.html", err = "만료된 링크입니다.")
        uid, at = pt[1], pt[2]
    except Exception as e:
        print(e)
        return render_template("config/restore_register.html", err = "잘못된 접근입니다.")
    

    user = get_user(user_id = uid, access_token = at)
    if not user:
        return render_template("config/restore_register.html", err = "올바르지 않은 계정입니다.")

    if request.method == "GET":
        return render_template("config/restore_register.html", nick = user.nickname, token = token)
    
    pm_data = json.loads(request.files['pmfile'].read())
    user.mails = []
    db_session.commit()
    
    for m in Mail.query.filter_by(member_id = 13).all():
        user.mails.append(m)
        db_session.commit()

    db_session.commit()
    processed = 0
    skipped = []
    mid = ""
    try:
        for pm in pm_data:
            mid = pm["id"]
            if pm["member"] == "운영팀" or mid[0] == "b":
                continue
            m = Mail.query.filter_by(mail_id = mid).one()
            if not m:
                skipped.append(mid)
                continue
            user.mails.append(m)
            db_session.commit()
            processed += 1

    except Exception as e:
        print(e)
        return render_template("config/restore_register.html", err = "{} 처리 중 에러가 발생하였습니다.<br>{}".format(mid, e))

    request.files['pmfile'].save("{}/{}.js".format(config.PMJS_PATH, uid))
    user.clear_read()

    if len(skipped) > 0:
        return render_template("config/restore_register.html",
                                msg = "{}개의 메일을 등록하였습니다.".format(processed),
                                warn = "{}개의 메일은 실패하였습니다.<br>관리자에게 연락 바랍니다.<br>세부사항 : {}".format(len(skipped), ','.join(skipped)))
    
    return render_template("config/restore_register.html", msg = "{}개의 메일을 등록하였습니다!".format(processed))
      

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
        if key == "read_clear":
            u.clear_read()
            return generate_json({"code": 200, "msg": "success"})

        if c:
            c.value = v
            db_session.commit()
            return generate_json({"code": 200, "msg": "success"})

        c = Config()
        c.key = key
        c.value = v
        db_session.add(c)
        u.configs.append(c)
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
