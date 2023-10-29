import json
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

PORT = 3200
HOST = 'localhost'

with open('{}/databases/movies.json'.format("."), "r") as jsf:
    movies = json.load(jsf)["movies"]


# root message
@app.route("/", methods=['GET'])
def home():
    """
        Returns the home page of the movie service
    """
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>", 200)


@app.route("/json", methods=['GET'])
def get_json():
    """
        Returns the json database of the movie service
    """
    res = make_response(jsonify(movies), 200)
    return res


@app.route("/movies/<movieid>", methods=['GET'])
def get_movie_byid(movieid):
    """
        Get a movie information from the movie database knowing the movieid
        param : a string movie id
    """
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            res = make_response(jsonify(movie), 200)
            return res
    return make_response(jsonify({"error": "Movie ID not found"}), 400)


def update_db(movies_db):
    """
        Returns the movies database updated
        param : the database to update
        return : the database on a json format
    """
    with open('{}/databases/movies.json'.format("."), "w") as wfile:
        formatted_movies = {
            "movies": movies_db
        }
        json.dump(formatted_movies, wfile)
    return movies_db


@app.route("/movies/<movieid>", methods=['POST'])
def create_movie(movieid):
    """
        Returns the movie to add to the movie database
        param : a string movie id
        return : the movie added to the database
    """
    req = request.get_json()

    for movie in movies:
        if str(movie["id"]) == str(movieid):
            return make_response(jsonify({"error": "movie ID already exists"}), 409)

    movies.append(req)
    update_db(movies)
    res = make_response(jsonify({"message": "movie added"}), 200)
    return res


@app.route("/titles/<title>", methods=['GET'])
def get_movie_by_title(title):
    """
        Returns the movie requested, knowing its title
        param : a string title
        return : the movie requested information on a json format
    """
    for movie in movies:
        if str(movie["title"]) == str(title):
            res = make_response(jsonify(movie), 200)
            return res
    return make_response(jsonify({"error": "Movie title not found"}), 400)


@app.route("/movies/<movieid>/<rate>", methods=['PUT'])
def update_movie_rating(movieid, rate):
    """
        Returns the movie updated, knowing its movieid
        param : a string movieid and the new rating to update in the movie information
        return : the movie updated information on a json format
    """
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movie["rating"] = rate
            res = make_response(jsonify(movie), 200)
            update_db(movies)
            return res
    res = make_response(jsonify({"error": "movie ID not found"}), 201)
    return res


@app.route("/movies/<movieid>", methods=['DELETE'])
def del_movie(movieid):
    """
        Delete a movie from the bookings database knowing the movieid
        param : a string movieid
        return : the movie deleted information
    """
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movies.remove(movie)
            update_db(movies)
            return make_response(jsonify(movie), 200)
    res = make_response(jsonify({"error": "movie ID not found"}), 400)
    return res


if __name__ == "__main__":
    # p = sys.argv[1]
    print("Server running in port %s" % PORT)
    app.run(host=HOST, port=PORT)
