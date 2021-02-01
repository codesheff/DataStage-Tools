#!/usr/bin/env python3

#import logging
#import logging.config

from mylogging import getLogFile, setLogFile, LogMessage
#import globals

import os

def RemoveFile(file=''):
    try:
        os.remove(file)
    except:
        pass

    return 0

RemoveFile('/tmp/stetest_main.log')
RemoveFile('/tmp/stetest_module1.log')
RemoveFile('/tmp/stetest_module2.log')
RemoveFile('/tmp/stetest_module1_a.log')


test = getLogFile()
if getLogFile() is None:
    setLogFile('/tmp/logs/stetest_main.log')

logMessage=LogMessage()

# Write messages with all different types of levels
logMessage.info('info - log file ' + getLogFile())
logMessage.debug('debug - from main')
logMessage.info('info - from main')
logMessage.warning('warning - from main')
logMessage.error('error - from main')
logMessage.critical('critical - from main')


# Define a variable, so we can see if its available when I call code in another module
myvariable='/tmp/newfilename.txt'

import module1 

module1.WriteSomeLogMessages_mod1()

## Now test just importing single function

from module2 import WriteSomeLogMessages_mod2
setLogFile('/tmp/logs/stetest_main2.log') #You can change the log file like this.
WriteSomeLogMessages_mod2()

