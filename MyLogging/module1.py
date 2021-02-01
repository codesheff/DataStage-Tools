#!/usr/bin/env python3



from mylogging import getLogFile, setLogFile, LogMessage

test = getLogFile()
if getLogFile() is None:
    setLogFile('/tmp/logs/stetest_module1.log')


logMessage=LogMessage()


def WriteSomeLogMessages_mod1():
    logMessage.debug('debug - from module1')
    logMessage.info('info - from module1')
    logMessage.warning('warning - from module1')
    logMessage.error('error - from module1')
    logMessage.critical('critical - from module1')


def main():
    print('This is main')

    logMessage.debug('debug - from module1 when run as main')
    logMessage.info('info - from module1 when run as main')
    logMessage.warning('warning - from module1 when run as main')
    logMessage.error('error - from module1 when run as main')
    logMessage.critical('critical - from module1 when run as main')


if __name__== "__main__" :
    main()


