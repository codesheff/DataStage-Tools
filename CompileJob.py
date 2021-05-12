#!/usr/bin/env python3





def HandleInputParameters():

    import os
    import argparse

    ## Variables for this script
    this_script_path=(os.path.dirname(sys.argv[0]))
    
    this_script_name=(os.path.basename(sys.argv[0]))
    # not used datadir=os.path.join(this_script_path,"data") # Ah!  you don't want the '/' in your args - makes sense!  
    logdir=os.path.join(this_script_path,"logs") # Ah!  you don't want the '/' in your args - makes sense!  
    default_logfile=os.path.join(logdir,this_script_name + '_log_file.txt')
   
        
    # Set up input options
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--serviceTierHostName", type=str, dest="serviceTierHostName", help="The hostName/dns/ipaddress of the DataStage Service layer. e.g 127.0.0.1:9443 ", default='127.0.0.1', required=False) # Setting all to false here as it's making testing easier
    parser.add_argument("--isPort", type=str, dest="isPort", help="The port for accesing the serviceTier e.g 9443 ", default='9443', required=False) # Setting all to false here as it's making testing easier
    parser.add_argument("--hostName", type=str, dest="hostName", help="The hostName of the DataStage engine. e.g HN01. Often the same as the serviceTierHostName ", default='HN01', required=True) # Setting all to false here as it's making testing easier
    parser.add_argument("--projectName", type=str, dest="projectName", help="project to compile jobs in ", required=True)
    parser.add_argument("--logfile", type=str, dest="logfile", help="the logfile to be processed", default=default_logfile)
    parser.add_argument("--jobName", action='append', type=str, dest="job_list", help="jobs to compile", required=True)
    


    # Add logon credentials 
    #       get credentials, using generic code.
    from general_functions import GetCredentials
    Credentials = GetCredentials(user_argname='--ds-user', password_argname='--ds-password')
    parser = Credentials.add_login_args(parser)

    args = parser.parse_args()
    args.funct_getlogon(args)
    
   
    
    return args






def main():
    ##  Main line

    ## This script has been coded with 3.7.
    import sys
    if sys.version_info < (3,7):
        sys.exit("\nThis script requires python 3.7 or higher.\n")
    
     

    args = HandleInputParameters()
    #args = parser.parse_args()

    from MyLogging.mylogging  import getLogFile, setLogFile, LogMessage
    global logMessage
    logMessage=LogMessage()

    setLogFile(args.logfile)
    logMessage.info("Starting the compile script.")

    


    #url='https://127.0.0.1:9443/ibm/iis/api/dscdesignerapi?api=compileDSJob&jobName=Job_2&projectName=dstage1&hostName=HN01&getFullOutput=false&apiVersion=3.0'
    #url='https://127.0.0.1:9443/ibm/iis/api/dscdesignerapi'
    url='https://' + args.serviceTierHostName + ':' + args.isPort + '/ibm/iis/api/dscdesignerapi'
    p = {"api": "compileDSJob", "jobName": "Job_1", "projectName" : args.projectName , "hostName" : args.hostName , "getFullOutput" : "False", "apiVersion" : "3.0"}

    user=args.user
    password=args.password

    


    #def compileJob(url='https://127.0.0.1:9443/ibm/iis/api/dscdesignerapi', parameters={"api": "compileDSJob", "jobName": "Job_1", "projectName" : "dstage1" , "hostName" : 'HN01', "getFullOutput" : "False", "apiVersion" : "3.0"} )
    # Do as multiple requests in one session, so only needs to authenticate once.

    
    import requests
    from requests.auth import HTTPBasicAuth 

    #response = requests.get('https://127.0.0.1:9443/ibm/iis/api/dscdesignerapi', params={"api": "compileDSJob", "jobName": "Job_1", "projectName" : args.projectName , "hostName" : args.hostName , "getFullOutput" : "False", "apiVersion" : "3.0"}, auth = HTTPBasicAuth(user,password),verify=False ) 

 
    
    #jobs=['Job_1','Job_2','Job_3']
    jobs=args.job_list
    with requests.Session() as s:

        ssl_warned_already=False
        import warnings
        import urllib3
        #urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        #warnings.filterwarnings('error',"InsecureRequestWarning")
        warnings.filterwarnings('error')  # Not sure how to specify just the warning we're interested in.

        for job in jobs:
            p["jobName"] = job
                


            try:
                response = s.get(url, params=p, auth = HTTPBasicAuth(user,password),verify=False )  #Need to look into sorting out the ssl here.
      
            except urllib3.exceptions.InsecureRequestWarning as e:
                
                # Log a message, then Switch warnings off for this warning, and get the response. This might mean we're actually doing the compile 2x here but anyway, that's fine for now.
                # Need to switch warnings back on after
                if ssl_warned_already == False:
                    logMessage.warning(str(e))
                    ssl_warned_already=True
                
                warnings.filterwarnings('default')
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                response = s.get(url, params=p, auth = HTTPBasicAuth(user,password),verify=False )  #Need to look into sorting out the ssl here.
            
            except Exception as e:
                logMessage.error('Exception occured. Exception is :' + str(e) + '. Check if url ( hostname and port) is correct.')
                
                break 
                

            if response.status_code == 401:
                logMessage.error('Unauthorized for url : ' + url + '. Check you have entered username and password correctly.')
                break

            if response.json()['succeeded'] == True:
                logMessage.info(job + ' compiled ok.')
            else:
                logMessage.warning(job + ' compiled FAILED.' + str(response.json()['failureMessage']) + ' ( If "Null RID" then the combination of hostName,project and jobname does not exist.) ')
            
    warnings.filterwarnings('default')
                

            
    
    
   
    
if __name__=="__main__":
    import sys
    main()



print('The End!')



