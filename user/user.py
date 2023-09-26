from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

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
   bookings = requests.get('http://172.16.132.100:3201/bookings').json()
   for booking in bookings:
      if str(booking["userid"]) == str(userid):
         res = make_response(jsonify(booking["dates"]),200)
         return res
   return make_response(jsonify({"error":"no booking found"}),400)



if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
