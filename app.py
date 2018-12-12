from flask import Flask, Response, request, jsonify, redirect, url_for, render_template,session, abort
import os
import pymongo
import json


client = pymongo.MongoClient('db', 27017)
db = client['db1']
students = db['students']
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://db:27017/db1"
app.config['SECRET_KEY'] = 'secret!'

#Sanity Check
@app.route("/ping")
def ping():
    app.logger.debug("Responded ping with pong")
    return "Pong"


# URL Routes
@app.route('/api/students/all')
def return_all_students():
    output = list(students.find({}, {'_id': False}))
    return jsonify(output)

@app.route('/api/students/registered')
def return_registered_students():
    output = list(students.find({'registrationStatus':1}, {'_id': False}))
    return jsonify(output)

@app.route('/api/students/unregistered')
def return_unregistered_students():
    output = list(students.find({'registrationStatus':0}, {'_id': False}))
    return jsonify(output)



if __name__ == "__main__":
    Flask.run(app, host='0.0.0.0', port=80, debug=True)
