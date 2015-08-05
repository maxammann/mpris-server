from flask import Flask, jsonify, request, url_for
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import pympris
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

mpris = None
bus = None
app = Flask(__name__)


def try_connect():
    global mpris
    players_ids = list(pympris.available_players())

    if not players_ids:
        raise pympris.PyMPRISException("No players found")

    print("Available players : " + str(players_ids))

    mpris = pympris.MediaPlayer(players_ids[0], bus)
    print("Using " + str(mpris.root.Identity))


def get_player():
    if mpris is None:
        try_connect()

    try:
        mpris.root.Identity
    except pympris.PyMPRISException:
        try_connect()

    return mpris.player


@app.errorhandler(pympris.PyMPRISException)
def handle_invalid_usage(error):
    response = jsonify({"message": str(error), "result": "failed"})
    response.status_code = 503
    return response


@app.errorhandler(KeyError)
def handle_invalid_usage(error):
    response = jsonify({"message": "Failed to access mpris key: " + error.message, "result": "failed"})
    response.status_code = 503
    return response


@app.route("/play")
def play():
    get_player().Play()
    return jsonify(result="success")


@app.route("/stop")
def stop():
    get_player().Stop()
    return jsonify(result="success")


@app.route("/pause")
def pause():
    get_player().Pause()
    return jsonify(result="success")


@app.route("/next")
def next():
    get_player().Next()
    return jsonify(result="success")


@app.route("/title")
def title():
    return jsonify(result="success", title=get_player().Metadata['xesam:title'])


@app.route("/seek")
def seek():
    id = get_player().Metadata['mpris:trackid']
    get_player().SetPosition(id, get_player().Position + int(request.args.get('offset')) * int(10e5))
    return jsonify(result="success")


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():

        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint)
            links.append(url)

    return str(links)


def run():
    global mpris
    global bus

    dbus_loop = DBusGMainLoop()
    bus = dbus.SessionBus(mainloop=dbus_loop)

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(28781)
    IOLoop.instance().start()
    # app.run(host="0.0.0.0", port=28781)
