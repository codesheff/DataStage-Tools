#!/usr/bin/env python3

#print('Hello')


from MyLogging.mylogging  import getLogFile, setLogFile, LogMessage
import os 
global logMessage
logMessage=LogMessage()

    #test = getLogFile()
if getLogFile() is None:
    setLogFile(os.path.join(os.sep,'tmp','logs','stetest_datastage_functions.log'))
    



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



def GetListOfComponentsRecentlyModified(modified_since, xmeta_user='db2inst1', xmeta_password='default' ):

    """
    modified_since should be a datetime  ( utc) ( or None).

    What's the best way of providing db credentials to this?

    Initial MVP  - just doing jobdefns
    
    """
    
    if modified_since is None:
        logMessage.info('Getting list of all DataStage components')
    else:
        logMessage.info('Getting list of DataStage components modified since :' + str(modified_since) )

    # https://www.ibm.com/docs/en/db2/9.7?topic=db-fetching-rows-columns-from-result-sets
    #https://stackoverflow.com/questions/6044326/how-to-connect-python-to-db2

    #from ibm_db import connect, exec_immediate  

    database='XMETA'
    database_schema='XMETA'



    

    ## Setup input args

    
    import ibm_db
    # Careful with the punctuation here - we have 3 arguments.
    # The first is a big string with semicolons in it.
    # (Strings separated by only whitespace, newlines included,
    #  are automatically joined together, in case you didn't know.)
    # The last two are emptry strings.
    conn = ibm_db.connect('DATABASE='+ database +';'
                     'HOSTNAME=localhost;'  # 127.0.0.1 or localhost works if it's local
                     'PORT=50000;'
                     'PROTOCOL=TCPIP;'
                     'UID=' + xmeta_user + ';'
                     'PWD=' + xmeta_password  + ';', '', '')
    
    ## Example ..get all tables
    #from ibm_db import tables
    #t = db2_results(tables(connection))
    #print(t)

    
    # This SQL would show you the different types of class and users that modify things.
    #db2 "select CLASSNAME_XMETA, XMETA_MODIFIED_BY_USER_XMETA, count(*) from DATASTAGEX_DSITEM group by  CLASSNAME_XMETA, XMETA_MODIFIED_BY_USER_XMETA "
    ## Maybe we should not include things last modified by DataStageSystemUser in the backup - I assume they are default components.



    #SQL="select NAME_XMETA, XMETA_MODIFICATION_TIMESTAMP_XMETA \
    # from ISMETA01.DATASTAGEX_DSJOBDEF \
    # order by XMETA_MODIFICATION_TIMESTAMP_XMETA desc \
    # fetch first 6 rows only"

    ##ob I created has modification date 2020-10-08-08.29.14.000000
    #That's shown as 1602142154825 in db2
    #
    #So, need to divide the number by 1000 and add as seconds to 1970-01-01
    
    

    # Convert the timestamp input 

    from datetime import datetime
    dt = datetime.today()  # Get timezone naive now
    
    seconds = dt.timestamp()

    import time
    import datetime
    
  
  
    where_clause="""
       t2.XMETA_MODIFIED_BY_USER_XMETA <> 'DataStageSystemUser' 
       and t2.XMETA_MODIFIED_BY_USER_XMETA <> 'admin01' 
    """

    if modified_since is not None:
        where_clause+=' and XMETA_MODIFICATION_TIMESTAMP_XMETA >= ' + str(modified_since.timestamp() * 1000 )
        

    

    #sql="""
    # select XMETA_MODIFIED_BY_USER_XMETA, PROJECTNAMESPACE_XMETA, CLASSNAME_XMETA, NAME_XMETA, XMETA_MODIFICATION_TIMESTAMP_XMETA 
    # from  XMETA.DATASTAGEX_DSITEM  
    # where """ + where_clause + """
    # ;
    # """

    sql="""
    select t1.CATEGORY_XMETA, t2.NAME_XMETA, t2.XMETA_MODIFICATION_TIMESTAMP_XMETA, t2.CLASSNAME_XMETA, t2.PROJECTNAMESPACE_XMETA
    from """ + database_schema + """.DATASTAGEX_DSJOBDEF t1
    inner join """ + database_schema + """.DATASTAGEX_DSITEM t2 on ( t1.XMETA_REPOS_OBJECT_ID_XMETA  = t2.REPOSID_XMETA  ) 
    where """ + where_clause + """
    ;
    """
     
    ## Need to include component path in here too. 
    ## I guess need to join to these or tables like these 
    """"                    DATASTAGEX_DSIMSVIEWSET                                                                                                          CATEGORY_XMETA
                            DATASTAGEX_DSJCLTEMPLATE                                                                                                         CATEGORY_XMETA
                            DATASTAGEX_DSJOBDEF                                                                                                              CATEGORY_XMETA
                            DATASTAGEX_DSMACHINEPROFILE                                                                                                      CATEGORY_XMETA
                            DATASTAGEX_DSPARAMETERSET                                                                                                        CATEGORY_XMETA
                            DATASTAGEX_DSROUTINE                                                                                                             CATEGORY_XMETA
                            DATASTAGEX_DSSHAREDCONTAINERDEF                                                                                                  CATEGORY_XMETA
                            DATASTAGEX_DSSTAGETYPE                                                                                                           CATEGORY_XMETA
                            DATASTAGEX_DSTABLEDEFINITION                                                                                                     CATEGORY_XMETA
                            DATASTAGEX_DSTRANSFORM                                                                                                           CATEGORY_XMETA
                            VWDATASTAGEX_DSIMSROOTOBJECT                                                                                                     CATEGORY_XMETA
                            VWMMI_ABSTRACTPERSISTENTADMINPROPERTY                                                                                            CATEGORY_XMETA


    maybe better to have something liek.
    select t1.CATEGORY_XMETA , t2.*
from DATASTAGEX_DSJOBDEF t1
inner join DATASTAGEX_DSITEM t2 on ( t1.XMETA_REPOS_OBJECT_ID_XMETA  = t2.REPOSID_XMETA  ) 
    """
    ## build dictionary of 
    #( engine, project) [ (component_type, component_name, component_last_modified_timestamp) , .. , ..  ]
    objectsList={} # 

    #sql = "SELECT * FROM XMETA.DATASTAGEX_DSITEM "
    stmt = ibm_db.exec_immediate(conn, sql)
    #counter=0
    while ibm_db.fetch_row(stmt) != False:
        #counter+=1
        #mod_timestamp=datetime.datetime.fromtimestamp(mod_timestamp_unix,tz=datetime.timezone.utc) # Let's just stick with utc.
        #formatted_modification_timestamp=mod_timestamp.strftime("%A, %B %d, %Y %I:%M:%S")
        project_namespace= ibm_db.result(stmt, "PROJECTNAMESPACE_XMETA")
        project_namespace_tuple = tuple(project_namespace.split(':'))
        component_type= ibm_db.result(stmt, "CLASSNAME_XMETA")
        component_name= ibm_db.result(stmt, "NAME_XMETA")
        mod_timestamp_unix=int(ibm_db.result(stmt, "XMETA_MODIFICATION_TIMESTAMP_XMETA"))/1000
        component_last_modified_ts= datetime.datetime.fromtimestamp(mod_timestamp_unix,tz=datetime.timezone.utc)
        category= ibm_db.result(stmt, "CATEGORY_XMETA")
        
        try:
            objectsList[project_namespace_tuple]+=[(component_type,component_name,component_last_modified_ts,category)]
        except KeyError:
            objectsList[project_namespace_tuple]=[(component_type,component_name,component_last_modified_ts,category)]

    return objectsList

def ExportAJob(modified_since):
    pass

    
    
        
 
        


if __name__== "__main__" :
    print('Not intended to be run as a script.')


