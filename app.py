from flask import Flask, Response, request, jsonify, redirect, url_for, render_template,session, abort
import os
import pymongo
import json


client = pymongo.MongoClient('db', 27017)
db = client['db1']
students = db['students']
teams = db['teams']
tasks = db['tasks']

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
    team_members=request.args.get('reg_nos').split(',')
    #Input Validation
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
    team = teams.find_one({"teamID":int(teamid)},{"_id":False})
    if team is None:
        return jsonify({'status':'error', 'error':'Team {} Does not exist'.format(teamid)})
    else:
        return jsonify(team)

@app.route('/api/team/<teamid>/assign_tasks')
def assign_task(teamid):
    task_list = list(map(int,request.args.get('tasks').split(',')))
    team = teams.find_one({"teamID":int(teamid)},{"_id":False})
     
    #Input Validation todo: check if all tasks in type assigned or not
    if team is None:
        return jsonify({'status':'error', 'error':'Team {} Does not exist'.format(teamid)})
    for task in task_list:
        if tasks.find({"taskID":int(task)},{"_id":False}) is None:
            return jsonify({'status':'error', 'error':'taskID {} Does not exist'.format(teamid)})
        else:
            #update tasks
            teams.update_one({"teamID":int(teamid)},{'$addToSet':{'tasks': {'taskID':task, 'status':'incomplete'}}})
    return jsonify(list(teams.find({"teamID":int(teamid)},{"_id":False}))[0])

@app.route('/api/team/<teamid>/complete_tasks')
def complete_task(teamid):
    task_list = list(map(int,request.args.get('tasks').split(',')))
    team = teams.find_one({"teamID":int(teamid)},{"_id":False})
    task_list_team = [task['taskID'] for task in teams.find_one({"teamID":int(teamid)},{"_id":False})['tasks']]
    task_list_team_complete = [task['taskID'] for task in teams.find_one({"teamID":int(teamid), 'tasks.status': 'complete'},{"_id":False})['tasks']]
    task_types_team = list(set([get_task_type(task) for task in task_list_team]))
    
    #Input Validation
    if team is None:
        return jsonify({'status':'error', 'error':'Team {} Does not exist'.format(teamid)})
    for task in task_list:
        
        if tasks.find({"taskID":int(task)},{"_id":False}) is None:
            return jsonify({'status':'error', 'error':'taskID {} Does not exist'.format(task)})
        if task not in task_list_team:
            return jsonify({'status':'error', 'error':'task {} not assigned to team'.format(task)})
        
        #Set tasks to complete
        teams.update_one({'teamID':int(teamid), 'tasks.taskID': task}, {'$set':{'tasks.$.status':'complete'}}, upsert=False)
   
   #Check and award points
    for task_type in task_types_team:
        if set(get_tasks_in_type(task_type)).issubset(set(task_list_team_complete)):
            awarded_points = sum([tasks.find_one({"taskID":int(taskid)},{"_id":False})['points'] for taskid in get_tasks_in_type(task_type)])
            teams.update_one({'teamID':int(teamid)}, {'$inc':{'points':awarded_points}}, upsert=False)



     

    return jsonify(list(teams.find({"teamID":int(teamid)},{"_id":False}))[0])

@app.route('/api/points/<teamid>')
def get_points(teamid):
    team =teams.find_one({"teamID":int(teamid)},{"_id":False})
    if team is None:
        return jsonify({'status':'error', 'error':'Team {} Does not exist'.format(teamid)})
    else:
        output = {'teamID':int(teamid), 'points': team['points']}
    return jsonify(output)

@app.route('/api/tasks/<taskid>')
def get_task_data(taskid):
    if tasks.find({"taskID":int(taskid)},{"_id":False}) is None:
            return jsonify({'status':'error', 'error':'taskID {} Does not exist'.format(taskid)})
    return jsonify(tasks.find_one({"taskID":int(taskid)},{"_id":False}))

@app.route('/api/tasks/all')
def get_task_data_all():
    return jsonify(list(tasks.find()))


#Helper Functions 
def get_tasks_in_type(tasktype):
    return [task['taskID'] for task in list(tasks.find({"type":int(tasktype)},{"_id":False}))]
def get_task_type(taskid):
   return tasks.find_one({"taskID":int(taskid)},{"_id":False})['type']

def get_max_team_id():
    maxval = teams.find_one({"teamID": {"$ne":0}},sort=[("teamID",-1)])
    if maxval is None:
        return 0
    else:
        return int(maxval["teamID"])






if __name__ == "__main__":
    Flask.run(app, host='0.0.0.0', port=80, debug=True)
