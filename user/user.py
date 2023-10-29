import json

import requests
from flask import Flask, jsonify, make_response

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/databases/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]


@app.route("/", methods=['GET'])
def home():
    """
        Returns the home page of the user service
    """
    return make_response("<h1 style='color:blue'>Welcome to the User service!</h1>", 200)


@app.route("/users", methods=['GET'])
def get_json():
    """
        Returns the json database of the user service
    """
    res = make_response(jsonify(users), 200)
    return res


@app.route("/users/<userid>", methods=['GET'])
def get_user_by_id(userid):
    """
        Get a user information from the user database knowing the userid
        param : a string userid
    """
    for user in users:
        if str(user["id"]) == str(userid):
            res = make_response(jsonify(user), 200)
            return res
    return make_response(jsonify({"error": "bad input parameter"}), 400)


@app.route("/users/bookings/<userid>", methods=['GET', 'POST'])
def get_bookings_by_userid(userid):
    """
        Returns the bookings of a user from the bookings database knowing the userid
        param : a string userid
        return : the bookings requested on a json format
    """
    bookings = requests.get('http://localhost:3201/bookings/' + userid).json()
    res = make_response(jsonify(bookings["dates"]), 200)
    return res


@app.route("/users/movies/<userid>", methods=['GET'])
def get_movies_by_userid(userid):
    """
        Returns the movies of a user from the bookings and movies database knowing the userid
        param : a string userid
        return : the movies information requested on a json format
    """
    print("userid", userid)
    user_bookings_request = requests.get('http://localhost:3203/users/bookings/' + userid)
    user_bookings = user_bookings_request.json()
    print("user_bookings", user_bookings)
    if user_bookings_request.status_code == 200:
        moviesInfo = {
            "movies": []
        }
        for booking in user_bookings:
            for movieid in booking["movies"]:
                print("movieid", movieid)
                print('http://localhost:3200/movies/' + movieid)
                movie_request = requests.get('http://localhost:3200/movies/' + movieid)
                movie = movie_request.json()
                if movie_request.status_code == 200:
                    print("movie", movie)
                    moviesInfo["movies"].append(movie)
        return make_response(jsonify(moviesInfo), 200)
    return make_response(jsonify({"error": "no booking found for user" + userid}), 400)


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
