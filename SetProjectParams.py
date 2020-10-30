#!/usr/bin/env python3

"""
This script will 
  * take in path to a param file?( format?), which contains project parameter definitions.
  * take the standard DSParams from Template, and apply the project parameter definitions to it to create a new DSParams file.
  * compare the new DSParams file with the current active one for the project. If it has changed, it will back up the current one, and move the new one into place.

"""
import sys
import argparse

import re
import os 




def GetProjectParamConfig():
    """
    This should really take  in a path to the config file
    Returns json object

    """

    projectParamConfig= [
        {
            "name": "Sabrina Green",
            "username": "sgreen",
            "phone": {
                      "office": "802-867-5309",
                      "cell": "802-867-5310"
                   },
            "department": "IT Infrastructure",
            "role": "Systems Administrator"
        },
        {
            "name": "Eli Jones",
            "username": "ejones",
            "phone": {
                      "office": "684-348-1127"
                      },
            "department": "IT Infrastructure",
            "role": "IT Specialist"
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
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    

    #If I did want to use traceback to get funtion names I could do something like this
    ## But I might need to set up a class for this.
    
    
    import traceback
    trace_b=traceback.extract_stack(limit=None)
    
    
    # Loop backwards through stack , to get function names
    funcs=[]
    for i in range( len(trace_b) - 1, -1, -1):
    #    
    #    ## If we hit '<module>', then stop. I assume this is as far as we need to go.
        if trace_b[i][2] == '<module>':
            break
    #
        funcs.append(trace_b[i][2])  

    return log





def GetDSParamValues(filePath=''):
    """
    Get values from a DSParam file and load them to a format we can process
    """
    
    ## Trying to set it up so it uses same object if it already exists
    #logMessage=SetUpLog()
    # If I just set it up in main script it works.
    # Am I going to have to put this try block in every function that uses logging?
    # Maybe just better to just import my LogMessages class each time and create as new local object.

    try:
        logMessage.debug('Entered function GetDSParamValues')
    except:
        logMessage=LogMessage()
        logMessage.debug('Entered function GetDSParamValues')

    def SubFun1():
        pass
        logMessage.info('We are now in GetDSParamValues. ')

    
    SubFun1()




def HandleInputParameters():
    
    this_script_path=(os.path.dirname(sys.argv[0]))
    #print('this_script_path:' + this_script_path)
    # this_script_name=(os.path.basename(sys.argv[0]))
    datadir=os.path.join(this_script_path,"data") # Ah!  you don't want the '/' in your args - makes sense!
    #print('datadir:' + datadir)
    
    default_logfile=os.path.join(datadir,"syslog_example")
    #print('default is :' + default_logfile)
    # Set up input options
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--logfile", type=str, dest="logfile", help="the logfile to be processed", default=default_logfile)
    parser.add_argument("--install-base", type=str, dest="install_base", help="The base of the DS install. e.g /iis/01 .", default='/iis/01')
    parser.add_argument("--template-dsparam", type=str, dest="template_dsparam", help="the template DSParam file", default='/iis/01/InformationServer/Server/Template/DSParams')
    #global args
    #args = parser.parse_args()
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
        self.log.info(message + self.__getFunctionNames())
    
    def debug(self, message):
        """
        This method is to log info
        """
        self.log.debug(message + self.__getFunctionNames())



##  Main line
logMessage=LogMessage()
parser=HandleInputParameters()
args = parser.parse_args()

logMessage.info('logfile is :' + args.logfile)
logMessage.info('install_base is :' + args.install_base )
logMessage.info('template_dsparam is :' + args.template_dsparam )

projectParamConfig=GetProjectParamConfig()
#print(projectParamConfig)



logMessage=LogMessage()
#logMessage=SetUpLog()

#logMessage.info('info message')

GetDSParamValues(args.template_dsparam)

