#!/usr/bin/env python3

import requests
from requests.auth import HTTPBasicAuth 


from general_functions import SayHi


def HandleInputParameters():

    import os
    import argparse
    # read this, and look at mutually exclusive arrgs  https://linuxconfig.org/how-to-use-argparse-to-parse-python-scripts-parameters
    
    this_script_path=(os.path.dirname(sys.argv[0]))
    
    # this_script_name=(os.path.basename(sys.argv[0]))
    datadir=os.path.join(this_script_path,"data") # Ah!  you don't want the '/' in your args - makes sense!  
    default_logfile=os.path.join(datadir,"default_log_file.txt")
    default_password='default1'
        
    # Set up input options
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--hostName", type=str, dest="hostName", help="The hostName of the DataStage engine. e.g HN01 ", default='HN01', required=True) # Setting all to false here as it's making testing easier
    parser.add_argument("--project-name", type=str, dest="project_list", help="project to compile jobs in ", required=True)
    parser.add_argument("--logfile", type=str, dest="logfile", help="the logfile to be processed", default=default_logfile)
    parser.add_argument("--jobName", action='append', type=str, dest="job_list", help="jobs to compile", required=True)
    parser.add_argument("--password", type=str, dest="password", help="password", default=default_password, action=PasswordPromptAction, nargs='?')
    

    
    
    return parser






def main(arrgv=None):
    ##  Main line

    ## This script has been coded with 3.7.
    import sys
    if sys.version_info < (3,7):
        sys.exit("\nThis script requires python 3.7 or higher.\n")
    
     

    parser=HandleInputParameters()
    args = parser.parse_args()

    global logMessage # Make it available to all 
    from general_functions import LogMessage
    logMessage=LogMessage(args.logfile)

    logMessage.info("Starting the compile script.")

    print(SayHi())


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
    
    
   
    
if __name__=="__main__":
    import sys
    main()



print('The End!')



