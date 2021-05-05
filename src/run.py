from sys import argv
from app import *

if __name__ == "__main__":
    if argv[1] == "run":
        app.run(host = "0.0.0.0", port = 10000, debug = True)
    elif argv[1] == "initdb":
        init_db()
    elif argv[1] == "testdb":
        test_db()