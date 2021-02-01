#!/usr/bin/env python3



from mylogging import getLogFile, setLogFile, LogMessage

test = getLogFile()
if getLogFile() is None:
    setLogFile('/tmp/logs/stetest_module2.log')


logMessage=LogMessage()


def WriteSomeLogMessages_mod2():
    logMessage.debug('debug - from module2')
    logMessage.info('info - from module2')
    logMessage.warning('warning - from module2')
    logMessage.error('error - from module2')
    logMessage.critical('critical - from module2')


def main():
    print('This is main')

    logMessage.debug('debug - from module2 when run as main')
    logMessage.info('info - from module2 when run as main')
    logMessage.warning('warning - from module2 when run as main')
    logMessage.error('error - from module2 when run as main')
    logMessage.critical('critical - from module2 when run as main')


if __name__== "__main__" :
    main()


