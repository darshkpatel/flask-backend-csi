# Flask API Backend - Docker
This is a simple flask backend for the requirements given above. It uses MongoDB and Flask, also docker-compose has been configure to spin up docker containers for MongoDB and Flask.

# Installation and running
``` sudo docker-compose build```

```sudo docker-compose up```

# Endpoint Documentation:

 ## ```/ping```
Sanity check route to check if the backend is up

##  ```/api/students/all```
Returns all student data stored in the database in JSON format

## ```/api/students/registered```
Returns all registered students in the database in JSON format

## ```/api/students/unregistered```
Returns all unregistered students in the database in JSON format

## ```/api/team/add```
* Example: ```/api/team/add?reg_nos="18bci0000,18bci0001"```
* Requires GET attribute ```reg_nos``` which contains a string of comma seperated Registration Numbers.

Returns JSON data of the new team which was formed. 

Returns ```{'status':'error', 'error': 'ERROR INFO' }``` in case of error.


 ## ```/api/team/<teamid>```
 * Example: ```/api/team/1```
 
 Returns Team data stored in the database. 

 Returns ```{'status':'error', 'error': 'ERROR INFO' }``` in case of error.

 ## ```/api/team/<teamid>/assign_tasks```
 * Example: ```/api/team/1/assign_tasks?tasks=1,2,3,4```
* Requires GET attribute ```tasks``` which contains a string of comma seperated taskID's .

Returns JSON data of the team. 

Returns ```{'status':'error', 'error': 'ERROR INFO' }``` in case of error.
 ## ```/api/team/<teamid>/complete_tasks```
 * Example: ```/api/team/1/complete_tasks?tasks=1,2,3,4```
* Requires GET attribute ```tasks``` which contains a string of comma seperated taskID's .

Returns JSON data of the team with updated points. 

Returns ```{'status':'error', 'error': 'ERROR INFO' }``` in case of error.
 
 ## ```/api/points/<teamid>```
 * Example: ```/api/points/1```
 
 Returns Team points stored in the database. 

 Returns ```{'status':'error', 'error': 'ERROR INFO' }``` in case of error.
 ## ```/api/tasks/<taskid>```
 * Example: ```/api/tasks/1```
 
 Returns task details in JSON format stored in the database. 

 Returns ```{'status':'error', 'error': 'ERROR INFO' }``` in case of error.
 ## ```/api/tasks/all```

 Returns all task details in JSON format stored in the database. 
