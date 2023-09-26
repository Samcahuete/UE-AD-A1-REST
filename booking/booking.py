from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
   bookings = json.load(jsf)["bookings"]

@app.route("/", methods=['GET'])
def home():
   return make_response("<h1>Test</h1>", 200)

@app.route("/bookings", methods=['GET'])
def get_json():
   res = make_response(jsonify(bookings), 200)
   return res

@app.route("/bookings/<userid>", methods=['GET'])
def get_bookings_by_userid(userid):
    for users_info in bookings:
        if str(users_info["userid"]) == str(userid):
            res = make_response(jsonify(users_info),200)
            return res
    return make_response(jsonify({"error":"bad input parameter"}),400)

@app.route("/bookings/<userid>", methods=['POST'])
def add_booking(userid):
    req = request.get_json()
    if not check_booking_validity(req):
        return make_response(jsonify({"error":"schedule doesn't exist"}),400)
    user_found = False

    for user_bookings in bookings:
        if str(user_bookings["userid"]) == str(userid):
            user_found = True
            print("user_found = true")
            for schedule in user_bookings["dates"]:
                if schedule["date"] == req["date"]:
                    print("date trouvée")
                    for movie in schedule["movies"]:
                        if movie == req["movieid"]:
                            return make_response(jsonify({"error": "booking already registered"}), 400)
                    print("avant schedule[movies]", schedule["movies"])
                    schedule["movies"].append([req["movieid"]])
                    print("après schedule[movies]", schedule["movies"])

                    res = make_response(jsonify({"message": "booking added"}), 200)
                    return res
            new_date = {
                "date":req["date"],
                "movies": [req["movieid"]]
            }
            user_bookings["dates"].append(new_date)
            res = make_response(jsonify({"message":"booking added"}),200)
    if not user_found:
        print("user_found = false")
        new_date = {
            "date": req["date"],
            "movies": [req["movieid"]]
        }
        new_user_bookings ={
            "dates" : [new_date],
            "userid": userid
        }
        bookings.append(new_user_bookings)
        res = make_response(jsonify({"message": "new user and booking added"}), 200)
    return res


def check_booking_validity(booking):
    schedule = requests.get('http://172.16.132.100:3202/showtimes').json()
    print(schedule)
    for single_schedule in schedule:
        if single_schedule["date"] == booking["date"]:
            for movie in single_schedule["movies"]:
                if movie == booking["movieid"]:
                    return True
    return False

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
