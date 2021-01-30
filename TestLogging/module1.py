#!/usr/bin/env python3


import logging
import logging.config
import globals


# No need to set these here. It will pick up the values already set.
#logging.log_file='/tmp/stetest2.log'
#logging.config.fileConfig('/iis_backup/DataStage-Tools/TestLogging/logging.conf', disable_existing_loggers=False)

if hasattr(logging, 'log_file') == False:
    logging.log_file='/tmp/stetest_module1default.log'

# No way to check if this is already set or not.
logging.config.fileConfig(globals.logging_conf, disable_existing_loggers=False)


# Use the logger defined in your config
logger = logging.getLogger("my_logger")



# Write messages with all different types of levels


def WriteSomeLogMessages_mod1():
    logger.debug('debug - from module1')
    logger.debug('debug 0',stacklevel=0)
    logger.debug('debug 1',stacklevel=1)
    logger.debug('debug 2',stacklevel=2)
    logger.debug('debug 3',stacklevel=3)
    logger.info('info - from module1')
    logger.warning('warning - from module1')
    logger.error('error - from module1')
    logger.critical('critical - from module1')

    from standard_functions import  getFunctionNames
    funNames=getFunctionNames()

    print(funNames)

    #import module2

    #module2.WriteSomeLogMessages_mod2()

def main():
    print('This is main')

if __name__== "__main__" :
    main()


