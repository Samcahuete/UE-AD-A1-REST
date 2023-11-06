import json
import requests
from flask import Flask, request, jsonify, make_response
from werkzeug.exceptions import NotFound


app = Flask(__name__)
PORT = 3203
HOST = 'localhost'

with open('{}/databases/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]


def update_db(users_db):
    """
        Returns the users database updated
        param : the database to update
        return : the database on a json format
    """
    with open('{}/databases/users.json'.format("."), "w") as wfile:
        formatted_users = {
            "users": users_db
        }
        json.dump(formatted_users, wfile)
    return users_db


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
        if user["id"] == userid:
            res = make_response(jsonify(user), 200)
            return res
    return make_response(jsonify({"error": "bad input parameter"}), 400)


@app.route("/users/<userid>", methods=['POST'])
def add_user(userid):
    """
        Add a user to the database if it doesn't already exist
        param : a string userid
    """
    user_req = request.get_json()
    if user_req["id"] != userid:
        res = make_response(jsonify({"error": f"the userid specified in the url ({userid}) "
                                              f"doesn't match with the one given in the body ({user_req['id']})"}), 400)
        return res
    for user in users:
        if user["id"] == userid:
            res = make_response(jsonify({"error": f"user {userid} already exists"}), 400)
            return res
    users.append(user_req)
    update_db(users)
    return make_response(jsonify({"message": f"user {userid} added"}), 200)


@app.route("/users/<userid>", methods=['DELETE'])
def delete_user(userid):
    """
        Delete a user given its id and all its bookings
        param : a string userid
    """
    for user in users:
        if user["id"] == userid:
            requests.delete(f"http://localhost:3201/bookings/delete_multiple/{userid}")
            users.remove(user)
            update_db(users)
            res = make_response(jsonify({"message": f"user {userid} deleted"}), 200)
            return res
    return make_response(jsonify({"error": f"non existent user {userid} "}), 400)


@app.route("/users/bookings/<userid>", methods=['GET'])
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
    user_bookings_request = requests.get('http://localhost:3203/users/bookings/' + userid)
    user_bookings = user_bookings_request.json()
    if user_bookings_request.status_code == 200:
        moviesInfo = {
            "movies": []
        }
        for booking in user_bookings:
            for movieid in booking["movies"]:
                movie_request = requests.get('http://localhost:3200/movies/' + movieid)
                if movie_request.status_code == 200:
                    movie = movie_request.json()
                    moviesInfo["movies"].append(movie)
        return make_response(jsonify(moviesInfo), 200)
    return make_response(jsonify({"error": "no booking found for user" + userid}), 400)


if __name__ == "__main__":
    print("Server running in port %s" % PORT)
    app.run(host=HOST, port=PORT)
