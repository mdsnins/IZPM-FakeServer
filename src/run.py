import json
from sys import argv
from app import *

if __name__ == "__main__":
    if argv[1] == "run":
        init()
        app.run(host = "0.0.0.0", port = 1000, debug = True)
    elif argv[1] == "initdb":
        init_db()
    elif argv[1] == "testdb":
        test_db()
    elif argv[1] == "loadpm":
        f = open("pm.js", "r")
        raw = f.read()[14:]
        f.close()
        load_pm(json.loads(raw))
    elif argv[1] == "debug":
        import code
        code.interact(local=locals())
