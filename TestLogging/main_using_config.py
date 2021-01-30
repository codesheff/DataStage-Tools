#!/usr/bin/env python3

import logging
import logging.config

import globals

import os

def RemoveFile(file=''):
    try:
        os.remove(file)
    except:
        pass

    return 0

RemoveFile('/tmp/stetest1.log')
RemoveFile('/tmp/stetest2.log')
RemoveFile('/tmp/stetest3.log')

# Define the logging.conf filePath
#logging.log_file='/tmp/stetest1.log'
#logging.config.fileConfig('/iis_backup/DataStage-Tools/TestLogging/logging.conf', disable_existing_loggers=False)

if hasattr(logging, 'log_file') == False:
    logging.log_file='/tmp/stetest_module1default.log'

# No way to check if this is already set or not.
logging.config.fileConfig(globals.logging_conf, disable_existing_loggers=False)




# Define your own logger name
logger = logging.getLogger("my_logger")



# Write messages with all different types of levels
logger.debug('debug 0',stacklevel=0)
logger.debug('debug 1',stacklevel=1)
logger.debug('debug 2',stacklevel=2)
logger.debug('debug 3',stacklevel=3)
logger.info('info')
logger.warning('warning')
logger.error('error')
logger.critical('critical')


# Define a variable, so we can see if its available when I call code in another module
myvariable='/tmp/newfilename.txt'

#import module1 

#module1.WriteSomeLogMessages()

## Now test just importing single function

from module1 import WriteSomeLogMessages_mod1
#logging.log_file='/tmp/stetest3.log'
WriteSomeLogMessages_mod1()

from standard_functions import  getFunctionNames
funNames=getFunctionNames()

print(funNames)