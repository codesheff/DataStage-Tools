#!/usr/bin/env python3

#print('Hello')


def GetValueFromVersionXML(VersionXMLPath='/iis/test/InformationServer/Version.xml' ,VariableName='datastage.user.name'):
    """
    return value for 'VariableName' in Version.xml file
    """

    # Define versionXMLValue as global, so that we can cache the results

    global versionXMLValue

    try: 
        versionXMLValue[VariableName]
    except (NameError, KeyError):
        versionXMLValue=GetValuesFromVersionXML(VersionXMLPath=VersionXMLPath)


    return versionXMLValue[VariableName]



def GetValuesFromVersionXML(VersionXMLPath='/iis/test/InformationServer/Version.xml'):
    """
    return dictionary of values  from Version.xml file
    """

    import re

    try:
        f = open(VersionXMLPath)
    except OSError:
        return None

    # Define versionXMLValue as global, so that we can cache the results
    global versionXMLValue
    
    try: 
        versionXMLValue
    except NameError:
        versionXMLValue={}

    
    # Version.xml has values stored in lines like this:
    #line='    <PersistedVariable encrypted="false" name="ds.sqlowner" persistent="true" readonly="true" value="dsadm"/>\n'
    #line='    <PersistedVariable encrypted="false" name="db2.fenced.home.directory" persistent="true" readonly="true" value="/iis/home/db2fenc1"/>\n'

    pattern=r'^\s*<PersistedVariable encrypted="(\w*)" name="([\w.]*)" persistent="(true|false)" readonly="(true|false)" value="([\w/]*)".*'
    
    for line in f:
        
        result=re.search(pattern, line)
        if result == None:
            continue

        # Not sure if other fields are useful yet, so just getting nama and value
        #encrypted=result[1]
        name=result[2]
        #persistent=result[3]
        #readonly=result[4]
        value=result[5]

        versionXMLValue[name]=value



    
    f.close
    return(versionXMLValue)

def GetDSAdminName(version_xml='/iis/test/InformationServer/Version.xml'):
    """
    This should be the standard way of getting the DataStage admin user name
    """

    from datastage_functions import GetValueFromVersionXML

    #version_xml='/iis/01/InformationServer/Version.xml'
    variable_name='datastage.user.name'
    value=GetValueFromVersionXML(version_xml,variable_name )
    
    return value


def GetDSAdminGroup(version_xml='/iis/test/InformationServer/Version.xml'):
    """
    This should be the standard way of getting the DataStage admin users group
    """

    from datastage_functions import GetValueFromVersionXML

    
    variable_name='ds.admin.gid'
    value=GetValueFromVersionXML(version_xml,variable_name )
    return value


    return value

def GetProjectPath(project_name='dstage1',dsadm_user='dsadm', dshome='/iis/test/InformationServer/Server/DSEngine'):
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

    import getpass
    current_user=getpass.getuser()
    
    dsenv=os.path.join(dshome,'dsenv')
    dsjobcommand=os.path.join(dshome,'bin/dsjob')
    command='source ' + dsenv + ' ; ' +  dsjobcommand + ' -projectinfo ' + project_name
    sudo_command='sudo -u ' + dsadm_user + ' -s sh -c "' + command + ' | grep \'^Project Path\'"'

    if current_user == dsadm_user:
        command_to_run = command
    else:
        command_to_run = sudo_command
    
    
    ## Annoying
    import sys
    if sys.version_info >= (3,7):
        result = subprocess.run([command_to_run] , capture_output=True, shell=True, encoding="UTF-8")
    else: 
        result = subprocess.run([command_to_run] , shell=True, encoding="UTF-8", stdout=subprocess.PIPE)



    if result.returncode != 0:
        return None
    else:
        pattern=r'^Project Path\t: (.*)'
        projectpath = re.search(pattern,result.stdout)[1]
        return(projectpath)



if __name__== "__main__" :
    print('Not intended to be run as a script.')


