#!/usr/bin/env python3

"""
This script should take a template dsenv file, and apply changes to it based on entries in a json config file
"""

print('Hello world!')



def HandleInputParameters():

    import os
    import argparse
    import sys
    # read this, and look at mutually exclusive arrgs  https://linuxconfig.org/how-to-use-argparse-to-parse-python-scripts-parameters
    
    this_script_path=(os.path.dirname(sys.argv[0]))
    
    # this_script_name=(os.path.basename(sys.argv[0]))
    #datadir=os.path.join(this_script_path,"data") # Not required
    
    
    #default_logfile=os.path.join(datadir,"default_log_file.txt")
    from general_functions import MakeALogFileName
    default_logfile=MakeALogFileName()
    

    #default_DSParams_template=os.path.abspath(os.path.join(this_script_path, 'TestFiles','DSParams.template'))
    # Set up input options
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--install-base", type=str, dest="install_base", help="The base of the DS install. e.g /iis/test .", default='/iis/test', required=True) # Setting all to false here as it's making testing easier
    parser.add_argument("--temp-base", type=str, dest="temp_base", help="The base of the temp/scratch location.  e.g /scratch", default='/scratch')
    parser.add_argument("--logfile", type=str, dest="logfile", help="the logfile to be processed", default=default_logfile)
    
    
    
    
    
    return parser









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

   
    #import MyLogging.mylogging

    from MyLogging.mylogging  import getLogFile, setLogFile, LogMessage
    global logMessage
    logMessage=LogMessage()

    #test = getLogFile()
    #if getLogFile() is None:
    setLogFile(args.logfile)

    
    #Check input params
    errorfound=False
    #if not os.path.exists(args.template_dsparam):
    #    errorfound=True
    #    logMessage.info('Template dsenv file not found at: ' + args.template_dsparam)
    
    if not os.path.exists(args.install_base):
        
        logMessage.warning('Install base does not existat: ' + args.install_base)
    
    if not os.path.exists(args.temp_base):
        
        logMessage.warning('Temp base does not existat: ' + args.temp_base)

    if errorfound:
        sys.exit("\nInput parameter failed validation. See previous messages.\n")


    
    


    logMessage.info('logfile is :' + args.logfile)
    logMessage.info('install_base is :' + args.install_base )
    logMessage.info('temp_base is :' + args.temp_base )
           


    # Check you will have permissions to change the files as required

    import pwd
    import grp 
    
    version_xml=os.path.join(args.install_base,'InformationServer', 'Version.xml')
    dshome=os.path.join(args.install_base,'InformationServer','Server', 'DSEngine')

    from datastage_functions import GetDSAdminName,GetDSAdminGroup
    try: 
        adminName=GetDSAdminName(version_xml)
        # not used anywhere yet adminGroup=GetDSAdminGroup()
        
        uid=pwd.getpwnam(adminName).pw_uid  
        # not used anywhere yet. gid=grp.getgrnam(adminGroup).gr_gid
    except KeyError:
        logMessage.error('Unable to find uid or gid for ' + adminName )
        sys.exit("\nUser not found.\n")



    if not os.geteuid() == 0 and not os.getuid() == uid:
        sys.exit("\nOnly root or the datastage admin can run this script\n")


    #standard_params=GetProjectParamConfig(args.standard_params_file,'EnvVarDefns')
    #standard_project_settings=GetProjectParamConfig(args.standard_params_file,'PROJECT')
    #standard_autopurge_settings=GetProjectParamConfig(args.standard_params_file,'AUTO-PURGE')


    # Get the project specific parameters from the config file
    #project_specific_params=GetProjectParamConfig(args.project_specific_params_file,'EnvVarDefns')
    #project_specific_project_settings=GetProjectParamConfig(args.project_specific_params_file,'PROJECT')
    #project_specific_autopurge_settings=GetProjectParamConfig(args.project_specific_params_file,'AUTO-PURGE')

    ## Create the new temp dsenv file
    ## This creates a temp file that will be removed once it is closed.
    ## Then use normal open to open the same file so that we can write to it as normal
    import tempfile
    fp = tempfile.NamedTemporaryFile()

    try:
        f_temp = open(fp.name,'w')
    except OSError:
        logMessage.error('Unable to open the temp file :' + f_temp )
        return None


    ## Run a command to create a new dsenv file
    ## Annoying
    import subprocess
    cmd_setupenv='source ' + os.path.join(dshome,'dsenv')
    cmd_create_new_dsenv=os.path.join(dshome,'bin', 'loadfile') + ' ' + os.path.join(dshome,'dsenv.single.u') + ' ' + os.path.join(os.sep,'tmp') + ' -noconvert'  
    command_to_run=cmd_setupenv +';' + cmd_create_new_dsenv
    import sys
    if sys.version_info >= (3,7):
        result = subprocess.run([command_to_run] , capture_output=True, shell=True, encoding="UTF-8")
    else: 
        result = subprocess.run([command_to_run] , shell=True, encoding="UTF-8", stdout=subprocess.PIPE)
    print(result)





    
        

        
    

if __name__=="__main__":
    main()
