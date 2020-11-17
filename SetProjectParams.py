#!/usr/bin/env python3

"""
This script will 
  * take in path to a param file?( format?), which contains project parameter definitions.
  * take the standard DSParams from Template, 
  * apply the standard parameter definitions to it .
  * apply the project parameter definitions to it 
  * create a new DSParams file.
  * compare the new DSParams file with the current active one for the project. If it has changed, it will back up the current one, and move the new one into place.

"""
import sys
import argparse

import re
import os 




def GetProjectParamConfig(filePath=''):
    """
    This should really take  in a path to the config file
    Returns json object

    Definitions are taken from the DSParam file.
    i.e 

    <EnvVarName> is the name of the enviroment variable that will be set in OSH
    <Category> is the category name where the environment variable will appear.  In format <cat1>/<subcat1>/<subcat2>/... etc
    <JobType> is the job type number (0 = Server, 3 = Parallel, -1 = all)
    <Type> is one of: Number, String, FilePath, DirPath, List, Boolean, UserDef
                   If List, then format of Type is futher divided: ...<EnvVarName>\List/<Item1>/<ItemDisplay1>/<Item2>/<ItemDisplay2>\<Scope>...
                     (ItemDisplay values must be left blank here, and added as localised strings in envvar.cls
                   If Boolean, then the value the envvar is set to should be irrelevant
                   If proceeded by a '+' character, then the value set here is appended to any existing value already set in the shell,
                   separated by a ':' character
    <Default> The default value
    <SetAction> What action should be taken when setting the environment variable at job run time:
                        0 = Always set if the environment variable has been overriden.
                        1 = Only set the environment variable if its value is different to its default
                        2 = Explicitly unset the environment variable if the value is set to the default, otherwise same as 1
                        3 = Always set the environment variable
                        4 = Osh Boolean. Set if true, no action if false
    <Scope> is one of: Project, Design, RunTime
    <PromptText> is the text displayed to prompt the user for the env var. If "" then <EnvVarName> will be used
    <HelpText> is a longer description of the env var.

  

"""
    ## Really all we need here is 
    #    For all fields below, if EnvVarName already exists  - defaults to existing.
    #    Only allow definition to change for User Defined
    # EnvVarName - This is required
    # Category  -- if already exists  - defaults to existing. If does not exist, defaults to "User Defined".
    # Type -- defaults to String
    # PromptText --defaults to EnvVarName
    # Default  -- defaults to unset - for user defined Default is always empty in the definition but then record is set in the EnvVarValues to set it.
    # SetAction  -- defaults to 0
    # Scope -- defaults to Project
    # HelpText -- defaults to PromptText
    ## Actually, we maybe we should remove some of this fields, as we're just going to ignore them anyway. Only really valid for non-UserDefinined.
    ## I'll start with the assumption that anything that comes from the parameter is either existing in template ( in which case we just use the values already in the definition), or is user definined.

    ## For user defined, only valid fields are:
    # EnvVarName
    # Type - defaults to String
    # Default - will actualy be used to set the Value ( Default in definition will stay as empty)
    # PromptText



    projectParamConfig= [
        {
            "EnvVarName": "MyVariable",
            "Category": "User Defined",
            "JobType": "-1", 
            "Type": "String",
            "Default": "default_value",
            "SetAction" : "0",
            "Scope" :  "Project",
            "PromptText" : "Prompty prompt prompt."
        },
        {
            "EnvVarName": "MyVariable2",
            "Category": "User Defined",
            "JobType": "-1",
            "Type": "String",
            "Default": "default_value",
            "SetAction" : "0",
            "Scope" :  "Project",
            "PromptText" : "Prompty prompt prompt.",
            "HelpText" : "This is helpful."
        },
        {
            "EnvVarName": "MyVariableMinDefn"            
        },
        {
            "EnvVarName": "MyUnsetVariable",
            "Default": "It's set now!"

        },
        {
            "EnvVarName": "APT_CONFIG_FILE",
            "PromptText" : "Prompty prompt prompt.",     # this should get ignored as it's not user defined.
            "Default": "/tmp/myconfig.apt"
        }
    ]

    return projectParamConfig

def GetProjectParamConfig_DodgyCopyForStandardParamsTest(filePath=''):
    """
    This should really take  in a path to the config file
    Returns json object

    Definitions are taken from the DSParam file.
    i.e 

    <EnvVarName> is the name of the enviroment variable that will be set in OSH
    <Category> is the category name where the environment variable will appear.  In format <cat1>/<subcat1>/<subcat2>/... etc
    <JobType> is the job type number (0 = Server, 3 = Parallel, -1 = all)
    <Type> is one of: Number, String, FilePath, DirPath, List, Boolean, UserDef
                   If List, then format of Type is futher divided: ...<EnvVarName>\List/<Item1>/<ItemDisplay1>/<Item2>/<ItemDisplay2>\<Scope>...
                     (ItemDisplay values must be left blank here, and added as localised strings in envvar.cls
                   If Boolean, then the value the envvar is set to should be irrelevant
                   If proceeded by a '+' character, then the value set here is appended to any existing value already set in the shell,
                   separated by a ':' character
    <Default> The default value
    <SetAction> What action should be taken when setting the environment variable at job run time:
                        0 = Always set if the environment variable has been overriden.
                        1 = Only set the environment variable if its value is different to its default
                        2 = Explicitly unset the environment variable if the value is set to the default, otherwise same as 1
                        3 = Always set the environment variable
                        4 = Osh Boolean. Set if true, no action if false
    <Scope> is one of: Project, Design, RunTime
    <PromptText> is the text displayed to prompt the user for the env var. If "" then <EnvVarName> will be used
    <HelpText> is a longer description of the env var.

  

"""
    ## Really all we need here is 
    #    For all fields below, if EnvVarName already exists  - defaults to existing.
    #    Only allow definition to change for User Defined
    # EnvVarName - This is required
    # Category  -- if already exists  - defaults to existing. If does not exist, defaults to "User Defined".
    # Type -- defaults to String
    # PromptText --defaults to EnvVarName
    # Default  -- defaults to unset - for user defined Default is always empty in the definition but then record is set in the EnvVarValues to set it.
    # SetAction  -- defaults to 0
    # Scope -- defaults to Project
    # HelpText -- defaults to PromptText
    ## Actually, we maybe we should remove some of this fields, as we're just going to ignore them anyway. Only really valid for non-UserDefinined.
    ## I'll start with the assumption that anything that comes from the parameter is either existing in template ( in which case we just use the values already in the definition), or is user definined.

    ## For user defined, only valid fields are:
    # EnvVarName
    # Type - defaults to String
    # Default - will actualy be used to set the Value ( Default in definition will stay as empty)
    # PromptText



    projectParamConfig= [
        {
            "EnvVarName": "MyVariable",
            "Category": "User Defined",
            "JobType": "-1", 
            "Type": "String",
            "Default": "default_value",
            "SetAction" : "0",
            "Scope" :  "Project",
            "PromptText" : "Prompty prompt prompt.",
            "HelpText" : "This is helpful - and from standard ."
        },
        {
            "EnvVarName": "MyVariable2",
            "Category": "User Defined",
            "JobType": "-1",
            "Type": "String",
            "Default": "default_value",
            "SetAction" : "0",
            "Scope" :  "Project",
            "PromptText" : "Prompty prompt prompt.",
            "HelpText" : "This is helpful."
        },
        {
            "EnvVarName": "MyVariableMinDefn"            
        },
        {
            "EnvVarName": "Standard1", 
            "PromptText" : "Standard prompt prompt.",     # this should get ignored as it's not user defined.
            "Default": "/tmp/standardconfig.apt"           
        },
        {
            "EnvVarName": "MyUnsetVariable",
            "Default": "It's set now!"

        },
        {
            "EnvVarName": "APT_CONFIG_FILE",
            "PromptText" : "Standard prompt prompt.",     # this should get ignored as it's not user defined.
            "Default": "/tmp/standardconfig.apt"
        }
    ]

    return projectParamConfig

def GetLogger():

    
    import logging

    ##Maybe this should be a class really. Something I set up once at start of script, rather than reimporting every time we log a message.

    # Set up logging 2x. One for logging to file, and one for logging to screen.
    # You can control the logging level to each separately - and also at top level
    
    # log - general 
    log = logging.getLogger('logger')
    log.setLevel(logging.DEBUG)     #  this is initial filter. Messages have to be above this to get anywhere.

    formatter = logging.Formatter('%(asctime)s : %(levelname)s -  %(message)s  ( from %(filename)s -> %(module)s) -> %(funcName)s')
    
    # fh - logging filehandler
    fh = logging.FileHandler('/tmp/test.log', mode='w', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    # ch - logging streamhandler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO) ## Change to DEBUG while testing. Should just be INFO normally
    ch.setLevel(logging.DEBUG) ## Change to DEBUG while testing. Should just be INFO normally
    ch.setFormatter(formatter)
    log.addHandler(ch)

    return log


class EnvVarDefn():
    def __init__(self, EnvVarName,Category,JobType,Type,Default,SetAction,Scope,PromptText,HelpText):
        #print('Initialising a LogMessage object.')
        self.EnvVarName=EnvVarName
        self.Category=Category
        self.JobType=JobType
        self.Type=Type
        self.Default=Default
        self.SetAction=SetAction
        self.Scope=Scope
        self.PromptText=PromptText
        self.HelpText=HelpText

    
class EnvVarValue():
    def __init__(self, EnvVarName,EnvVarValue):
        #print('Initialising a LogMessage object.')
        self.EnvVarName=EnvVarName
        self.WhatIsThis='1'
        self.EnvVarValue=EnvVarValue        
        
    
class EnvVar():
    def __init__(self, EnvVarName,EnvVarDefn,EnvVarValue ):
        self.EnvVarName=EnvVarName
        self.EnvVarDefn=EnvVarDefn
        self.EnvVarValue=EnvVarValue
    
    def print_definition(self):

        #Create output line in format 
        # Format is: <EnvVarName>\<Category>\<JobType>\<Type>[+]\<Default>\<SetAction>\<Scope>\<PromptText>\<HelpText>
        separator='\\'
         
        return separator.join( (self.EnvVarDefn.EnvVarName, self.EnvVarDefn.Category, self.EnvVarDefn.JobType, self.EnvVarDefn.Type, self.EnvVarDefn.Default, self.EnvVarDefn.SetAction, self.EnvVarDefn.Scope, self.EnvVarDefn.PromptText, self.EnvVarDefn.HelpText) ) 
    
    def print_value(self):
        return 'This is my formatted value line'
        

def GetLinesFromDSParam(filePath='',sectionStartPattern=r'^\[EnvVarDefns\] *',sectionEndPattern=r'^\[.*\] *',pattern_toMatch=r'^.*$' ):
    """ 
    Get lines from DSParam file
    sectionStartPattern=r'^\[EnvVarDefns\] *'
    sectionEndPattern=r'^\[.*\] *'    ## or end of file
    
    pattern_toMatch=r'^(\w*)\\User Defined\\.*$'
    """

    try:
        f = open(filePath)
    except OSError:
        return None


    return_lines=[]
    sectionFound=False

    for line in f:
        # We are only interested in the section '[EnvVarDefns]'
        # If you find the start of the section, then set sectionFound to True, and continue processesing from next line
        if re.search(sectionStartPattern,line):
            sectionFound=True
            continue
        
        # If you get to the end of the section, stop processing
        if sectionFound == True:
            if re.search(sectionEndPattern,line):
                break
            else:
                # Format is: <EnvVarName>\<Category>\<JobType>\<Type>[+]\<Default>\<SetAction>\<Scope>\<PromptText>\<HelpText>
                # DSIPC_OPEN_TIMEOUT\Parallel/Operator Specific\3\Number\30\3\Project\IPC Open timeout\Specifies the time allowed for server shared containers and Basic Transformers to complete initialization.
                # APT_PXDEBUGGER_FORCE_SEQUENTIAL\Parallel\3\String\\2\Project\Debugger force sequential\Double quoted string containing a space separated list of operators to be forced to run sequentially when running in the debugger.
                # APT_LINKOPT\Parallel/Compiler\3\String\-shared -m64\3\Project\Linker options\Linker options for Parallel transformer\
                # APT_USE_CRLF\Parallel/Operator Specific\3\Boolean\0\4\Project\Default to Windows format files\Default to Windows format files (carriage return, line feed) if unspecified for sequential stages. Otherwise sequential files default to UNIX format.
            

                # Seems that some fields have a '\' at the end of the HelpText Field
                fields = line.split('\\')

                #Basic check to make sure record is as expected
                if len(fields) != 9 and len(fields) != 10 :
                    logMessage.error('Unexpected number of fields in line in DSParams. Expected 9. Found ' + str(len(fields)) + '. Line is :' + line)
            
                #Skip through til you get to the user definined variables
                #pattern_UserDefined=r'^(\w*)\\User Defined\\.*$'
                if re.search(pattern_toMatch, line) == None:
                    continue

            
            # This is if its EnvVarDefn that we're getting.
            return_lines.append(line)
    
    f.close
    return(return_lines)

def GetDSParamValues(filePath='',sectionName='EnvVarDefns',pattern_toMatch=r'^(\w*)\\User Defined\\.*$'):
    """
    Get values from a DSParam file and load them to a format we can process
    We only need to look at user defined variables, and variable the have a value set. ( Assume the rest can stay as default.)

    sectionName  - which section of DSParams to look at. Defaults to EnvVarDefns
    pattern_toMatch - limit results to only those that match certain pattern, e.g r'^(\w*)\\User Defined\\.*$'


    returns EnvVars objects



    """
    import re

    ## Trying to set it up so it uses same object if it already exists
    #logMessage=SetUpLog()
    # If I just set it up in main script it works.
    # Am I going to have to put this try block in every function that uses logging?
    # Maybe just better to just import my LogMessages class each time and create as new local object.

    #try:
    #    logMessage.debug('Entered function GetDSParamValues')
    #except:
    #    logMessage=LogMessage()
    #    logMessage.debug('Entered function GetDSParamValues')

    

    # def GetLinesFromDSParam(filePath='',sectionStartPattern=r'^\[EnvVarDefns\] *',sectionEndPattern=r'^\[.*\] *',pattern_toMatch=r'^.*$' ):
    #     """ 
    #     Get lines from DSParam file
    #     sectionStartPattern=r'^\[EnvVarDefns\] *'
    #     sectionEndPattern=r'^\[.*\] *'    ## or end of file
        
    #     pattern_toMatch=r'^(\w*)\\User Defined\\.*$'
    #     """

    #     try:
    #         f = open(filePath)
    #     except OSError:
    #         return None


    #     return_lines=[]
    #     sectionFound=False

    #     for line in f:
    #         # We are only interested in the section '[EnvVarDefns]'
    #         # If you find the start of the section, then set sectionFound to True, and continue processesing from next line
    #         if re.search(sectionStartPattern,line):
    #             sectionFound=True
    #             continue
            
    #         # If you get to the end of the section, stop processing
    #         if sectionFound == True:
    #             if re.search(sectionEndPattern,line):
    #                 break
    #             else:
    #                 # Format is: <EnvVarName>\<Category>\<JobType>\<Type>[+]\<Default>\<SetAction>\<Scope>\<PromptText>\<HelpText>
    #                 # DSIPC_OPEN_TIMEOUT\Parallel/Operator Specific\3\Number\30\3\Project\IPC Open timeout\Specifies the time allowed for server shared containers and Basic Transformers to complete initialization.
    #                 # APT_PXDEBUGGER_FORCE_SEQUENTIAL\Parallel\3\String\\2\Project\Debugger force sequential\Double quoted string containing a space separated list of operators to be forced to run sequentially when running in the debugger.
    #                 # APT_LINKOPT\Parallel/Compiler\3\String\-shared -m64\3\Project\Linker options\Linker options for Parallel transformer\
    #                 # APT_USE_CRLF\Parallel/Operator Specific\3\Boolean\0\4\Project\Default to Windows format files\Default to Windows format files (carriage return, line feed) if unspecified for sequential stages. Otherwise sequential files default to UNIX format.
                

    #                 # Seems that some fields have a '\' at the end of the HelpText Field
    #                 fields = line.split('\\')

    #                 #Basic check to make sure record is as expected
    #                 if len(fields) != 9 and len(fields) != 10 :
    #                     logMessage.error('Unexpected number of fields in line in DSParams. Expected 9. Found ' + str(len(fields)) + '. Line is :' + line)
                
    #                 #Skip through til you get to the user definined variables
    #                 #pattern_UserDefined=r'^(\w*)\\User Defined\\.*$'
    #                 if re.search(pattern_toMatch, line) == None:
    #                     continue

                
    #             # This is if its EnvVarDefn that we're getting.
    #             return_lines.append(line)
        
    #     f.close
    #     return(return_lines)







    try: 
        logMessage.debug('Entered function GetDSParamValues')
        #logMessage.debug('We are reading values from ' + filePath + ' .')
    except NameError:
        print('This is the except NameError')
    except:
        print('this is just general except.')
    else:
        print('this is when no exception happened.')
    finally:
        print('This is the finally section. It will aways run')
        print('This is the finally section. It will aways run')
    
    logMessage.info('We got to here.')

    # First, try to open the file
    #try:
    #    f = open(filePath)
    #except OSError:
    #    return None

    # Now process the file
    #characters = {}
    #sectionStartPattern=r'^\[EnvVarDefns\] *'
    sectionStartPattern=r'^\[' + sectionName + '\] *'
    sectionEndPattern=r'^\[.*\] *'    ## or end of file
    # pattern_toMatch=r'^(\w*)\\User Defined\\.*$'  - this is now a param
    #envvar=[]
    EnvVarDefns_lines=GetLinesFromDSParam(filePath,sectionStartPattern, sectionEndPattern, pattern_toMatch )
    EnvVarDefns={}
    for line in EnvVarDefns_lines:
        #EnvVarDefn(EnvVarName = fields[0], Category= fields[1], JobType= fields[2], Type= fields[3], Default= fields[4], SetAction=fields[5], Scope=fields[6], PromptText=fields[7], HelpText=fields[8] ) )
        #EnvVarDefn(EnvVarName = fields[0], Category= fields[1], JobType= fields[2], Type= fields[3], Default= fields[4], SetAction=fields[5], Scope=fields[6], PromptText=fields[7], HelpText=fields[8] ) )
        EnvVarName, Category, JobType, Type, Default, SetAction, Scope, PromptText, HelpText  = line.split('\\')[:9]
        EnvVarDefns[EnvVarName] = EnvVarDefn(EnvVarName, Category, JobType, Type, Default, SetAction, Scope, PromptText, HelpText)


    sectionStartPattern=r'^\[EnvVarValues\] *'
    sectionEndPattern=r'^\[.*\] *'    ## or end of file
    #pattern_toMatch=r'^(\w*)\\User Defined\\.*$'
    EnvVarValues_lines=GetLinesFromDSParam(filePath,sectionStartPattern, sectionEndPattern )

    EnvVarValues={}
    for line in EnvVarValues_lines:
        envVarNameQuoted, parp, envVarValue = line.split('\\')
        envVarName = envVarNameQuoted.replace('"','')
        EnvVarValues[envVarName] = EnvVarValue(envVarNameQuoted, envVarValue)


    ## So curently we have all UserDefinedEnvVarDefns_lines and all EnvVarValues. 

    
    ## return a dictionary of EnvVar objects

    ## How to update if exists - and just update the relent part?
    #class EnvVar():
    #def __init__(self, EnvVarName,EnvVarDefn,EnvVarValue ):
    #    self.EnvVarName=EnvVarName
    #    self.EnvVarDefn=EnvVarDefn
    #    self.EnvVarValue=EnvVarValue
    EnvVars={}
    for env_var_name, envVarDefn in EnvVarDefns.items():
        if env_var_name in EnvVars:
            EnvVars[env_var_name].EnvVarDefn = envVarDefn # Need to check if it exists really, and just update if already exists
        else:
            EnvVars[env_var_name]= EnvVar(env_var_name,envVarDefn,None )
    
    ## loop through dictionary, getting the key 'env_var_name' and the value 'env_var_value'
    for env_var_name, env_var_value in EnvVarValues.items():
        if env_var_name in EnvVars:
            EnvVars[env_var_name].EnvVarValue = env_var_value # Need to check if it exists really, and just update if already exists
        else:
            EnvVars[env_var_name]= EnvVar(env_var_name,None,EnvVarValue )


        




    return EnvVars



    

    
    




def HandleInputParameters():
    
    this_script_path=(os.path.dirname(sys.argv[0]))
    #print('this_script_path:' + this_script_path)
    # this_script_name=(os.path.basename(sys.argv[0]))
    datadir=os.path.join(this_script_path,"data") # Ah!  you don't want the '/' in your args - makes sense!
    #print('datadir:' + datadir)
    
    default_logfile=os.path.join(datadir,"syslog_example")
    #print('default is :' + default_logfile)

    #default_DSParams_template=os.path.abspath(os.path.join(this_script_path, 'TestFiles','DSParams.template'))
    default_DSParams_template=os.path.abspath(os.path.join(this_script_path, 'TestFiles','DSParams.example'))
    # Set up input options
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--logfile", type=str, dest="logfile", help="the logfile to be processed", default=default_logfile)
    parser.add_argument("--install-base", type=str, dest="install_base", help="The base of the DS install. e.g /iis/01 .", default='/iis/01')
    parser.add_argument("--template-dsparam", type=str, dest="template_dsparam", help="the template DSParam file", default=default_DSParams_template)
    parser.add_argument("--project-name", type=str, dest="project_name", help="project to check, and apply changes to ", default='dstage1')
    
    
    return parser

class LogMessage():
    def __init__(self):
        #print('Initialising a LogMessage object.')
        self.log=GetLogger()
    
    def __getFunctionNames(self):
        import traceback
        trace_b=traceback.extract_stack(limit=None)
        
        # Loop backwards through stack , to get function names
        funcs=[]
        for i in range( len(trace_b) - 1, -1, -1):
            # If we hit '<module>', then stop. I assume this is as far as we need to go.
            if trace_b[i][2] == '<module>':
                break
            funcs.append(trace_b[i][2])  

        return(str(funcs))

    def info(self, message):
        """
        This method is to log info
        """
        self.log.info(message + ' ---> ' + self.__getFunctionNames())
    
    def debug(self, message):
        """
        This method is to log info
        """
        self.log.debug(message + ' ---> ' + self.__getFunctionNames())
    
    def error(self, message):
        """
        This method is to log error
        """
        self.log.error(message + ' ---> ' + self.__getFunctionNames())



def ReplaceOldWithNewFile(orig_file='', new_temp_file=''):
    """
    Compare original file and the new temp file  ( contents and permissions).
    If they are the same, just remove the temp version. ( maybe not needed, handled in calling function)
    If they are different, backup original and then replace teh orig_file with the new_temp_file

    Return code values:
    0: No changes made
    1: Changes made
    """


    import os
    import time
    import shutil

    # If file exists, 
    if os.path.exists(orig_file):
    
        import filecmp
        content_matches=filecmp.cmp(orig_file,new_temp_file)
        permission_matches=os.stat(orig_file).st_mode == os.stat(new_temp_file).st_mode
        user_matches=os.stat(orig_file).st_uid == os.stat(new_temp_file).st_uid
        group_matches=os.stat(orig_file).st_gid == os.stat(new_temp_file).st_gid

        logMessage.info( 'Checking file ' + orig_file + '. content_matches:' + str(content_matches) + '; permission_matches:' + str(permission_matches) + ';  user_matches:' + str(user_matches) + ';  group_matches:' + str(group_matches))

        if content_matches and permission_matches and user_matches and group_matches:
            logMessage.info(orig_file + ' is unchanged.')
            os.remove(new_temp_file)
            return 0
        else:
            # backup the original file
            t = time.localtime()
            backupfile=orig_file + time.strftime('%b-%d-%Y_%H%M', t)
            shutil.copyfile(orig_file,backupfile)
    else:
        logMessage.info(orig_file + ' - does not exist. Creating new file.')
    
    ## Only got to here if does not match  (ie new or different)
    logMessage.info(orig_file + ' - has been amended. ( to match ' + new_temp_file + ' )')
    shutil.copyfile(new_temp_file, orig_file)
    return 1




def GetAmendedEnvVars(origEnvVar={}, templateDSParamsPath='' , params_to_update=[]):
    """
    Update EnvVar object with definitions of variables that are in the 'params_to_update'

    Start from template DSParams...then apply stuff from origEnvVar (ie. the dictionary you've already done some updates to ) then apply stuff from params_to_update ( e.g standard or project specific config)
    """

    # Get Full set of Env Var definitions from the DSParam file, and store as a EnvVar object
    myTemplateEnvVar=GetDSParamValues(filePath=templateDSParamsPath, sectionName='EnvVarDefns', pattern_toMatch=r'^.*$') 
    myOutputEnvVar_ToApply = origEnvVar


    ## Get values from project specific params, and apply them to the EnvVar object. params_to_update is a list of dictionaries, each dictionary defines a variable
    ##    
    for variable_definition in params_to_update:

        
        ## Look for the variable in the EnvVar object
        envvar_name=variable_definition['EnvVarName']
        if envvar_name in myTemplateEnvVar:
            print(envvar_name + ' exists in myTemplateEnvVar')
            # Copy it to my output env var - nb. This is just creating new obj referencing the original..so updates will be seen in both! ( This should not matter though, in current process)
            myOutputEnvVar_ToApply[envvar_name]=myTemplateEnvVar[envvar_name]

            ## Check if it is user defined. ( for non-user defined, then we do not change the definition, only the value)
            
            if myOutputEnvVar_ToApply[envvar_name].EnvVarDefn.Category == 'User Defined':
                ## For user defined, update each variable based on what's in the params_to_update

                ## Update existing User Defined Variable based on contents of variable_definition
                if 'Type' in variable_definition:
                    myOutputEnvVar_ToApply[envvar_name].EnvVarDefn.Type = variable_definition['Type']
                
                if 'PromptText' in variable_definition:
                    myOutputEnvVar_ToApply[envvar_name].EnvVarDefn.PromptText = variable_definition['PromptText']

                if 'Default' in variable_definition:
                    pass 
                    # For 'Default' we actually set the value in the 
                
                if 'Default' in variable_definition:
                    myEnvVarValue=EnvVarValue(EnvVarName=envvar_name, EnvVarValue=variable_definition['Default'] )
                else:
                    # If variable is defined with no Default here, this should cause the variable to be unset.(i.e this overrides any previous default that existed in the template DSParam)
                    myEnvVarValue = None
                
                myOutputEnvVar_ToApply[envvar_name].EnvVarValue = myEnvVarValue
                
            else: 
                
                myEnvVarValue=EnvVarValue(EnvVarName=envvar_name, EnvVarValue=variable_definition['Default'] )
                myOutputEnvVar_ToApply[envvar_name].EnvVarValue=myEnvVarValue
                
                

        else:
            ## This variable does not already exist, so will be created as user defined
            ## e.g. MyUnsetVariable\User Defined\-1\String\\0\Project\This is my unset variable - it has no value set.\
            print(envvar_name + ' does not exists in myEnvVar')

            ## Create new User Defined Variable based on contents of variable_definition

            if 'Default' in variable_definition:
                myEnvVarValue=EnvVarValue(EnvVarName=envvar_name, EnvVarValue=variable_definition['Default'] )
            else:
                # No need to store value object
                myEnvVarValue = None
                
            # EnvVarName
            # Type - defaults to String
            # Default - will actualy be used to set the Value ( Default in definition will stay as empty)
            # PromptText
            if 'Type' in variable_definition:
                varType=variable_definition['Type']
            else:
                varType='String'
                
            
            if 'PromptText' in variable_definition:
                varPromptText=variable_definition['PromptText']
            else:
                varPromptText=variable_definition['EnvVarName']
                

            myEnvVarDefn=EnvVarDefn(EnvVarName=envvar_name,
                                        Category='User Defined' , 
                                        JobType='-1' , 
                                        Type=varType, 
                                        Default='', 
                                        SetAction='0', 
                                        Scope='Project', 
                                        PromptText=varPromptText, HelpText='hello')

            # Now update  myEnvVar with the value and definition                    
            myOutputEnvVar_ToApply[envvar_name]=EnvVar(EnvVarName=envvar_name, EnvVarDefn= myEnvVarDefn, EnvVarValue=myEnvVarValue)



    

    return myOutputEnvVar_ToApply




    

def CheckFixDSParams(dsparams_path='/tmp/stetest1', templateDSParamsPath='', standard_params=[], project_specific_params=[]):
    """
    This function will take in a path to a template DSParams file, and a list of dictionaries for the project specific parameter settings.
    TemplateDSParamsPath could be pointing to the Templates folder, or some other DSParams file  ( e.g if we're building one in multiple stages ..starting from template..apply standard...create new temp.. use new temp as template, apply project specific changes)

    It combines them to produce a new file ( or should it be a new object in the program???. Lets decide in a bit )    

    If it creates output file.. then should the path to that be a param too?
    """

    #UserDefinedEnvVarDefns={}
    #EnvVarValues={}
    #UserDefinedEnvVarDefns, EnvVarValues = GetDSParamValues(templateDSParamsPath)
    
    ## Get dictionary of all variables to amend.
    amendedEnvVars=GetAmendedEnvVars(origEnvVar={}, templateDSParamsPath=args.template_dsparam , params_to_update=standard_params)
    amendedEnvVars=GetAmendedEnvVars(origEnvVar=amendedEnvVars, templateDSParamsPath=args.template_dsparam , params_to_update=project_specific_params)


    
        ## I think that whole section above my not be needed actually
        ##  Could just to this:
           
        ##  Create myEnvVar - Needs to contain all User Defined, and any Values that are set  
        ##  Create new output 'temp' file
        ##  Read template file
        ##  For each line.
        ##      if its not in relevent section ( EnvVarValues or EnvVarDefn)m the write it out unchanged to new temp file
        ##      for EnvVarDefn section
        ##         Compared line it with what's in myEnvVar,
        ##         If found in myEnvVar
        ##            If matches, write it out as is - only valid for User Definited though
        ##            If does not match, write out the new version



    try:
        f = open(templateDSParamsPath)
    except OSError:
        logMessage.error('Unable to open the template DSParam file :' + templateDSParamsPath )
        return None
    
    ## This creates a temp file that will be removed once it is closed.
    ## Then use normal open to open the same file so that we can write to it as normal
    import tempfile
    fp = tempfile.NamedTemporaryFile()

    try:
        f_temp = open(fp.name,'w')
    except OSError:
        logMessage.error('Unable to open the temp file :' + f_temp )
        return None
 
    ##  Read each line from template file
    currentSection=None
    ## Build up the pattern for matching the EnvVarDefn format
    pattern_separator='\\'
    pattern_EnvVarName=r'(\w*)'
    pattern_Category=r'(\w*[/\w ]*)'
    pattern_JobType=r'([-]*\d)'
    pattern_Type=r'(\w*[/\w+]*)'
    pattern_Default=r'(.*?)'
    pattern_SetAction=r'(\d)'
    pattern_Scope=r'(\w*)'
    pattern_PromptText=r'(.*?)'
    pattern_HelpText=r'(.*)$'

    #EnvVarDefnFormat=r'^(\w*)\\(\w*[/\w ]*)\\(\d)\\(\w*[/\w]*)\\(.*?)\\.*'; result = re.search(EnvVarDefnFormat, line); print(result[5])
    EnvVarDefnFormat=r'^' 
    EnvVarDefnFormat+=pattern_EnvVarName
    EnvVarDefnFormat+=r'\\'
    EnvVarDefnFormat+=pattern_Category
    EnvVarDefnFormat+=r'\\'
    EnvVarDefnFormat+=pattern_JobType
    EnvVarDefnFormat+=r'\\'
    EnvVarDefnFormat+=pattern_Type
    EnvVarDefnFormat+=r'\\'
    EnvVarDefnFormat+=pattern_Default
    EnvVarDefnFormat+=r'\\'
    EnvVarDefnFormat+=pattern_SetAction
    EnvVarDefnFormat+=r'\\'
    EnvVarDefnFormat+=pattern_Scope
    EnvVarDefnFormat+=r'\\'
    EnvVarDefnFormat+=pattern_PromptText
    EnvVarDefnFormat+=r'\\'
    EnvVarDefnFormat+=pattern_HelpText

    for line in f:
        
        
        ## Work out what section we're in.
        sectionStartPattern=r'^\[([\w-]*)\]'
        result = re.search(sectionStartPattern,line)
        if result != None:
            sectionFound=True
            previousSection=currentSection # When Section changes, save off the previousSection name. 
            currentSection=result[1]


            # If section change, and previous section was EnvVarDefns, need to make sure any EnvVarDefns which have not been processed from amendedEnvVars are written out.
            if previousSection == 'EnvVarDefns':
                
                for env_var_name, env_var_object in amendedEnvVars.items():
                    print('processing ' + env_var_name )
                    if env_var_object.EnvVarDefn != None:
                        print('processing definition for  ' + env_var_name )
                        print('THIS IS WHERE YOU ARE UP TO STEPHEN! ')
                        ## Need to add in bit for adding these ( user defined ) variable definitions
                        ### Then need to add code for setting the values in the values section.


            logMessage.info('Processing ' + currentSection)
        else:
            if currentSection == 'EnvVarDefns':

                # Check it matches our expected format
                #EnvVarDefnFormat=r'^(\w*)\(\w*)\3\String\\2\Project\Debugger force sequential\Double quoted string containing a space separated list of operators to be forced to run sequentially when running in the debugger.
                #EnvVarDefnFormat=r'^(\w*)\\(\w*)\\(\d)\\(\w)\\\\(\d)\\(\w)\\([\w\.]*)'
                # See if this env var defn is amended by our config
                #print(project_specific_params)
                result = re.search(EnvVarDefnFormat, line)
                if result != None:
                    logMessage.info('Processing ' + result[1])

                    #First, does the envvar exist in either the 'standard' or 'project specific' ( ie. does it need changing)
                    # Check if it's in amendedEnvVars
                    envvar_name=result[1]
                    envvar_category=result[2]
                    envvar_jobtype=result[3]
                    envvar_type=result[4]
                    envvar_default=result[5]
                    envvar_set_action=result[6]
                    envvar_scope=result[7]
                    envvar_prompt_text=result[8]
                    envvar_help_text=result[9]


                    #Could change this to only update if user defined - as they are only ones that should be able to change definition.  Should already be handled though, so doesn't matter really.
                    ## Remove the definition from amendedEnvVars once you've processed it. ( but leave that value - we need to set that later)
                    if envvar_name in amendedEnvVars:
                        line=amendedEnvVars[envvar_name].print_definition()
                        amendedEnvVars[envvar_name].EnvVarDefn = None


                else:
                    logMessage.info('Line does not match expected format for a variable' + line)
                    # Would be nice to move this debug code to some other function, to keep this code a bit shorter. 
                    EnvVarDefnFormat=r'^' + pattern_EnvVarName
                    result = re.search(EnvVarDefnFormat, line)
                    logMessage.debug('EnvVarName :  ' + result[1])
                    
                    EnvVarDefnFormat+=r'\\' + pattern_Category
                    result = re.search(EnvVarDefnFormat, line)
                    if result == None:
                        continue
                    logMessage.debug('Category :  ' + result[2])

                    EnvVarDefnFormat+=r'\\' + pattern_JobType
                    result = re.search(EnvVarDefnFormat, line)
                    if result == None:
                        continue
                    logMessage.debug('JobType :  ' + result[3])

                    EnvVarDefnFormat+=r'\\' + pattern_Type
                    result = re.search(EnvVarDefnFormat, line)
                    if result == None:
                        continue
                    logMessage.debug('Type :  ' + result[4])

                    EnvVarDefnFormat+=r'\\' + pattern_Default
                    result = re.search(EnvVarDefnFormat, line)
                    if result == None:
                        continue
                    logMessage.debug('Default :  ' + result[5])

                    EnvVarDefnFormat+=r'\\' + pattern_SetAction
                    result = re.search(EnvVarDefnFormat, line)
                    if result == None:
                        continue
                    logMessage.debug('SetAction :  ' + result[6])

                    EnvVarDefnFormat+=r'\\' + pattern_Scope
                    result = re.search(EnvVarDefnFormat, line)
                    if result == None:
                        continue
                    logMessage.debug('Scope :  ' + result[7])

                    EnvVarDefnFormat+=r'\\' + pattern_PromptText
                    result = re.search(EnvVarDefnFormat, line)
                    if result == None:
                        continue
                    logMessage.debug('PromptText :  ' + result[8])

                    EnvVarDefnFormat+=r'\\' + pattern_HelpText
                    result = re.search(EnvVarDefnFormat, line)
                    if result == None:
                        continue
                    logMessage.debug('HelpText :  ' + result[9])


                # Then go through remaining variables from our config to add them on 

        f_temp.write(line)
            




    f_temp.close() # This will close ( and finish writing to ) the temp file
    # Now compare the temp file and the target DSParam file, and replace the target DSParam with new temp file if there are differences. ( set the correct ownership and permissions first)
    import pwd
    uid=pwd.getpwnam(GetDSAdminName()).pw_uid
    import grp 
    gid=grp.getgrnam(GetDSAdminName()).gr_gid

    try:
        os.chown(fp.name,uid,gid)
    except PermissionError:
        logMessage.error('Unable to set ownership on ' + fp.name + '. Trying to change to chown ' + GetDSAdminName() + ':' + GetDSAdminName() + ' ' + fp.name )
        return None
    
    try:
        os.chmod(fp.name,0o755)  # change to octal 755
    except PermissionError:
        logMessage.error('Unable to set permissions on ' + fp.name + '. Trying to change to chmod 755 ' + fp.name )
        return None
    

    ReplaceOldWithNewFile(orig_file=dsparams_path, new_temp_file=fp.name)

    fp.close() # This will close and delete the temp file
    f.close
    






def GetDSAdminName():
    """
    This should be the standard way of getting the DataStage admin user name
    """
    #return 'isdsad01'
    return 'stedo'

def GetDSAdminGroup():
    """
    This should be the standard way of getting the DataStage admin users group
    """
    return 'dsadmgrp'
    #return 'stedo'


##  Main line

## The test ...  If I can't read this and understand what's going on ...then it needs re-writing
##   Any function should fit on 1 screen ( ish) ( ideally)
##   Each function should be easily describable so we know what it does

logMessage=LogMessage()
parser=HandleInputParameters()
args = parser.parse_args()

logMessage.info('logfile is :' + args.logfile)
logMessage.info('install_base is :' + args.install_base )
logMessage.info('template_dsparam is :' + args.template_dsparam )
logMessage.info('project_name is :' + args.project_name )

# Check you will have permissions to change the files as required
import os
import pwd
uid=pwd.getpwnam(GetDSAdminName()).pw_uid
import grp 
gid=grp.getgrnam(GetDSAdminGroup()).gr_gid

if not os.geteuid() == 0 and not os.getuid() == uid:
    sys.exit("\nOnly root or the datastage admin can run this script\n")

## Get the standard parameters

print('Getting standard parameters is not coded yet.')

## Get the project specific parameters
projectParamConfig='/tmp/test1' # 
standardParamConfig='/tmp/test1'
project_specific_params=GetProjectParamConfig(projectParamConfig)
standard_params=GetProjectParamConfig(standardParamConfig)
standard_params=GetProjectParamConfig_DodgyCopyForStandardParamsTest(standardParamConfig) # this is just til I get GetProjectParamConfig working correctly from config file ( its just hardcoded at the moment).

## Need to combine those ( project specific overrides standard)



# Build up new DSParams file from template, plus the standard and project specific Param config, and if compare/fix the DSParams of the target project

project_list=['dstage1']




for project in project_list:

    dsparams_path='/tmp/stetest1_DSParams1'
    CheckFixDSParams(dsparams_path=dsparams_path, templateDSParamsPath=args.template_dsparam,  standard_params=standard_params, project_specific_params=project_specific_params  )
    #ApplySettingsToTemplateDSParams(args.template_dsparam,project_specific_params)

# Create new temp DSParams files



# Copy new temp DSParams files with current, and replace if any differences

