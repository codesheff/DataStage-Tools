#!/usr/bin/env python3

"""
This was written to try and get a standard way of doing logs.
Make available 
    logMessage.info()
    logMessage.debug()  etc



Example for using it:
    
    from MyLogging.mylogging  import getLogFile, setLogFile, LogMessage
    global logMessage
    logMessage=LogMessage()

    
    if getLogFile() is None:
        setLogFile(mylogfilepath)

    

"""

import logging
import logging.config

#import MyLogging.globals  #globals has the path to the config file. Could maybe move it to here

import os


#What's best way to define this? Relative path I guess? Also, check this exists and give decent error if it doesn't
#logging_conf='/iis_backup/DataStage-Tools/MyLogging/logging.conf'
logging_conf=os.path.join(os.path.dirname(__file__),'logging.conf')



def getLogFile():
    if hasattr(logging, 'log_file') == False:
        return None
    else:
        return logging.log_file
    


def setLogFile(log_file):

    """
    Sets the log_file, and also makes sure that the directory exists.

    """
    logging.log_file=log_file
    

    log_dir=os.path.dirname(log_file)
    if ( not(os.path.exists(log_dir))):
        os.makedirs(log_dir,0o755)
      

    logging.config.fileConfig(logging_conf, disable_existing_loggers=False)
    
    return None



#logMessage.info('Project specific DSParams file not found at: ' + args.project_specific_params_file)

class LogMessage():

    import logging
    import logging.config

    #import MyLogging.globals  #globals has the path to the config file. Could maybe move it to here

    import os


    #What's best way to define this? Relative path I guess? Also, check this exists and give decent error if it doesn't
    #logging_conf='/iis_backup/DataStage-Tools/MyLogging/logging.conf'

    logging_conf=os.path.join(os.path.dirname(__file__),'logging.conf')
    def __init__(self):
        # Define your own logger name
        self.log = logging.getLogger("my_logger")
        pass

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
    
    def getLogFile(self):

        if hasattr(logging, 'log_file') == False:
            return None
        else:
            return logging.log_file

    
    def setLogFile(self,log_file):

        """
        Sets the log_file, and also makes sure that the directory exists.

        """
        logging.log_file=log_file
    

        log_dir=os.path.dirname(log_file)
        if ( not(os.path.exists(log_dir))):
            os.makedirs(log_dir,0o755)
      

        logging.config.fileConfig(logging_conf, disable_existing_loggers=False)
    
        return None
                       


    def debug(self,message):
        """
        Add information about the functions in the stack to the message.

        """
        self.log.debug(message + ' ---> ' + self.__getFunctionNames()) 
        

    def info(self,message):
        self.log.info(message)
    
    def warning(self,message):
        self.log.warning(message)
    
    def error(self,message):
        self.log.error(message)
    
    def critical(self,message):
        self.log.critical(message)
    
    
        
    
    
