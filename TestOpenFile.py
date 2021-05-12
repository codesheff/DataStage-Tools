#!/usr/bin/env python3 


try:
    with open('/etc/hosts2') as f:

        for line in f:
            print(line)

    
except OSError:
    print('None')

from general_functions import LogMessage
logMessage=LogMessage()
logMessage.debug('Entered SetProjectParams.py')
logMessage.setLogFile('/tmp/stetest/logs2')
logMessage.debug('Entered Hello Again2')
logMessage.setLogFile('/tmp/stetest/logs3')
logMessage.debug('Entered Hello Again3')
print(logMessage.getLogFile())

    #setLogFile(args.logfile) 
