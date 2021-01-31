import logging
import logging.config

import globals  #globals has the path to the config file. Could maybe move it to here

import os





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
      

    logging.config.fileConfig(globals.logging_conf, disable_existing_loggers=False)
    
    return None



#logMessage.info('Project specific DSParams file not found at: ' + args.project_specific_params_file)

class LogMessage():
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
    
    
        
    
    
