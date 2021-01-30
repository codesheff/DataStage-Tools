#!/usr/bin/env python3


import logging
import logging.config

import globals

# Define the logging.conf filePath
if hasattr(logging, 'log_file') == False:
    logging.log_file='/tmp/stetest_module2default.log'

# No way to check if this is already set or not.
logging.config.fileConfig(globals.logging_conf, disable_existing_loggers=False)


# Use the logger defined in your config
logger = logging.getLogger("my_logger")



# Write messages with all different types of levels


def WriteSomeLogMessages_mod2():
    logger.debug('debug - from module2')
    logger.debug('debug 0',stacklevel=0)
    logger.debug('debug 1',stacklevel=1)
    logger.debug('debug 2',stacklevel=2)
    logger.debug('debug 3',stacklevel=3)
    logger.info('info - from module2')
    logger.warning('warning - from module2')
    logger.error('error - from module2')
    logger.critical('critical - from module2')

    from standard_functions import  getFunctionNames
    funNames=getFunctionNames()

    print(funNames)


def main():
    print('This is main')
    WriteSomeLogMessages_mod2()


if __name__== "__main__" :
    main()




