#!/usr/bin/env python3

"""
This will be used to store functions that are generally of use in our scripting.
This can be used to help give a standard behaviour to all our scripts.
"""


def SayHi():
    """
    return 'Hi'
    """

    return 'Hi'




class LogMessage():

    """
    This will setup up message logging.
    By default:
    INFO and ERROR will go to screen, and also to the log file.
    DEBUG will just go to the log file
    """

    def __init__(self,logfile='/tmp/logfile.txt'):
        
        self.log=self.__GetLogger(logfile)
        self.info('Log file is ' + logfile)
    
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

    def info(self, message):
        """
        This method is to log info
        """
        self.log.info(message)
    
    def debug(self, message):
        """
        This method is to log dubug information. 
        It will include the list functions in current call stack.
        """
        self.log.debug(message + ' ---> ' + self.__getFunctionNames())
    
    def error(self, message):
        """
        This method is to log error
        """
        self.log.error(message )

    def warning(self, message):
        """
        This method is to log warnings
        """
        self.log.warning(message )

    def __GetLogger(self, logfile='/tmp/logfile.txt'):
        import os
        import logging

        #Maybe this should be a class really. Something I set up once at start of script, rather than reimporting every time we log a message.
        # Set up logging 2x. One for logging to file, and one for logging to screen.
        # You can control the logging level to each separately - and also at top level

        # log - general 
        log = logging.getLogger('logger')
        log.setLevel(logging.DEBUG)     #  this is initial filter. Messages have to be above this to get anywhere.
        
        formatter_debug = logging.Formatter('%(asctime)s : %(levelname)s -  %(message)s  ( from %(filename)s -> %(module)s) -> %(funcName)s ) ')
        formatter_info =  logging.Formatter('%(asctime)s : %(levelname)s -  %(message)s ')
           
        # fh - logging filehandler, This is intened for debugging
        ## Make sure dir exists 
        logdir=os.path.dirname(logfile)

        if ( not(os.path.exists(logdir))):
            os.mkdir(logdir)
            os.chmod(logdir,0o755)
        else:
            pass

        fh = logging.FileHandler(logfile, mode='w', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter_debug)
        log.addHandler(fh)

        # ch - logging streamhandler. This is what will appear on your stdout
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO) ## Change to DEBUG while testing. Should just be INFO normally
        #ch.setLevel(logging.DEBUG) ## Change to DEBUG while testing. Should just be INFO normally
        ch.setFormatter(formatter_info)
        log.addHandler(ch)

        return log

