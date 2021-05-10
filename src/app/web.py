from flask import Flask, render_template, request, url_for, redirect, Blueprint, send_from_directory, send_file
from . import config
from .model import *
from .tool import *

router = Blueprint("web", __name__, subdomain = config.WEB_SUBDOMAIN)
members = []

def get_user():
    u = User.query.get(request.headers.get("User-Id", ""))
    if not u or u.access_token != request.headers.get("Access-Token", ""):
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

# Mail
@router.route("/mail/<mid>")
def inbox_read(mid):
    user = get_user()
    if not user:
        return error(401, "AuthorizationError", "인증 오류")

    if mid == "config":
        # Move to config page
        return user_config(user)

    mail = Mail.query.get(mid)
    if not mail:
        return error(401, "MailError", "접근 오류")

    #TODO: implement
    pass

# Config page
def user_config(user):
    # Configurations: Postposition replacement setting
    pass