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
    
    components_list=GetListOfComponentsRecentlyModified(modified_since=args.modified_since_timestamp)

    #from datetime import datetime
    import datetime 
    components_list_test={
        ('HN01', 'dstage1'): [
            ('JobDefn', 'ExternalSource', datetime.datetime(2021, 1, 7, 17, 21, 34, 685000, tzinfo=datetime.timezone.utc), '\\\\Jobs'), 
            ('JobDefn', 'RunCommand2', datetime.datetime(2021, 4, 6, 12, 0, 48, 589000, tzinfo=datetime.timezone.utc), '\\\\Jobs'), 
            ('JobDefn', 'RunCommand3', datetime.datetime(2021, 4, 8, 16, 4, 20, 516000, tzinfo=datetime.timezone.utc), '\\\\Jobs'), 
            ('JobDefn', 'RunCommand4', datetime.datetime(2021, 4, 9, 15, 11, 28, 998000, tzinfo=datetime.timezone.utc), '\\\\SteTest'), 
            ('JobDefn', 'RunCommand5', datetime.datetime(2021, 4, 15, 16, 28, 9, 708000, tzinfo=datetime.timezone.utc), '\\\\SteTest\\\\SubFolder1')]
        }

    #components_list=components_list_test

    print(components_list)

    def ExportComponentList(export_base_dir='/var/repo_base/default', components_list={}):

        import os
        import re


        for project_namespace_tuple, job_details in components_list.items():
            engine_host=project_namespace_tuple[0]
            project=project_namespace_tuple[1]
            logMessage.info('Exporting Jobs from ' + engine_host + ':/' + project ) 

            for job_info in job_details:
                logMessage.info('Exporting Jobs ' + job_info[3]  ) 

                #Create path for archive file
                
                component_name=job_info[1]
                category=re.sub(r"\\\\",os.sep,job_info[3])   # Convert to using os.sep ('/')
                category_path=re.sub(r"^"+os.sep,'',category) # Remove the leading '/'
                archive_dir_path=os.path.join(export_base_dir,project,category_path,component_name)

                if ( not(os.path.exists(archive_dir_path))):
                    os.makedirs(archive_dir_path,0o755)

                archive_file=component_name + '.isx'

                archive_path=os.path.join(archive_dir_path, archive_file)


                # Export the job
                import subprocess   
                
                ds_pattern=engine_host + '/' + project + '/' + '*'  + '/'+ component_name + '.*'
                command_to_run_old='/iis/01/InformationServer/Clients/istools/cli/istool.sh export -archive ' + archive_path + ' -up -ds "hn01/dstage1/*/'+component_name + '.*" -u isadmin -p default;'
                command_to_run='/iis/01/InformationServer/Clients/istools/cli/istool.sh export -archive ' + archive_path + ' -up -ds "' +ds_pattern + '" -u isadmin -p default;'
    
                ## Annoying
                import sys
                if sys.version_info >= (3,7):
                    result = subprocess.run([command_to_run] , capture_output=True, shell=True, encoding="UTF-8")
                else: 
                    result = subprocess.run([command_to_run] , shell=True, encoding="UTF-8", stdout=subprocess.PIPE)
                
                if result.returncode != 0:
                    logMessage.warning('Export of ' + component_name + ' ended with return code ' + str(result.returncode) + '. stdout : ' + result.stdout + '. stderr: ' + result.stderr )
                else:
                    logMessage.debug('Export of ' + component_name + ' ended with return code ' + str(result.returncode) + '. stdout : ' + result.stdout + '. stderr: ' + str(result.stderr) )
                    

      


                
            

        logMessage.info('Export to ' +  archive_path + ' finished .')

    
    ExportComponentList(export_base_dir='/var/git/test1_repo/code_sheff/DataStageJobsTest1', components_list=components_list)
    logMessage.info('Done')











    
        

        
    

if __name__=="__main__":
    main()
