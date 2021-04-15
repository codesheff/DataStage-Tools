#!/usr/bin/env python3

"""
This script will export DataStage components.
Aim is to export components individually to a structure which suits the git repo
"""





def HandleInputParameters():

    import os
    import argparse
    import sys
    import datetime
    # read this, and look at mutually exclusive arrgs  https://linuxconfig.org/how-to-use-argparse-to-parse-python-scripts-parameters
    
    this_script_path=(os.path.dirname(sys.argv[0]))
    
    # this_script_name=(os.path.basename(sys.argv[0]))
    #datadir=os.path.join(this_script_path,"data") # Not required
    
    
    #default_logfile=os.path.join(datadir,"default_log_file.txt")
    from general_functions import MakeALogFileName
    default_logfile=MakeALogFileName()
    

   
    input_ts_format='%Y-%m-%d %H:%M:%S'
    parser = argparse.ArgumentParser()
    parser.add_argument("--install-base", type=str, dest="install_base", help="The base of the DS install. e.g /iis/test .", default='/iis/test', required=False) # Setting all to false here as it's making testing easier
    #parser.add_argument("--since-timestamp", type=datetime.date.fromisoformat, dest="modified_since_timestamp", help="the timestamp to be used to find jobs modified since. ( as UTC and in format 1970-01-01 00:00:00 )", default='1970-01-01 00:00:00')
    parser.add_argument('--since-timestamp', dest="modified_since_timestamp", type=lambda s: datetime.datetime.strptime(s, input_ts_format))
    parser.add_argument("--logfile", type=str, dest="logfile", help="the logfile to be written to ", default=default_logfile)
    
    


        
    
    
    return parser



def db2_results_not_used(command):
    from ibm_db import fetch_assoc

    ret = []
    result = fetch_assoc(command)
    while result:
        # This builds a list in memory. Theoretically, if there's a lot of rows,
        # we could run out of memory. In practice, I've never had that happen.
        # If it's ever a problem, you could use
        #     yield result
        # Then this function would become a generator. You lose the ability to access
        # results by index or slice them or whatever, but you retain
        # the ability to iterate on them.
        ret.append(result)
        result = fetch_assoc(command)
    return ret  # Ditch this line if you choose to use a generator.


  





def main(arrgv=None):
    ##  Main line

    ## This script has been coded with 3.7., but I stuck im a workaround for 3.6
    import sys
    if sys.version_info < (3,6):
        sys.exit("\nThis script requires python 3.6 or higher.\n") 



    ## The test ...  If I can't read this and understand what's going on ...then it needs re-writing
    ##   Any function should fit on 1 screen ( ish) ( ideally)
    ##   Each function should be easily described so we know what it does

    import os
   

    # Get input paramaters
    parser=HandleInputParameters()
    global args 
    args = parser.parse_args()
    #args = parser.parse_known_args()

   
    #import MyLogging.mylogging

    from MyLogging.mylogging  import getLogFile, setLogFile, LogMessage
    global logMessage
    logMessage=LogMessage()

    
    setLogFile(args.logfile)

    
    #Check input params
    errorfound=False
    #if not os.path.exists(args.template_dsparam):
    #    errorfound=True
    #    logMessage.info('Template dsenv file not found at: ' + args.template_dsparam)
    
    if not os.path.exists(args.install_base):
        
        logMessage.warning('Install base does not existat: ' + args.install_base)
    
    if errorfound:
        sys.exit("\nInput parameter failed validation. See previous messages.\n")


    
    if args.modified_since_timestamp is None:
        logMessage.info('No value for --since-timestamp . So will export all components')
    
        

    logMessage.info('logfile is :' + args.logfile)
    logMessage.info('install_base is :' + args.install_base )
   
           


    
    if not os.geteuid() == 0 :
        sys.exit("\nOnly root can run this script\n")


    ## Main Code
    #from datastage_functions import GetListOfComponentsRecentlyModified
    import general_functions
    #import datastage_functions 
    from datastage_functions import GetListOfComponentsRecentlyModified
    
    GetListOfComponentsRecentlyModified(modified_since=args.modified_since_timestamp)








    
        

        
    

if __name__=="__main__":
    main()
