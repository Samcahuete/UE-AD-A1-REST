from flask import Flask, render_template, request, jsonify, make_response
import requests
import json

app = Flask(__name__)
PORT = 3203
HOST = '0.0.0.0'

with open('{}/databases/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]


@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the User service!</h1>", 200)

@app.route("/users", methods=['GET'])
def get_json():
    res = make_response(jsonify(users), 200)
    return res

@app.route("/users/<userid>", methods=['GET'])
def get_user_by_id(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            res = make_response(jsonify(user),200)
            return res
    return make_response(jsonify({"error":"bad input parameter"}),400)

@app.route("/users/bookings/<userid>", methods=['GET'])
def get_bookings_by_userid(userid):
    bookings = requests.get('http://localhost:3201/bookings/'+userid).json()
    res = make_response(jsonify(bookings["dates"]),200)
    return res

@app.route("/users/movies/<userid>", methods=['GET'])
def get_movies_by_userid(userid):
    user_bookings_request = requests.get('http://localhost:3203/users/bookings/'+userid)
    user_bookings = user_bookings_request.json()
    if user_bookings_request.status_code == 200:
        moviesInfo = {
            "movies":[]
        }
        for booking in user_bookings:
            for movieid in booking["movies"]:
                movie_request = requests.get('http://localhost:3200/movies/'+movieid)
                movie = movie_request.json()
                if movie_request.status_code ==200:
                    moviesInfo["movies"].append(movie)
        return make_response(jsonify(moviesInfo),200)
    return make_response(jsonify({"error": "no booking found for user" + userid}), 400)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
