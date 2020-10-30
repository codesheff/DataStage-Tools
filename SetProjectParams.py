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

def LogMessage(text=''):

    import traceback
    import logging

    # Set up logging 2x. One for logging to file, and one for logging to screen.
    # You can control the logging level to each separately - and also at top level
    
    # log - general 
    log = logging.getLogger('logger')
    log.setLevel(logging.DEBUG)     #  this is initial filter. Messages have to be above this to get anywhere.

    formatter = logging.Formatter('%(message)s')
    
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

    

    #logging.basicConfig(level=logging.INFO,filename='/tmp/app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    
    
   
    trace_b=traceback.extract_stack(limit=None)
    
    
    # Loop backwards through stack , to get function names
    funcs=[]
    for i in range( len(trace_b) - 1, -1, -1):
        
        ## If we hit '<module>', then stop. I assume this is as far as we need to go.
        if trace_b[i][2] == '<module>':
            break

        funcs.append(trace_b[i][2])  

    print(funcs)
    print('And now for some logging...')
    
    log.info('This is info')
    log.warn('This is a warning')
    log.error('This is an error')
    log.debug('This is a debug')



def GetDSParamValues(filePath=''):
    """
    Get values from a DSParam file and load them to a format we can process
    """
    LogMessage('hello')



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



##  Main line
parser=HandleInputParameters()
args = parser.parse_args()

print('logfile is :' + args.logfile )
print('install_base is :' + args.install_base )
print('template_dsparam is :' + args.template_dsparam )

projectParamConfig=GetProjectParamConfig()
#print(projectParamConfig)

GetDSParamValues(args.template_dsparam)

