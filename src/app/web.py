from flask import Flask, render_template, request, url_for, redirect, Blueprint, send_from_directory, send_file
from . import config
from .model import *

router = Blueprint("web", __name__, subdomain = config.WEB_SUBDOMAIN)
members = []

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
    