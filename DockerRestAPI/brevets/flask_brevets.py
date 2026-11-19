"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
from pymongo import MongoClient
from pymongo.errors import PyMongoError


import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = getattr(CONFIG, "SECRET_KEY", "dev-only-key")

client = MongoClient('db', 27017, serverSelectionTimeoutMS=3000)
db = client.brevetsdb

VALID_DISTANCES = [200, 300, 400, 600, 1000]

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', type=float)
    brevet_dist = request.args.get('brevet_dist', 200, type=int)
    begin_time = request.args.get('begin_time', type=str)
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))
    if km is None or km < 0 or not begin_time:
        return flask.jsonify(result={"open": "", "close": ""})
    
    open_time = acp_times.open_time(km, brevet_dist, begin_time)
    close_time = acp_times.close_time(km, brevet_dist, begin_time)
    return flask.jsonify(result={"open": open_time, "close": close_time})

@app.route("/_submit_times", methods=["POST"])
def _submit_times():
    data = request.get_json(silent=True)
    if not data:
        return flask.jsonify(error="No data was received."), 400

    items = data.get("items", [])
    if not items:
        return flask.jsonify(
            error="Please enter at least one control time before submitting."), 400

    try:
        brevet_dist = int(data.get("brevet_dist"))
    except (TypeError, ValueError):
        return flask.jsonify(error="Brevet distance is missing or invalid."), 400
    if brevet_dist not in VALID_DISTANCES:
        return flask.jsonify(
            error="Brevet distance must be one of 200, 300, 400, 600, or 1000."), 400

    cleaned = []
    for item in items:
        try:
            km = float(item.get("km"))
        except (TypeError, ValueError):
            return flask.jsonify(error="Control distances must be numbers."), 400
        if km < 0 or km > brevet_dist * 1.2:
            return flask.jsonify(
                error="{} km is outside the allowed range for a {} km brevet.".format(
                    km, brevet_dist)), 400
        if not item.get("open") or not item.get("close"):
            return flask.jsonify(
                error="The {} km control is missing its times.".format(km)), 400
        cleaned.append({
            "brevet_dist": brevet_dist,
            "begin_time": data.get("begin_time"),
            "km": km,
            "open": item["open"],
            "close": item["close"],
        })

    try:
        db.controls.delete_many({})  # keep only the latest submission
        db.controls.insert_many(cleaned)
    except PyMongoError:
        return flask.jsonify(
            error="Could not reach the database. Please try again."), 500

    return flask.jsonify(message="Saved {} control times.".format(len(cleaned)))


@app.route("/display")
def display():
    try:
        items = list(db.controls.find({}, {"_id": 0}).sort("km", 1))
    except PyMongoError:
        return flask.render_template("display.html", items=[],
                                     error="Could not reach the database."), 500
    return flask.render_template("display.html", items=items, error=None)


#############

app.debug = getattr(CONFIG, "DEBUG", False)
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    port = getattr(CONFIG, "PORT", 5000)
    print("Opening for global access on port {}".format(port))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
