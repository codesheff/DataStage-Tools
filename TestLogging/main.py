#!/usr/bin/env python3

import logging
import sys

# Log file location
logfile = '/tmp/debug.log'


# Define your own logger name
logger = logging.getLogger("my_logger")
# Set default logging level to DEBUG
logger.setLevel(logging.DEBUG)

# create a console handler
# and define a custom log format, set its log level to CRITICAL
print_format = logging.Formatter('%(levelname)-8s %(name)-12s %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.CRITICAL)
console_handler.setFormatter(print_format)

# create a log file handler
# and define a custom log format, set its log level to DEBUG
log_format = logging.Formatter('[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')
file_handler = logging.FileHandler(logfile)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)

#Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Write messages with all different types of levels
logger.debug('debug')
logger.info('info')
logger.warning('warning')
logger.error('error')
logger.critical('critical')