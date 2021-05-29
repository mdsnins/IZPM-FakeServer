import json
import re
import random
from functools import wraps
from datetime import datetime, timedelta
from .model import *
from . import config

single_date = re.compile("([0-9]{8})(.*)?")
double_date = re.compile("([0-9]{8})\-([0-9]{8})(.*)?")

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

def generate_json(object):
    return json.dumps(object, ensure_ascii = False), 200, {'Content-Type': 'application/json; charset=UTF-8;'}

def random_alphanumeric(length):
    return ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=length))

def resolve_name(body, name, postposition = False):
    if not postposition:
        return re.sub('\<(($)|위)즈?원?(>|$)', name, body)
    
    # If postposition replacement is enabled, check name first
    replace_flag = True
    last = ord(name[-1]) - 44032
    if last < 0 or 11171 < last:   # If not Korean
        replace_flag = False
    elif last % 28 == 0:
        replace_flag = False   # No last letter

    while True:
        i = body.find("<위즈원>")
        if i < 0:
            break
        
        try:
            if body[i+5] in ["이", "가"] and body[i+6] == " ":
                body = body[:i] + name +  ("이" if replace_flag else "가") + body[i+6:]
            elif body[i+5] in ["을", "를"] and body[i+6] == " ":
                body = body[:i] + name +  ("을" if replace_flag else "를") + body[i+6:]
            elif body[i+5] in ["은", "는"] and body[i+6] == " ":
                body = body[:i] + name + ("은" if replace_flag else "는") + body[i+6:]
            else:
                body = body[:i] + name + body[i+5:]    
        except: # To handle exception at the very last of the letter
            body = body[:i] + name + body[i+5:]

    return re.sub('\<(($)|위)즈?원?(>|$)', name, body) #Process rest

def parse_search_query(q):
    if q == "":
        return {}
    
    res = {}
    if q[0] == "!":
        res["reverse"] = True
        q = q[1:]

    try:
        t = double_date.match(q)
        if t != None:
           res.update({
               "begin": datetime.strptime(t.groups()[0], "%Y%m%d"),
               "end": datetime.strptime(t.groups()[1], "%Y%m%d") + timedelta(days = 1),
               "q": t.groups()[2].strip() if len(t.groups()) == 3 else ""
           })
        else:
            t = single_date.match(q)
            if t != None:
                res.update({
                    "begin": datetime.strptime(t.groups()[0], "%Y%m%d"),
                    "end": datetime.strptime(t.groups()[0], "%Y%m%d") + timedelta(days = 1),
                    "q": t.groups()[1].strip() if len(t.groups()) == 2 else ""
                })
            else:
                res["q"] = q
    except Exception as e:
        res["q"] = q
    finally:
        return res
        
def get_image_preview(image):
    if not image:
        return [config.NO_IMAGE, config.NO_IMAGE]
    else:
        return [config.IMAGE_PREFIX + image.image_url, config.IMAGE_PREFIX + image.image_url]

def datetojp(dt):
    return dt.strftime("%Y年%-m月%-d日")