from flask import Flask, Response, request, jsonify, redirect, url_for, render_template,session, abort
import os
import pymongo
import json


client = pymongo.MongoClient('db', 27017)
db = client['db1']
students = db['students']
teams = db['teams']

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

@app.route('/api/team/add')
def add_team():
    #students.update({'gravitasID':12361}, {'$set':{'team':1}}, upsert=False)
    team_members=request.args.get('reg_nos').split(',')
    if(len(team_members)<2):
        return jsonify({'status':'error', 'error':'less than two team members given'})

    if(len(team_members)>3):
        return jsonify({'status':'error', 'error':'more than three team members given'})

    for member_reg in team_members:
        app.logger.info(member_reg)
        team_member = students.find_one({'registrationNo':member_reg})
        app.logger.info(team_member)
        if(team_member['registrationStatus']!=1):
            return jsonify({'status':'error', 'error':'Member {} Not Registered'.format(member_reg)})
        if(team_member['teamID']!=0):
            return jsonify({'status':'error', 'error':'Member {} already in a team'.format(member_reg)})
    
    team_id = get_max_team_id()+1
    for member_reg in team_members:
        students.update({'registrationNo':member_reg}, {'$set':{'teamID':team_id}}, upsert=False)

    inserted_id = teams.insert_one({"teamID":team_id,'team_members':team_members, 'tasks':[], 'points':0}).inserted_id
    
    return jsonify(list(teams.find({"_id":inserted_id},{"_id":False}))[0])


@app.route('/api/team/<teamid>')
def get_team(teamid):
    return jsonify(list(teams.find({"teamID":int(teamid)},{"_id":False})))
@app.route('/api/points/<teamid>')
def get_points(teamid):
    team =teams.find_one({"teamID":int(teamid)},{"_id":False})
    if team is None:
        return jsonify({'status':'error', 'error':'Team {} Does not exist'.format(teamid)})
    else:
        output = {'teamID':int(teamid), 'points': team['points']}
    return jsonify(output)





def get_max_team_id():
    maxval = teams.find_one({"teamID": {"$ne":0}},sort=[("teamID",-1)])
    if maxval is None:
        return 0
    else:
        return int(maxval["teamID"])

if __name__ == "__main__":
    Flask.run(app, host='0.0.0.0', port=80, debug=True)
