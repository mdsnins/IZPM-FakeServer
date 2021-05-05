from sys import argv
from app import *

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 10000, debug = True)