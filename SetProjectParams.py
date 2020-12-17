#!/usr/bin/env python3

"""
STILL TO DO:
  Better log info messages
  Work out path to DSParams file ( or take that in as param?) - maybe either give project name or give path to the DSParam file
 
  Got through and tidy up. Make sure each function can be described easily.
  See if you can create unit tests ( is it appropriate for this?)
  Check what can go into some SharedFunctions module ( probably want a better name for that)

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




def GetProjectParamConfig(filePath=''):
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

    return data

    




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
                #Skip through until you get to lines that match your pattern
                if re.search(pattern_toMatch, line) == None:
                    continue

            
            # This is if its EnvVarDefn that we're getting.
            return_lines.append(line)
    
    f.close
    return(return_lines)

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


        




    return EnvVars



    

    
    




def HandleInputParameters():

    import os
    import argparse
    # read this, and look at mutually exclusive arrgs  https://linuxconfig.org/how-to-use-argparse-to-parse-python-scripts-parameters
    
    this_script_path=(os.path.dirname(sys.argv[0]))
    
    # this_script_name=(os.path.basename(sys.argv[0]))
    datadir=os.path.join(this_script_path,"data") # Ah!  you don't want the '/' in your args - makes sense!
    
    
    default_logfile=os.path.join(datadir,"default_log_file.txt")
    

    #default_DSParams_template=os.path.abspath(os.path.join(this_script_path, 'TestFiles','DSParams.template'))
    default_DSParams_template=os.path.abspath(os.path.join(this_script_path, 'TestFiles','DSParams.template'))
    default_project_specific_params=os.path.abspath(os.path.join(this_script_path, 'TestFiles','project_specific_project_params.json'))
    default_standard_params=os.path.abspath(os.path.join(this_script_path, 'TestFiles','standard_project_params.json'))
    # Set up input options
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--install-base", type=str, dest="install_base", help="The base of the DS install. e.g /iis/01 .", default='/iis/01', required=True) # Setting all to false here as it's making testing easier
    parser.add_argument("--project-name", action='append', type=str, dest="project_list", help="project to check, and apply changes to ", required=True)

    parser.add_argument("--logfile", type=str, dest="logfile", help="the logfile to be processed", default=default_logfile)
    
    parser.add_argument("--template-dsparam", type=str, dest="template_dsparam", help="the template DSParam file", default=default_DSParams_template,required=False)
    
    
    parser.add_argument("--project-specific-params-file", type=str, dest="project_specific_params_file", help="json file for project specific params", default=default_project_specific_params)
    parser.add_argument("--standard-params-file", type=str, dest="standard_params_file", help="json file for standard params", default=default_standard_params)
    
    
    return parser





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
            backupfile=orig_file + time.strftime('%Y%M%d_%H%M%S', t)
            shutil.copyfile(orig_file,backupfile)
        
    else:
        logMessage.info(orig_file + ' - does not exist. Creating new file.')
    
    ## Only got to here if does not match  (ie new or different)
    logMessage.info(orig_file + ' - has been amended. ( to match ' + new_temp_file + ' )')
    #shutil.copyfile(new_temp_file, orig_file)
    shutil.move(new_temp_file, orig_file)
    
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

        ## ignore entries that do not contain 'EnvVarName' ( ie. skip past comments or any other invalid entries)
        if 'EnvVarName'not in variable_definition:
            continue

        ## Look for the variable in the EnvVar object
        envvar_name=variable_definition['EnvVarName']
        if envvar_name in myTemplateEnvVar:
            logMessage.info(envvar_name + ' exists in myTemplateEnvVar')
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
            logMessage.debug(envvar_name + ' does not exist in myEnvVar')

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
    amendedEnvVars=GetAmendedEnvVars(origEnvVar={}, templateDSParamsPath=templateDSParamsPath , params_to_update=standard_params)
    amendedEnvVars=GetAmendedEnvVars(origEnvVar=amendedEnvVars, templateDSParamsPath=templateDSParamsPath , params_to_update=project_specific_params)


    
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

    ## Build up the pattern for matching the EnvVarValue format
    ## "MySetVariable"\1\"Hello"
    EnvVarValueFormat=r'^"(\w*)"\\(1)\\"(.*)"' 
    
    def OutputDebugInfoForUnmatchedLineFormat():
        """
        This is just to help understand what patterns are being matched when line does not match format we expect.
        Should not really be needed.
        """
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


    def SectionChangeLogic(previousSection='', amendedEnvVars={}, f_temp=''):
        """
        This logic need to be called in the loop, and when the loop finishes.
        Need to check...is f_temp here referencing the same object as f_temp outside this functino?  ( That's what I want)

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
                    f_temp.write(new_value)
                  
            

    env_var_values_found=False ## This section does not always exist in the DSParams file. We need to create it if we don't find it.
    for line in f:
                
        ## Work out what section we're in.
        sectionStartPattern=r'^\[([\w-]*)\]'
        result = re.search(sectionStartPattern,line)
        if result != None:
            
            previousSection=currentSection # When Section changes, save off the previousSection name. 
            currentSection=result[1]
            if currentSection == 'EnvVarValues':
                env_var_values_found=True

            SectionChangeLogic(previousSection=previousSection, amendedEnvVars=amendedEnvVars, f_temp=f_temp)

        else:
            if currentSection == 'EnvVarValues':
                ## Check it matches the format we expect ( otherwise just allow line to be written out unchanged).
                           
                result = re.search(EnvVarValueFormat, line)

                if result != None:
                    envvar_name=result[1]
                    # Check if the variable is included in our variables that are to be amended.
                    if envvar_name in amendedEnvVars:
                        line=amendedEnvVars[envvar_name].print_value()
                        amendedEnvVars[envvar_name].EnvVarValue = None


                


            if currentSection == 'EnvVarDefns':

                # Check it matches our expected format              
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
                    OutputDebugInfoForUnmatchedLineFormat()
                    

        f_temp.write(line)
            



    # At end of file ( ie. the end of the EnvVarValues section), we need to add on any new values
    #  This logic needs to be called from inside loop ( on section change)  and here too
    previousSection=currentSection # When Section changes, save off the previousSection name. 
    currentSection='End of file'
    SectionChangeLogic(previousSection=previousSection, amendedEnvVars=amendedEnvVars, f_temp=f_temp)

    ## If EnvVarValues didnt exist at start , we need to add it on.
    if env_var_values_found == False:
        section_change_line='[EnvVarValues]\n'
        f_temp.write(section_change_line)
        SectionChangeLogic(previousSection='EnvVarValues', amendedEnvVars=amendedEnvVars, f_temp=f_temp)


    f_temp.close() # This will close ( and finish writing to ) the temp file

    # Now compare the temp file and the target DSParam file, and replace the target DSParam with new temp file if there are differences. ( set the correct ownership and permissions first)
    import pwd
    import grp 

    try: 
        adminName=GetDSAdminName()
        adminGroup=GetDSAdminGroup()
        
        uid=pwd.getpwnam(adminName).pw_uid  
        gid=grp.getgrnam(adminGroup).gr_gid
    except KeyError:
        logMessage.error('Unable to find uid or gid for ' + adminName )
        return None

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

    try: 
        fp.close() # This will close and delete the temp file
    except:
        ## file has been removed already by move done in ReplaceOldwithNewFile
        pass 
    f.close
    






def GetDSAdminName(version_xml='/iis/01/InformationServer/Version.xml'):
    """
    This should be the standard way of getting the DataStage admin user name
    """

    from datastage_functions import GetValueFromVersionXML

    #version_xml='/iis/01/InformationServer/Version.xml'
    variable_name='datastage.user.name'
    value=GetValueFromVersionXML(version_xml,variable_name )


    


    return value
    #return 'stedo'

def GetDSAdminGroup(version_xml='/iis/01/InformationServer/Version.xml'):
    """
    This should be the standard way of getting the DataStage admin users group
    """

    from datastage_functions import GetValueFromVersionXML

    
    variable_name='ds.admin.gid'
    value=GetValueFromVersionXML(version_xml,variable_name )
    return value

def GetProjectPath(project_name='dstage1',dsadm_user='dsadm', dshome='/iis/01/InformationServer/Server/DSEngine'):
    """
    This needs recoding to work this out correctly.
    Using uvsh, of other DS provided methods requires DataStage to be up. That's ok for me.
    """
    import os
    import subprocess
    
    import re

    #project_base_path='/iis/01/InformationServer/Server/Projects/'
    #project_path=os.path.join(project_base_path, project_name )

    #dsenvfile='/iis/01/InformationServer/Server/DSEngine/dsenv'
    #project_name='dstage1' - input param
    #dsadm_user='dsadm'
    
    dsenv=os.path.join(dshome,'dsenv')
    dsjobcommand=os.path.join(dshome,'bin/dsjob')
    command='source ' + dsenv + ' ; ' +  dsjobcommand + ' -projectinfo ' + project_name
    sudo_command='sudo -u ' + dsadm_user + ' -s sh -c "' + command + ' | grep \'^Project Path\'"'
    
    #result = subprocess.run([sudo_command] , env=my_env, capture_output=True, shell=True)
    result = subprocess.run([sudo_command] , capture_output=True, shell=True, encoding="UTF-8")



    if result.returncode != 0:
        return None
    else:
        pattern=r'^Project Path\t: (.*)'
        projectpath = re.search(pattern,result.stdout)[1]
        return(projectpath)


    

def main(arrgv=None):
    ##  Main line

    ## This script has been coded with 3.7.
    import sys
    if sys.version_info < (3,7):
        sys.exit("\nThis script requires python 3.7 or higher.\n")



    ## The test ...  If I can't read this and understand what's going on ...then it needs re-writing
    ##   Any function should fit on 1 screen ( ish) ( ideally)
    ##   Each function should be easily describable so we know what it does

    import os
    import pwd
    import grp 


    parser=HandleInputParameters()
    args = parser.parse_args()

    global logMessage # Make it available to all 
    from general_functions import LogMessage
    logMessage=LogMessage(args.logfile)

    
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

    if errorfound:
        sys.exit("\nInput parameter failed validation. See previous messages.\n")


    
    


    logMessage.info('logfile is :' + args.logfile)
    logMessage.info('install_base is :' + args.install_base )
    logMessage.info('template_dsparam is :' + args.template_dsparam) 
    logMessage.info('project_list is :' + str(args.project_list) )




    # Check you will have permissions to change the files as required
 

    try: 
        adminName=GetDSAdminName()
        adminGroup=GetDSAdminGroup()
        
        uid=pwd.getpwnam(adminName).pw_uid  
        #gid=grp.getgrnam(adminGroup).gr_gid
    except KeyError:
        logMessage.error('Unable to find uid or gid for ' + adminName )
        sys.exit("\nUser not found.\n")



    if not os.geteuid() == 0 and not os.getuid() == uid:
        sys.exit("\nOnly root or the datastage admin can run this script\n")

    # Get the standard parameters
    standard_params=GetProjectParamConfig(args.standard_params_file)


    # Get the project specific parameters
    project_specific_params=GetProjectParamConfig(args.project_specific_params_file)



    ## Need to combine those ( project specific overrides standard)



    # Build up new DSParams file from template, plus the standard and project specific Param config, and if compare/fix the DSParams of the target project

    
    project_list=args.project_list

    version_xml=os.path.join(args.install_base,'InformationServer/Version.xml')
    dshome=os.path.join(args.install_base,'InformationServer/Server/DSEngine')
    dsenvfile=os.path.join(dshome,'dsenv')
    



    import os 
    for project in project_list:
     
        dsadm_user=GetDSAdminName(version_xml=version_xml)
        
        project_path=GetProjectPath(project_name=project,dsadm_user=dsadm_user, dshome=dshome)
        if project_path is None:
            logMessage.warning('Skipping ' + project + ' . Unable to find project path.')
            continue


        dsparams_path=os.path.join(project_path,'DSParams')

        if os.path.exists(dsparams_path):
            logMessage.info('Processing ' + dsparams_path)
            CheckFixDSParams(dsparams_path=dsparams_path, templateDSParamsPath=args.template_dsparam,  standard_params=standard_params, project_specific_params=project_specific_params  )
        else:
            logMessage.warning('Skipping ' + project + ' . Unable to find DSParams file ' + dsparams_path) 

        
    

if __name__=="__main__":
    import sys
    main()
