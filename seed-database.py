from pymongo import MongoClient
import json
client = MongoClient('localhost', 27017)
db = client['db1']
students = db['students']
tasks = db['tasks']
with open('seed-students.json') as f:
    data = json.load(f)
    for student in data:
        student['teamID'] = 0
result = students.insert_many(data)

with open('seed-tasks.json') as f:
    data = json.load(f)
result = tasks.insert_many(data)


