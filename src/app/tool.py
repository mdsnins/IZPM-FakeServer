import json
import random
from functools import wraps
from .model import *

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