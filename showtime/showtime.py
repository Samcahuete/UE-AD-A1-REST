from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202
HOST = 'localhost'

with open('{}/databases/times.json'.format("."), "r") as jsf:
    schedule = json.load(jsf)["schedule"]


@app.route("/", methods=['GET'])
def home():
    return make_response("<h1>Test</h1>", 200)


@app.route("/showtimes", methods=['GET'])
def get_json():
    res = make_response(jsonify(schedule), 200)
    return res


@app.route("/showmovies/<date>", methods=['GET'])
def get_schedule_by_date(date):
    for single_schedule in schedule:
        if str(single_schedule["date"]) == str(date):
            res = make_response(jsonify(single_schedule), 200)
            return res
    return make_response(jsonify({"error": "bad input parameter"}), 400)


if __name__ == "__main__":
    print("Server running in port %s" % PORT)
    app.run(host=HOST, port=PORT)
