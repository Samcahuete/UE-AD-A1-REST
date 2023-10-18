from flask import Flask, render_template, request, jsonify, make_response
import json
import sys
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3200
HOST = 'localhost'

with open('{}/databases/movies.json'.format("."), "r") as jsf:
    movies = json.load(jsf)["movies"]


# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>", 200)


@app.route("/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(movies), 200)
    return res


@app.route("/new_endpoint", methods=['GET'])
def new_endpoint():
    res = make_response("<h1 style='color:red'>Nouveau point d'entrée</h1>", 200)
    return res


@app.route("/movies/<movieid>", methods=['GET'])
def get_movie_byid(movieid):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            res = make_response(jsonify(movie), 200)
            return res
    return make_response(jsonify({"error": "Movie ID not found"}), 400)


@app.route("/movies/<movieid>", methods=['POST'])
def create_movie(movieid):
    req = request.get_json()

    for movie in movies:
        if str(movie["id"]) == str(movieid):
            return make_response(jsonify({"error": "movie ID already exists"}), 409)

    movies.append(req)
    res = make_response(jsonify({"message": "movie added"}), 200)
    return res


@app.route("/titles/<title>", methods=['GET'])
def get_movie_bytitle(title):
    for movie in movies:
        if str(movie["title"]) == str(title):
            res = make_response(jsonify(movie), 200)
            return res
    return make_response(jsonify({"error": "Movie title not found"}), 400)


@app.route("/movies/<movieid>/<rate>", methods=['PUT'])
def update_movie_rating(movieid, rate):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movie["rating"] = rate
            res = make_response(jsonify(movie), 200)
            return res

    res = make_response(jsonify({"error": "movie ID not found"}), 201)
    return res


@app.route("/movies/<movieid>", methods=['DELETE'])
def del_movie(movieid):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movies.remove(movie)
            return make_response(jsonify(movie), 200)

    res = make_response(jsonify({"error": "movie ID not found"}), 400)
    return res


if __name__ == "__main__":
    # p = sys.argv[1]
    print("Server running in port %s" % PORT)
    app.run(host=HOST, port=PORT)
