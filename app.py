from flask import Flask, Response, request, jsonify, redirect, url_for, render_template,session, abort
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

#Sanity Chack
@app.route("/ping")
def ping():
    return "Pong"


# URL Routes
@app.route('/')
def index():
    return ('',401)


if __name__ == "__main__":
    Flask.run(app, host='0.0.0.0', port=80, debug=True)
