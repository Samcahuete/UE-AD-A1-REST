import json
import requests
from flask import Flask, request, jsonify, make_response
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = 'localhost'

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
    bookings = json.load(jsf)["bookings"]


def update_db(bookings_db):
    """
        Returns the bookings database updated
        param : the database to update
        return : the database on a json format
    """
    with open('{}/databases/bookings.json'.format("."), "w") as wfile:
        formatted_bookings = {
            "bookings": bookings_db
        }
        json.dump(formatted_bookings, wfile)
    return bookings_db


@app.route("/", methods=['GET'])
def home():
    """
        Returns the home page of the booking service
    """
    return make_response("<h1 style='color:blue'>Welcome to the Booking service!</h1>", 200)


@app.route("/bookings", methods=['GET'])
def get_json():
    """
        Returns the json database of the booking service
    """
    res = make_response(jsonify(bookings), 200)
    return res


@app.route("/bookings/<userid>", methods=['GET'])
def get_bookings_by_userid(userid):
    """
        Returns the bookings of a user, knowing his userid
        param : a string userid
        return : the bookings on a json format
    """
    for users_info in bookings:
        if str(users_info["userid"]) == str(userid):
            res = make_response(jsonify(users_info), 200)
            return res
    return make_response(jsonify({"error": "bad input parameter"}), 400)


@app.route("/bookings/<userid>", methods=['POST'])
def add_booking(userid):
    """
        Returns the requested booking after adding it to the bookings database knowing the userid
        param : a string userid
        return : the booking added on a json format (with two keys movieid and date)
    """
    req = request.get_json()
    validity = requests.get('http://localhost:3201/bookings/verification', json=req).json()
    user_existence_response = requests.get(f'http://localhost:3203//users/{userid}')
    if not validity["validity"]:
        return make_response(jsonify({"error": "schedule doesn't exist"}), 400)
    if user_existence_response.status_code !=200:
        return make_response(jsonify({"error": "user not found"}), 400)
    user_found = False
    for user_bookings in bookings:
        if str(user_bookings["userid"]) == str(userid):
            user_found = True
            print("User found")
            for schedule in user_bookings["dates"]:
                if schedule["date"] == req["date"]:
                    print("date found")
                    for movie in schedule["movies"]:
                        if movie == req["movieid"]:
                            return make_response(jsonify({"error": "booking already registered"}), 400)
                    schedule["movies"].append(req["movieid"])
                    res = make_response(jsonify({"message": "booking added"}), 200)
                    update_db(bookings)
                    return res
            new_date = {
                "date": req["date"],
                "movies": [req["movieid"]]
            }
            user_bookings["dates"].append(new_date)
            res = make_response(jsonify({"message": "booking added"}), 200)
    if not user_found:
        print("User not found")
        new_date = {
            "date": req["date"],
            "movies": [req["movieid"]]
        }
        new_user_bookings = {
            "dates": [new_date],
            "userid": userid
        }
        bookings.append(new_user_bookings)
        res = make_response(jsonify({"message": "new user and booking added"}), 200)
    update_db(bookings)
    return res


@app.route("/bookings/<userid>", methods=['DELETE'])
def delete_booking(userid):
    """
        Delete a booking from the bookings database knowing the userid, the movieid and the date
        param : a string userid
    """
    req = request.get_json()
    user_found = False
    movie_found = False
    for user_bookings in bookings:
        if str(user_bookings["userid"]) == str(userid):
            user_found = True
            print("user_found = true")
            for schedule in user_bookings["dates"]:
                print(schedule)
                if schedule["date"] == req["date"]:
                    print("date trouvée")
                    for movie in schedule["movies"]:
                        if movie == req["movieid"]:
                            movie_found = True
                if movie_found:
                    schedule["movies"].remove(req["movieid"])
                    update_db(bookings)
                    if len(schedule["movies"]) == 0:
                        user_bookings["dates"].remove(schedule)
                        update_db(bookings)
                    if len(user_bookings["dates"]) == 0:
                        bookings.remove(user_bookings)
                        update_db(bookings)
                    return make_response(jsonify({"message": "booking deleted"}), 200)
    if not user_found:
        print("user not found")
        return make_response(jsonify({"error": "user non existent"}), 400)
    if not movie_found:
        return make_response(jsonify({"error": "booking non existent"}), 400)


@app.route("/bookings/delete_multiple/<userid>", methods=['DELETE'])
def delete_all_bookings(userid):
    """
        Delete all the bookings of the given user (id) from the bookings database
        param : a string userid
    """
    for user_bookings in bookings:
        if str(user_bookings["userid"]) == str(userid):
            bookings.remove(user_bookings)
            update_db(bookings)
            return make_response(jsonify({"message": "all bookings deleted"}), 200)
    return make_response(jsonify({"error": "Aucun booking associé à ce user"}), 400)

@app.route("/bookings/verification", methods=['GET'])
def check_booking_validity():
    """
        Check a booking validity from the showtime database knowing the movieid and the date
    """
    new_movie = request.get_json()
    check_date_existence = requests.get(f'http://localhost:3202/showmovies/{new_movie["date"]}')
    if check_date_existence.status_code == 200:
        movies_available = check_date_existence.json()["movies"]
        if new_movie["movieid"] in movies_available:
            return make_response(jsonify({"validity": True}), 200)
    if check_date_existence.status_code == 400:
        return make_response(jsonify({"validity": False}), 200)
    return make_response(jsonify({"error": "Une erreur s'est produite lors de l'appel au service showtimes."
                                           f"code d'erreur: {check_date_existence.status_code}"}), 400)

if __name__ == "__main__":
    print("Server running in port %s" % PORT)
    app.run(host=HOST, port=PORT)
