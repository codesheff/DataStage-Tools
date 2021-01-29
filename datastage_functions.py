#!/usr/bin/env python3

#print('Hello')


def GetValueFromVersionXML(VersionXMLPath='/iis/test//InformationServer/Version.xml' ,VariableName='datastage.user.name'):
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

        # Not sure if other fiels are useful yet, so just getting nama and value
        #encrypted=result[1]
        name=result[2]
        #persistent=result[3]
        #readonly=result[4]
        value=result[5]

        versionXMLValue[name]=value



    
    f.close
    return(versionXMLValue)



#value=GetValueFromVersionXML('/iis/01//InformationServer/Version.xml','datastage.user.name' )
#value=GetValueFromVersionXML('/iis/01//InformationServer/Version.xml','lwas.home.dir' )
#print('Value is '  + value)
