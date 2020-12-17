#!/usr/bin/env python3

import requests
from requests.auth import HTTPBasicAuth 


#url='https://127.0.0.1:9443/ibm/iis/api/dscdesignerapi?api=compileDSJob&jobName=Job_2&projectName=dstage1&hostName=HN01&getFullOutput=false&apiVersion=3.0'
url='https://127.0.0.1:9443/ibm/iis/api/dscdesignerapi'
p = {"api": "compileDSJob", "jobName": "Job_1", "projectName" : "dstage1" , "hostName" : 'HN01', "getFullOutput" : "False", "apiVersion" : "3.0"}

user='isadmin'
password='default'


#def compileJob(url='https://127.0.0.1:9443/ibm/iis/api/dscdesignerapi', parameters={"api": "compileDSJob", "jobName": "Job_1", "projectName" : "dstage1" , "hostName" : 'HN01', "getFullOutput" : "False", "apiVersion" : "3.0"} )
# Do as multiple requests in one session, so only needs to authenticate once.

jobs=['Job_1', 'Job_2', 'Job_1']
with requests.Session() as s:

    for job in jobs:
        p["jobName"] = job
        response = s.get(url, params=p, auth = HTTPBasicAuth(user,password),verify=False )

        print(response.json())
    
    
   
    



print('The End!')



