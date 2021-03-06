#!/usr/bin/env python3

"""
STILL TO DO:
  Better log info messages
  Work out path to DSParams file ( or take that in as param?) - maybe either give project name or give path to the DSParam file
 
  Got through and tidy up. Make sure each function can be described easily.
  See if you can create unit tests ( is it appropriate for this?)
  Check what can go into some SharedFunctions module ( probably want a better name for that)

  See if any repeated logic that should be turned into functions instead
  Move some functions to the general modules  and some to the datastage modules

  Need to check best way to set oshvisable TRUE  ( can be done via dsadmin command )

This script will 
  * take in path to a param file?( format?), which contains project parameter definitions.
  * take the standard DSParams from Template, 
  * apply the standard parameter definitions to it .
  * apply the project parameter definitions to it 
  * create a new DSParams file.
  * compare the new DSParams file with the current active one for the project. If it has changed, it will back up the current one, and move the new one into place.

"""

#  For info, you might want to stick something like this in your launch.json for debugging this script.
#  "args": ["--install-base", "/iis/01", "--project-name" ,"dstage1"]
#
import sys



import re
import os 




def GetProjectParamConfig(filePath='',configType='EnvVarDefns'):
    """
    Reads a json file, and returns the json object ( list of dictionaries).

    Definitions for variables in json param file are taken from the DSParam file.  ( see comments below in code)         
""" 

#/* Contains environment variable definitions that can be set for DataStage jobs
#/* Format is: <EnvVarName>\<Category>\<JobType>\<Type>[+]\<Default>\<SetAction>\<Scope>\<PromptText>\<HelpText>
#/* Where:
#/*            <EnvVarName> is the name of the enviroment variable that will be set in OSH
#/*            <Category> is the category name where the environment variable will appear.  In format <cat1>/<subcat1>/<subcat2>/... etc
#/*            <JobType> is the job type number (0 = Server, 3 = Parallel, -1 = all)
#/*            <Type> is one of: Number, String, FilePath, DirPath, List, Boolean, UserDef
#/*                   If List, then format of Type is futher divided: ...<EnvVarName>\List/<Item1>/<ItemDisplay1>/<Item2>/<ItemDisplay2>\<Scope>...
#/*                     (ItemDisplay values must be left blank here, and added as localised strings in envvar.cls
#/*                   If Boolean, then the value the envvar is set to should be irrelevant
#/*                   If proceeded by a '+' character, then the value set here is appended to any existing value already set in the shell,
#/*                   separated by a ':' character
#/*            <Default> The default value
#/*            <SetAction> What action should be taken when setting the environment variable at job run time:
#/*                        0 = Always set if the environment variable has been overriden.
#/*                        1 = Only set the environment variable if its value is different to its default
#/*                        2 = Explicitly unset the environment variable if the value is set to the default, otherwise same as 1
#/*                        3 = Always set the environment variable
#/*                        4 = Osh Boolean. Set if true, no action if false
#/*            <Scope> is one of: Project, Design, RunTime
#/*            <PromptText> is the text displayed to prompt the user for the env var. If "" then <EnvVarName> will be used
#/*            <HelpText> is a longer description of the env var.
#/*
#/* The '/' or '\' characters can't be used as general text
#


    import json
    
    with open(filePath) as json_file:
        data = json.load(json_file)


    ## config is {} for PROJECT and AUTO-PURGE, but it might be list for ENVVars
    config={}
    for item in data:
        if configType in item:

            ## replace standard variables with their values:
            config = item[configType]
            break

    if config == {}:
        logMessage.info(configType + ' not found in ' + filePath + ' .')
      

    return config

    




class EnvVarDefn():
    def __init__(self, EnvVarName,Category,JobType,Type,Default,SetAction,Scope,PromptText,HelpText):
        
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
        definition=separator.join( (self.EnvVarDefn.EnvVarName, self.EnvVarDefn.Category, self.EnvVarDefn.JobType, self.EnvVarDefn.Type, self.EnvVarDefn.Default, self.EnvVarDefn.SetAction, self.EnvVarDefn.Scope, self.EnvVarDefn.PromptText, self.EnvVarDefn.HelpText) ) + '\n'
        return definition
    
    def print_value(self):
        #Create output line in format 
        
        # Format is: "<EnvVarName>"\1\"<Value>"
        # e.g "MySetVariable"\1\"Hello"
        separator='\\'
         
        return separator.join( ('"' + self.EnvVarValue.EnvVarName + '"', self.EnvVarValue.WhatIsThis, '"' + self.EnvVarValue.EnvVarValue + '"\n') ) 
        
        

def GetLinesFromDSParam(filePath='',sectionStartPattern=r'^\[EnvVarDefns\] *',sectionEndPattern=r'^\[.*\] *',pattern_toMatch=r'^.*$' ):
    """ 
    Get lines from DSParam file from the section defined by the section start pattern and the section end pattern.
    Only returns lines that match pattern in pattern_toMatch ( which defaults to everything).

    returns list of lines from DSParams file.

    """

    try:
        with open(filePath) as f:
    
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
                        #Skip through until you get to lines that match your pattern
                        if re.search(pattern_toMatch, line) == None:
                            continue

            
                    # This is if its EnvVarDefn that we're getting.
                    return_lines.append(line)
    
            f.close
            return(return_lines)

    except OSError:
        return None

def GetDSParamValues(filePath='',sectionName='EnvVarDefns',pattern_toMatch=r'^(\w*)\\User Defined\\.*$'):
    """
    Get values from a DSParam file and load them to a format we can process
    
    Get lines from DSParam file from the section defined by the section start pattern and the section end pattern.
    Only returns lines that match pattern in pattern_toMatch ( which defaults to everything).

    sectionName  - which section of DSParams to look at. Defaults to EnvVarDefns
    pattern_toMatch - limit results to only those that match certain pattern ( maybe this should default to all?)


    Return a dictionary of EnvVar objects


    """
    import re

    try: 
        logMessage.debug('Entered function GetDSParamValues')
        logMessage.debug('We are reading values from ' + filePath + ' .')
    except NameError:
        print('Unable to logMessage')
    #except:
    #    logMessage.debug('this is just general except.')
    #else:
    #    logMessage.debug('this is when no exception happened.')
    #finally:
    #    logMessage.debug('This is the finally section. It will aways run')
    #    logMessage.debug('This is the finally section. It will aways run')
    
    

  
    # Get the EnvVarDefinitions from template DSParams file
    sectionStartPattern=r'^\[' + sectionName + r'\] *'
    sectionEndPattern=r'^\[.*\] *'    ## or end of file    
    EnvVarDefns_lines=GetLinesFromDSParam(filePath,sectionStartPattern, sectionEndPattern, pattern_toMatch )
    # and load them int docitonary  -key env_var_name  --> EnvVarObject
    EnvVarDefns={}
    for line in EnvVarDefns_lines:
        EnvVarName, Category, JobType, Type, Default, SetAction, Scope, PromptText, HelpText  = line.rstrip().split('\\')[:9]      # User rstrip to remove the trailing newline character
        EnvVarDefns[EnvVarName] = EnvVarDefn(EnvVarName, Category, JobType, Type, Default, SetAction, Scope, PromptText, HelpText)

    # Get the EnvVarValues from source DSParams file
    sectionStartPattern=r'^\[EnvVarValues\] *'
    sectionEndPattern=r'^\[.*\] *'    ## or end of file
    #pattern_toMatch=r'^(\w*)\\User Defined\\.*$'
    EnvVarValues_lines=GetLinesFromDSParam(filePath,sectionStartPattern, sectionEndPattern )

    EnvVarValues={}
    for line in EnvVarValues_lines:
        #envVarNameQuoted, not_required, envVarValue = line.split('\\')[0]
        envVarNameQuoted = line.split('\\')[0]
        envVarValue = line.split('\\')[2]
        envVarName = envVarNameQuoted.replace('"','')
        EnvVarValues[envVarName] = EnvVarValue(envVarNameQuoted, envVarValue)


    ## So now we have all EnvVarDefns_lines and all EnvVarValues. from the source DSParams file.

    
    ## return a dictionary of EnvVar objects
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


    ## Get dictionary of PROJECT Values from source DSParams file
    sectionStartPattern=r'^\[PROJECT\] *'
    sectionEndPattern=r'^\[.*\] *'    ## or end of file
    #pattern_toMatch=r'^(\w*)\\User Defined\\.*$'
    Project_lines=GetLinesFromDSParam(filePath,sectionStartPattern, sectionEndPattern )

    ProjectValues={}
    for line in Project_lines:
        #envVarNameQuoted, not_required, envVarValue = line.split('\\')[0]
        ## PXDeployJobDirectoryTemplate=value
        envProjectVarNameQuoted = line.split('=')[0]
        envProjectVarValue = line.split('=')[1]
        envProjectVarName = envProjectVarNameQuoted.replace('"','')
        ProjectValues[envProjectVarName] = envProjectVarValue  #Could setup a class for this again, but I've just done as string for now as its just a simple Name=value

    AutoPurgeValues={}
    sectionStartPattern=r'^\[AUTO-PURGE\] *'
    sectionEndPattern=r'^\[.*\] *'    ## or end of file
    #pattern_toMatch=r'^(\w*)\\User Defined\\.*$'
    AutoPurge_lines=GetLinesFromDSParam(filePath,sectionStartPattern, sectionEndPattern )
    for line in AutoPurge_lines:
        #envVarNameQuoted, not_required, envVarValue = line.split('\\')[0]
        ## PXDeployJobDirectoryTemplate=value
        autoPurgeNameQuoted = line.split('=')[0]
        autoPurgeValue = line.split('=')[1]
        autoPurgeName = autoPurgeNameQuoted.replace('"','')
        AutoPurgeValues[autoPurgeName] = autoPurgeValue  #Could setup a class for this again, but I've just done as string for now as its just a simple Name=value



        




    return EnvVars, ProjectValues, AutoPurgeValues



    

    
    




def HandleInputParameters():

    import os
    import argparse
    # read this, and look at mutually exclusive arrgs  https://linuxconfig.org/how-to-use-argparse-to-parse-python-scripts-parameters
    
    this_script_path=(os.path.dirname(sys.argv[0]))
    
    # this_script_name=(os.path.basename(sys.argv[0]))
    #datadir=os.path.join(this_script_path,"data") # Not required
    
    
    #default_logfile=os.path.join(datadir,"default_log_file.txt")
    from general_functions import MakeALogFileName
    default_logfile=MakeALogFileName()
    

    #default_DSParams_template=os.path.abspath(os.path.join(this_script_path, 'TestFiles','DSParams.template'))
    default_DSParams_template=os.path.abspath(os.path.join(this_script_path, 'TestFiles','DSParams.template'))
    default_project_specific_params=os.path.abspath(os.path.join(this_script_path, 'TestFiles','project_specific_project_params.json'))
    default_standard_params=os.path.abspath(os.path.join(this_script_path, 'TestFiles','standard_project_params.json'))
    # Set up input options
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--install-base", type=str, dest="install_base", help="The base of the DS install. e.g /iis/test .", default='/iis/test', required=True) # Setting all to false here as it's making testing easier
    parser.add_argument("--temp-base", type=str, dest="temp_base", help="The base of the temp/scratch location.  e.g /scratch", default='/scratch')
    parser.add_argument("--project-name", action='append', type=str, dest="project_list", help="project to check, and apply changes to ", required=True)

    parser.add_argument("--logfile", type=str, dest="logfile", help="the logfile to be processed", default=default_logfile)
    
    parser.add_argument("--template-dsparam", type=str, dest="template_dsparam", help="the template DSParam file", default=default_DSParams_template,required=False)
    
    
    parser.add_argument("--project-specific-params-file", type=str, dest="project_specific_params_file", help="json file for project specific params", default=default_project_specific_params)
    parser.add_argument("--standard-params-file", type=str, dest="standard_params_file", help="json file for standard params", default=default_standard_params)
    
    
    
    return parser









def GetAmendedEnvVars(origEnvVar={},origProjectSettings={}, origAutoPurge={},  templateDSParamsPath='' , params_to_update=[],project_settings_to_update={}, autopurge_settings_to_update={}, install_base='/iis/example', temp_base='/scratch/example',project_name='dstage1'):
    """
    Update EnvVar object with definitions of variables that are in the 'params_to_update'

    Start from template DSParams...then apply stuff from origEnvVar (ie. the dictionary you've already done some updates to ) then apply stuff from params_to_update ( e.g standard or project specific config)


     params_to_update - a list of dictionaries
     project_settings_to_update - dictionary
     project_settings_to_update - dictionary
     autopurge_settings_to_update

    """
    #global logMessage
    #try:
    #    logMessage.debug('Starting function GetAmendedEnvVars')
    #except:
    #    from general_functions import LogMessage
    #    logMessage=LogMessage(args.logfile)

    # Get Full set of Env Var definitions from the DSParam file, and store as a EnvVar object
    #EnvVars, ProjectValues, AutoPurgeValues
    myTemplateEnvVar, myTemplateProjectValues, myTemplateAutoPurgeValues =GetDSParamValues(filePath=templateDSParamsPath, sectionName='EnvVarDefns', pattern_toMatch=r'^.*$') 
    #myTemplateEnvVar=GetDSParamValues(filePath=templateDSParamsPath, sectionName='EnvVarDefns', pattern_toMatch=r'^.*$') 
    def GetEnvVarToApply(origEnvVar={},params_to_update=[],myTemplateEnvVar=myTemplateEnvVar, install_base='/iis/example', temp_base='/scratch/example', project_name='dstage1'):
        

        """
        This function takes the original environment variable . 
        For each variable in the project_settings_to_update
           Check to see if exists in the template file, and get the full definition from there if required ( Need to do this since config file may not contain full definition)
           Create the updated full definition
        returns the dictionary of full definitions of the EnvVars ( definitions and values)


        """
        myOutputEnvVar_ToApply = origEnvVar


        ## Get values from project specific params, and apply them to the EnvVar object. params_to_update is a list of dictionaries, each dictionary defines a variable
        ##    
        for variable_definition in params_to_update:

            ## ignore entries that do not contain 'EnvVarName' ( ie. skip past comments or any other invalid entries)
            if 'EnvVarName'not in variable_definition:
                continue

            ## Look for the variable in the EnvVar object
            envvar_name=variable_definition['EnvVarName']
            if envvar_name in myTemplateEnvVar:
                logMessage.debug(envvar_name + ' exists in myTemplateEnvVar')
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
                    # Add code here to replace standard variables with values ( ${tempBase} and ${installBase})
                    ##  If we need to add more variables here, then it's worth doing this in a nicer way.

                    value=ReplaceVariablesInValue(variable_definition['Default'],install_base=install_base, temp_base=temp_base, project_name=project_name)
                    #mypatter=r'\${tempBase}' 
                    #result = re.sub(mypatter,temp_base, variable_definition['Default'])
                    #mypatter=r'\${installBase}' 
                    #result1 = re.sub(mypatter,install_base, result)

                    #myEnvVarValue=EnvVarValue(EnvVarName=envvar_name, EnvVarValue=variable_definition['Default'] )
                    myEnvVarValue=EnvVarValue(EnvVarName=envvar_name, EnvVarValue=value )
                    myOutputEnvVar_ToApply[envvar_name].EnvVarValue=myEnvVarValue
                    
                    

            else:
                ## This variable does not already exist, so will be created as user defined
                ## e.g. MyUnsetVariable\User Defined\-1\String\\0\Project\This is my unset variable - it has no value set.\
                logMessage.debug(envvar_name + ' does not exist in myEnvVar')

                ## Create new User Defined Variable based on contents of variable_definition

                if 'Default' in variable_definition:
                    value=ReplaceVariablesInValue(variable_definition['Default'],install_base=install_base, temp_base=temp_base, project_name=project_name)
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
                                            PromptText=varPromptText, HelpText='')

                # Now update  myEnvVar with the value and definition                    
                myOutputEnvVar_ToApply[envvar_name]=EnvVar(EnvVarName=envvar_name, EnvVarDefn= myEnvVarDefn, EnvVarValue=myEnvVarValue)
        return myOutputEnvVar_ToApply
    
    def GetProjectSettingsToApply(origProjectSettings={},project_settings_to_update={},myTemplateProjectValues=myTemplateProjectValues):
        """
        This can be simpler than the env var ones  (no need to check template file to find existing definitions , as this is simpler and will be fully defined in the config file)
        For each variable in the project_settings_to_update
           Check to see if exists in the template file
        return a dictionary of project settings with values.
        """
        myOutputProjectSettingsToApply=origProjectSettings
        for setting, value in project_settings_to_update.items():
            logMessage.debug('Processing ' + setting + ' ' + str(value))
            myOutputProjectSettingsToApply[setting]=value

        
        return myOutputProjectSettingsToApply
    
    def GetAutoPurgeSettingsToApply(origAutoPurge={},autopurge_settings_to_update={},myTemplateAutoPurgeValues=myTemplateAutoPurgeValues):

        myOutput=origAutoPurge
        for setting, value in autopurge_settings_to_update.items():
            logMessage.debug('Processing ' + setting + ' ' + str(value))
            myOutput[setting]=value
        
        return myOutput
        
    myOutputEnvVar_ToApply=GetEnvVarToApply(origEnvVar=origEnvVar,params_to_update=params_to_update,myTemplateEnvVar=myTemplateEnvVar, install_base=install_base, temp_base=temp_base, project_name=project_name)

            ## Need to add some code here to do other sections
    myOutputProjectSetting_ToApply=GetProjectSettingsToApply(origProjectSettings=origProjectSettings,project_settings_to_update=project_settings_to_update,myTemplateProjectValues=myTemplateProjectValues)
    myOutputAutoPurge_ToApply=GetAutoPurgeSettingsToApply(origAutoPurge=origAutoPurge,autopurge_settings_to_update=autopurge_settings_to_update,myTemplateAutoPurgeValues=myTemplateAutoPurgeValues)
                    
    return myOutputEnvVar_ToApply,myOutputProjectSetting_ToApply,myOutputAutoPurge_ToApply




def CheckFixDSParams_OutputDebugInfoForUnmatchedLineFormat(line):
        """
        This is just to help understand what patterns are being matched when line does not match format we expect.
        Should not really be needed.
        """

        ## This bits for EnvVarDefn
        #pattern_separator=r'\\'
        pattern_EnvVarName=r'(\w*)'
        pattern_Category=r'(\w*[/\w ]*)'
        pattern_JobType=r'([-]*\d)'
        pattern_Type=r'(\w*[/\w+]*)'
        pattern_Default=r'(.*?)'
        pattern_SetAction=r'(\d)'
        pattern_Scope=r'(\w*)'
        pattern_PromptText=r'(.*?)'
        pattern_HelpText=r'(.*)$'

        EnvVarDefnFormat=r'^' + pattern_EnvVarName
        result = re.search(EnvVarDefnFormat, line)
        logMessage.debug('EnvVarName :  ' + result[1])
        
        EnvVarDefnFormat+=r'\\' + pattern_Category
        result = re.search(EnvVarDefnFormat, line)
        if result == None:
            return
        logMessage.debug('Category :  ' + result[2])

        EnvVarDefnFormat+=r'\\' + pattern_JobType
        result = re.search(EnvVarDefnFormat, line)
        if result == None:
            return
        logMessage.debug('JobType :  ' + result[3])

        EnvVarDefnFormat+=r'\\' + pattern_Type
        result = re.search(EnvVarDefnFormat, line)
        if result == None:
            return
        logMessage.debug('Type :  ' + result[4])

        EnvVarDefnFormat+=r'\\' + pattern_Default
        result = re.search(EnvVarDefnFormat, line)
        if result == None:
            return
        logMessage.debug('Default :  ' + result[5])

        EnvVarDefnFormat+=r'\\' + pattern_SetAction
        result = re.search(EnvVarDefnFormat, line)
        if result == None:
            return
        logMessage.debug('SetAction :  ' + result[6])

        EnvVarDefnFormat+=r'\\' + pattern_Scope
        result = re.search(EnvVarDefnFormat, line)
        if result == None:
            return
        logMessage.debug('Scope :  ' + result[7])

        EnvVarDefnFormat+=r'\\' + pattern_PromptText
        result = re.search(EnvVarDefnFormat, line)
        if result == None:
            return
        logMessage.debug('PromptText :  ' + result[8])

        EnvVarDefnFormat+=r'\\' + pattern_HelpText
        result = re.search(EnvVarDefnFormat, line)
        if result == None:
            return
        logMessage.debug('HelpText :  ' + result[9])


def CheckFixDSParams_CreateSectionPattern(section='EnvVarDefns'):
    """
    Called from   CheckFixDSParams -  to return a pattern for the section
    """

    if section == 'EnvVarDefns':
        ## Build up the pattern for matching the EnvVarDefn format
        ## This bits for EnvVarDefn
        pattern_separator=r'\\'
        pattern_EnvVarName=r'(\w*)'
        pattern_Category=r'(\w*[/\w ]*)'
        pattern_JobType=r'([-]*\d)'
        pattern_Type=r'(\w*[/\w+]*)'
        pattern_Default=r'(.*?)'
        pattern_SetAction=r'(\d)'
        pattern_Scope=r'(\w*)'
        pattern_PromptText=r'(.*?)'
        pattern_HelpText=r'(.*)$'

        
        EnvVarDefnFormat=r'^' 
        EnvVarDefnFormat+=pattern_EnvVarName
        EnvVarDefnFormat+=pattern_separator
        EnvVarDefnFormat+=pattern_Category
        EnvVarDefnFormat+=pattern_separator
        EnvVarDefnFormat+=pattern_JobType
        EnvVarDefnFormat+=pattern_separator
        EnvVarDefnFormat+=pattern_Type
        EnvVarDefnFormat+=pattern_separator
        EnvVarDefnFormat+=pattern_Default
        EnvVarDefnFormat+=pattern_separator
        EnvVarDefnFormat+=pattern_SetAction
        EnvVarDefnFormat+=pattern_separator
        EnvVarDefnFormat+=pattern_Scope
        EnvVarDefnFormat+=pattern_separator
        EnvVarDefnFormat+=pattern_PromptText
        EnvVarDefnFormat+=pattern_separator
        EnvVarDefnFormat+=pattern_HelpText
        return EnvVarDefnFormat
    elif section == 'EnvVarValue':
        ## Build up the pattern for matching the EnvVarValue format
        EnvVarValueFormat=r'^"(\w*)"\\(1)\\"(.*)"' 
        return EnvVarValueFormat
    
    elif section == 'PROJECT':
        ProjectSettingFormat=r'^([\w\d]*)=([\w\d]*)' 
        return ProjectSettingFormat
    
    elif section == 'AUTO-PURGE':
        SettingFormat=r'^([\w\d]*)=([\w\d]*)' 
        return SettingFormat


def ReplaceVariablesInValue(value='', install_base='/iis/example', temp_base='/scratch/example', project_name='dstage1'):

    # Add code here to replace standard variables with values ( ${tempBase} and ${installBase})
    ##  If we need to add more variables here, then it's worth doing this in a nicer way.
    mypatter=r'\${tempBase}' 
    result = re.sub(mypatter,temp_base, value)
    mypatter=r'\${installBase}' 
    result1 = re.sub(mypatter,install_base, result)
    mypatter=r'\${projectName}' 
    result2 = re.sub(mypatter,project_name, result1)

    return result2

def CheckFixDSParams(version_xml='/iis/test/InformationServer/Version.xml', dsparams_path='/tmp/stetest1', templateDSParamsPath='', standard_params=[], standard_project_settings={}, standard_autopurge_settings={}, project_specific_params=[] ,project_specific_project_settings={}, project_specific_autopurge_settings={},install_base='/iis/example', temp_base='/scratch/example', project_name='dstage1'):

    #dsparams_path=dsparams_path, templateDSParamsPath=args.template_dsparam,  standard_params=standard_params, standard_project_settings=standard_project_settings, standard_autopurge_settings=standard_autopurge_settings, project_specific_params=project_specific_params ,project_specific_project_settings=project_specific_project_settings, project_specific_autopurge_settings=project_specific_autopurge_settings 
    """
    This function will take in a path to a template DSParams file, and a list of dictionaries for the project specific parameter settings.
    TemplateDSParamsPath could be pointing to the Templates folder, or some other DSParams file  ( e.g if we're building one in multiple stages ..starting from template..apply standard...create new temp.. use new temp as template, apply project specific changes)

    It combines them to produce a new file ( or should it be a new object in the program???. Lets decide in a bit )    

    If it creates output file.. then should the path to that be a param too?
    """




    def SectionChangeLogic(previousSection='', amendedEnvVars={}, f_temp='', install_base='/iis/example', temp_base='/scratch/example/', project_name=project_name):
        """
        This logic need to be called in the loop, and when the loop finishes.
        Need to check...is f_temp here referencing the same object as f_temp outside this function?  ( That's what I want)

        Should add in all variables as parms..get rid of global/shared

        """
        # If section change, and previous section was EnvVarDefns, need to make sure any EnvVarDefns which have not been processed from amendedEnvVars are written out.
        if previousSection == 'EnvVarDefns':
            

            # using items() to get all items  
            # lambda function is passed in key to perform sort by key  
            sorted_amendedEnvVars = {key: val for key, val in sorted(amendedEnvVars.items(), key = lambda ele: ele[0])} 
            #for env_var_name, env_var_object in amendedEnvVars.items():
            for env_var_name, env_var_object in sorted_amendedEnvVars.items():
                logMessage.debug('processing ' + env_var_name )
                if env_var_object.EnvVarDefn != None:
                    logMessage.debug('processing definition for  ' + env_var_name )
                    # Write the definition of the new variable out
                    new_line=env_var_object.print_definition()
                    f_temp.write(new_line)
                    ## Need to add in bit for adding these ( user defined ) variable definitions
                    ### Then need to add code for setting the values in the values section.
        
        if previousSection == 'EnvVarValues':
            sorted_amendedEnvVars = {key: val for key, val in sorted(amendedEnvVars.items(), key = lambda ele: ele[0])} 
            for env_var_name, env_var_object in sorted_amendedEnvVars.items():
                logMessage.debug('processing ' + env_var_name )
                if env_var_object.EnvVarValue != None:
                    logMessage.debug('processing value  for  ' + env_var_name )
                    # Write the values of the new variable out
                    new_value=env_var_object.print_value()


                    value = ReplaceVariablesInValue(new_value,install_base=install_base, temp_base=temp_base,project_name=project_name)

                    ## Add code here to replace standard variables with values ( ${tempBase} and ${installBase})
                    ###  If we need to add more variables here, then it's worth doing this in a nicer way.
                    #mypatter=r'\${tempBase}' 
                    #result = re.sub(mypatter,temp_base, new_value)
                    #mypatter=r'\${installBase}' 
                    #result1 = re.sub(mypatter,install_base, result)





                    f_temp.write(value)
        
        if previousSection == 'AUTO-PURGE':
            #format=AutoPurgeFormat
            amendedDictionary=amendedAutoPurge ### This needs to just be an alias to the real dictionary, as we want to pop items out of it.
            # PurgeEnabled needs to be the first line written for AUTO-PURGE, so process that one now.
            # In fact, there's only 3 fields, order matters, and we need defaults if they're not supplied, so put them all here.

            # Validate what's in the AUTO-PURGE settings

            if 'PurgeEnabled' not in amendedDictionary:
                amendedDictionary['PurgeEnabled'] = 0
            if 'DaysOld' not in amendedDictionary:
                amendedDictionary['DaysOld'] = 0
            if 'PrevRuns' not in amendedDictionary:
                amendedDictionary['PrevRuns'] = 0

            if amendedDictionary['PurgeEnabled'] not in [0,1]:
                logMessage.warning('PurgeEnabled is must be to 0 or 1. Config file contains : ' + str(amendedDictionary['PurgeEnabled']) + '. Defaulting to 1')
                amendedDictionary['PurgeEnabled'] = 1 


            if amendedDictionary['PurgeEnabled'] == 0:
                if 'DaysOld' in amendedDictionary:
                    if amendedDictionary['DaysOld'] != 0 :
                        logMessage.warning('PurgeEnabled is set to 0. DaysOld must be 0')
                        amendedDictionary['DaysOld'] = 0
                if 'PrevRuns' in amendedDictionary:
                    if amendedDictionary['PrevRuns'] != 0 :
                        logMessage.warning('PurgeEnabled is set to 0. PrevRuns must be 0')
                        amendedDictionary['PrevRuns'] = 0

            # If enabled, then either DaysOld or PrevRuns must be set
            if amendedDictionary['PurgeEnabled'] == 1:
                if amendedDictionary['DaysOld'] == 0 and amendedDictionary['PrevRuns'] == 0:
                    logMessage.warning('PurgeEnabled is set to 1. Either DaysOld or PrevRuns must be greater than 0. Setting DaysOld to 1')
                    amendedDictionary['DaysOld'] = 1
                    

            
            # Write out the values
            if 'PurgeEnabled' in amendedDictionary:
                amended_value=amendedDictionary.pop('PurgeEnabled')
            else:
                amended_value=0

            new_value='PurgeEnabled' + '=' + str(amended_value) + '\n'
            f_temp.write(new_value)
                
            if 'DaysOld' in amendedDictionary:
                amended_value=amendedDictionary.pop('DaysOld')
            else:
                amended_value=0

            new_value='DaysOld' + '=' + str(amended_value) + '\n'
            f_temp.write(new_value)  

            if 'PrevRuns' in amendedDictionary:
                amended_value=amendedDictionary.pop('PrevRuns')
            else:
                amended_value=0

            new_value='PrevRuns' + '=' + str(amended_value) + '\n'
            f_temp.write(new_value)  

        if previousSection == 'PROJECT':
            amendedDictionary=amendedProjectSettings ### This needs to just be an alias to the real dictionary, as we want to pop items out of it.
            sorted_amendedDictionary = {key: val for key, val in sorted(amendedDictionary.items(), key = lambda ele: ele[0])}
            for setting, value in sorted_amendedDictionary.items():
                logMessage.debug('processing ' + setting )
                
                amended_value = ReplaceVariablesInValue(str(value),install_base=install_base, temp_base=temp_base,project_name=project_name)
                new_value=setting + '=' + amended_value + '\n'
                f_temp.write(new_value) 


    #Main code for this function (CheckFixDSParams) 
    
    ## Get dictionary of all variables to amend. Start with empty, the apply the standard changes, then apply the project specific changes
    amendedEnvVars,amendedProjectSettings, amendedAutoPurge =GetAmendedEnvVars(origEnvVar={},            origProjectSettings={},                    origAutoPurge={},               templateDSParamsPath=templateDSParamsPath , params_to_update=standard_params, project_settings_to_update=standard_project_settings, autopurge_settings_to_update=standard_autopurge_settings, install_base=install_base, temp_base=temp_base, project_name=project_name)
    amendedEnvVars,amendedProjectSettings, amendedAutoPurge =GetAmendedEnvVars(origEnvVar=amendedEnvVars,origProjectSettings=amendedProjectSettings,origAutoPurge=amendedAutoPurge, templateDSParamsPath=templateDSParamsPath , params_to_update=project_specific_params, project_settings_to_update=project_specific_project_settings, autopurge_settings_to_update=project_specific_autopurge_settings,install_base=install_base, temp_base=temp_base,project_name=project_name)


    
      
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


    # Open the template DSParams file
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
        logMessage.error('Unable to open the temp file :' + fp.name )
        return None
 
    ##  Read each line from template file, and do processing depending on what section of the file we're in.
    currentSection=None
    env_var_values_found=False ## This section does not always exist in the DSParams file. We need to create it if we don't find it.
    auto_purge_found=False

    ## Define the record formats we will use
    EnvVarValueFormat = CheckFixDSParams_CreateSectionPattern(section='EnvVarValue')                            
    EnvVarDefnFormat = CheckFixDSParams_CreateSectionPattern(section='EnvVarDefns')              
    ProjectSettingFormat = CheckFixDSParams_CreateSectionPattern(section='PROJECT')              
    AutoPurgeFormat = CheckFixDSParams_CreateSectionPattern(section='AUTO-PURGE')              

    for line in f:
                
        ## Work out what section we're in.
        sectionStartPattern=r'^\[([\w-]*)\]'
        result = re.search(sectionStartPattern,line)
        if result != None:
            
            previousSection=currentSection # When Section changes, save off the previousSection name. 
            currentSection=result[1]
            if currentSection == 'EnvVarValues':
                env_var_values_found = True
            if currentSection == 'AUTO-PURGE':
                auto_purge_found = True

            SectionChangeLogic(previousSection=previousSection, amendedEnvVars=amendedEnvVars, f_temp=f_temp,install_base=install_base, temp_base=temp_base,project_name=project_name)

        else:
            if currentSection == 'EnvVarValues':
                ## Check it matches the format we expect ( otherwise just allow line to be written out unchanged).
                #EnvVarValueFormat = CheckFixDSParams_CreateSectionPattern(section='EnvVarValue')                            
                result = re.search(EnvVarValueFormat, line)
                if result != None:
                    envvar_name=result[1]
                    # Check if the variable is included in our variables that are to be amended.
                    if envvar_name in amendedEnvVars:
                        line=amendedEnvVars[envvar_name].print_value()
                        amendedEnvVars[envvar_name].EnvVarValue = None
                else:
                    logMessage.warning("We're in EnvVarValues section, but line does not match the expected format. Line is :" + line)
              


            if currentSection == 'EnvVarDefns':

                # Check it matches our expected format
                #EnvVarDefnFormat = CheckFixDSParams_CreateSectionPattern(section='EnvVarDefns')              
                result = re.search(EnvVarDefnFormat, line)
                if result != None:
                    logMessage.debug('Processing ' + result[1])

                    #First, does the envvar exist in either the 'standard' or 'project specific' ( ie. does it need changing)
                    # Check if it's in amendedEnvVars
                    envvar_name=result[1]
                    
                    # See if this env var defn is amended by our config
                    # Could change this to only update if user defined - as they are only ones that should be able to change definition.  Should already be handled though, so doesn't matter really.
                    if envvar_name in amendedEnvVars:
                        line=amendedEnvVars[envvar_name].print_definition()
                        # Remove the definition from amendedEnvVars once you've processed it ( so we know not to add it to end of the section in the output dsparms file). ( but leave the value - we need to set that later)
                        amendedEnvVars[envvar_name].EnvVarDefn = None                       

                else:
                    logMessage.info('Line does not match expected format for a variable' + line)
                    # Would be nice to move this debug code to some other function, to keep this code a bit shorter. 
                    CheckFixDSParams_OutputDebugInfoForUnmatchedLineFormat(line)

            if currentSection == 'PROJECT' or currentSection == 'AUTO-PURGE' :
                
                ## Check it matches expected format
                if currentSection == 'PROJECT' :
                    format=ProjectSettingFormat
                    amendedDictionary=amendedProjectSettings ### This needs to just be an alias to the real dictionary, as we want to pop items out of it.

                ## Don't process the AUTO-PURGE lines here, do them all as once in the SectionChange Logic. 
                #elif currentSection == 'AUTO-PURGE':
                #    format=AutoPurgeFormat
                #    amendedDictionary=amendedAutoPurge ### This needs to just be an alias to the real dictionary, as we want to pop items out of it.
                
                    result = re.search(format, line)
                    if result != None:
                        setting=result[1]
                        # not required.value=result[2]
                        # Check if the variable is included in our variables that are to be amended.
                        if setting in amendedDictionary:
                            line=setting + '=' + str(amendedDictionary[setting]) + '\n'
                            #amendedProjectSettings[setting] = None # remove it , so we know not to add it on at the end.
                            amendedDictionary.pop(setting)  #remove it , so we know not to add it on at the end.
                    else:
                        logMessage.warning("We're in PROJECT section, but line does not match the expected format. Line is :" + line)
                
                else:
                    logMessage.debug("We're in AUTO-PURGE section, but no need to do anything in this function")
                    # Continue to process next line, without writing this one.. (all AUTO-PURGE writes will be done in the Section Change logic, so that we can do the validation on the section as a whole.)
                    continue
                

        
                    

        f_temp.write(line)
            



    # At end of file ( ie. the end of the EnvVarValues section), we need to add on any new values
    #  This logic needs to be called from inside loop ( on section change)  and here too
    previousSection=currentSection # When Section changes, save off the previousSection name. 
    currentSection='End of file'
    SectionChangeLogic(previousSection=previousSection, amendedEnvVars=amendedEnvVars, f_temp=f_temp, install_base=install_base, temp_base=temp_base,project_name=project_name)

    ## If EnvVarValues didnt exist at start , we need to add it on.
    if env_var_values_found == False:
        section_change_line='[EnvVarValues]\n'
        f_temp.write(section_change_line)
        SectionChangeLogic(previousSection='EnvVarValues', amendedEnvVars=amendedEnvVars, f_temp=f_temp,install_base=install_base, temp_base=temp_base,project_name=project_name)

    ## If AUTO-PURGE didnt exist at start , we need to add it on.
    if auto_purge_found == False:
        section_change_line='[AUTO-PURGE]\n'
        f_temp.write(section_change_line)
        SectionChangeLogic(previousSection='AUTO-PURGE', amendedEnvVars=amendedEnvVars, f_temp=f_temp,install_base=install_base, temp_base=temp_base,project_name=project_name)
    
    



    f_temp.close() # This will close ( and finish writing to ) the temp file

    # Now compare the temp file and the target DSParam file, and replace the target DSParam with new temp file if there are differences. ( set the correct ownership and permissions first)
    import pwd
    import grp 

    #version_xml=os.path.join(args.install_base,'InformationServer', 'Version.xml')
    #dshome=os.path.join(args.install_base,'InformationServer','Server', 'DSEngine')

    from datastage_functions import GetDSAdminName,GetDSAdminGroup
    try: 
        adminName=GetDSAdminName(version_xml)
        adminGroup=GetDSAdminGroup(version_xml)
        
        uid=pwd.getpwnam(adminName).pw_uid  
        gid=grp.getgrnam(adminGroup).gr_gid
    except KeyError:
        logMessage.error('Unable to find uid or gid for ' + adminName )
        return None

    try:
        os.chown(fp.name,uid,gid)
    except PermissionError:
        logMessage.error('Unable to set ownership on ' + fp.name + '. Trying to change to chown ' + adminName + ':' + adminGroup() + ' ' + fp.name )
        return None
    
    try:
        os.chmod(fp.name,0o755)  # change to octal 755
    except PermissionError:
        logMessage.error('Unable to set permissions on ' + fp.name + '. Trying to change to chmod 755 ' + fp.name )
        return None
    
    from general_functions import ReplaceOldWithNewFile
    ReplaceOldWithNewFile(orig_file=dsparams_path, new_temp_file=fp.name)

    try: 
        fp.close() # This will close and delete the temp file
    except:
        ## file has been removed already by move done in ReplaceOldwithNewFile
        pass 
    f.close
    







    #return 'stedo'





    

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
    logMessage.setLogFile(args.logfile)

    
    #Check input params
    errorfound=False
    if not os.path.exists(args.template_dsparam):
        errorfound=True
        logMessage.info('Template DSParams file not found at: ' + args.template_dsparam)
    
    if not os.path.exists(args.standard_params_file):
        errorfound=True
        logMessage.info('Standard DSParams file not found at: ' + args.standard_params_file)
    
    if not os.path.exists(args.project_specific_params_file):
        errorfound=True
        logMessage.info('Project specific DSParams file not found at: ' + args.project_specific_params_file)

    if not os.path.exists(args.install_base):
        
        logMessage.warning('Install base does not exist at: ' + args.install_base)
    
    if not os.path.exists(args.temp_base):
        
        logMessage.warning('Temp base does not exist at: ' + args.temp_base)

    if errorfound:
        sys.exit("\nInput parameter failed validation. See previous messages.\n")


    
    


    logMessage.info('logfile is :' + args.logfile)
    logMessage.info('install_base is :' + args.install_base )
    logMessage.info('temp_base is :' + args.temp_base )
    logMessage.info('template_dsparam is :' + args.template_dsparam) 
    logMessage.info('project_list is :' + str(args.project_list) )
    logMessage.info('standard params file is : ' + args.standard_params_file)
    logMessage.info('project specific params file is : ' + args.project_specific_params_file)
        


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

    # Get the standard parameters from the config file 
    standard_params=GetProjectParamConfig(args.standard_params_file,'EnvVarDefns')
    standard_project_settings=GetProjectParamConfig(args.standard_params_file,'PROJECT')
    standard_autopurge_settings=GetProjectParamConfig(args.standard_params_file,'AUTO-PURGE')


    # Get the project specific parameters from the config file
    project_specific_params=GetProjectParamConfig(args.project_specific_params_file,'EnvVarDefns')
    project_specific_project_settings=GetProjectParamConfig(args.project_specific_params_file,'PROJECT')
    project_specific_autopurge_settings=GetProjectParamConfig(args.project_specific_params_file,'AUTO-PURGE')



    # Build up new DSParams file from template, plus the standard and project specific Param config, and if compare/fix the DSParams of the target project   
    project_list=args.project_list


    # not used anywhere yet  dsenvfile=os.path.join(dshome,'dsenv')
    

    
    
    import os 
    dsadm_user=GetDSAdminName(version_xml=version_xml)
    counter=1
    
    for project in project_list:

        logMessage.info( 'Processing project ' + str(counter) + ' of ' + str(len(project_list)) + '. Project Name: ' + project )
     
        
        from datastage_functions import GetProjectPath
        project_path=GetProjectPath(project_name=project,dsadm_user=dsadm_user, dshome=dshome)
        if project_path is None:
            logMessage.warning('Skipping ' + project + ' . Unable to find project path.')
            continue


        dsparams_path=os.path.join(project_path,'DSParams')

        if os.path.exists(dsparams_path):
            logMessage.info('Processing ' + dsparams_path)
        else:
            logMessage.warning('Unable to find DSParams file ' + dsparams_path + '. A new file will be created.') 
        
        ## Maybe I should have one object for standard settings, and one for project specific settings instead here. 
        CheckFixDSParams(version_xml=version_xml,  dsparams_path=dsparams_path, templateDSParamsPath=args.template_dsparam,  standard_params=standard_params, standard_project_settings=standard_project_settings, standard_autopurge_settings=standard_autopurge_settings, project_specific_params=project_specific_params ,project_specific_project_settings=project_specific_project_settings, project_specific_autopurge_settings=project_specific_autopurge_settings, install_base=args.install_base, temp_base=args.temp_base, project_name=project )

        counter+=1
        

        
## if logMessage does not exist, create it with default logfile path
## I've put these here in an attempt to make logMessage available in functions even if we call them directly without calling the full script.
##  ( will be useful for unit testing the functions)
try: 
    logMessage.debug('Entered SetProjectParams.py')
except NameError:
    from general_functions import LogMessage
    logMessage=LogMessage()
    logMessage.debug('Entered SetProjectParams.py')
    #setLogFile(args.logfile) 

if __name__=="__main__":
    main()
