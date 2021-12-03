from flask import Flask
import time

app = Flask(__name__)


@app.route("/motion/<room>/<state>")
def motion_room(room: str, state: str):
    f = open("../data/" + room + "motion" + state, "w")
    f.write(str(time.time()))
    f.close()
    return "<h1>Success! Motion %s for %s <h1>" % (state, room)


@app.route("/mode/<room>/<mode>")
def mode_room(room: str, mode: str):
    f = open("../data/" + room + "mode", "w")
    f.write(mode)
    f.close()
    return "<h1>Success! Mode %s for %s <h1>" % (mode, room)
