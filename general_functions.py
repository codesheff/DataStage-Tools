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
        #self.info('Log file is ' + logfile)
        
        for handler in self.log.handlers:
            try:
                logfile=handler.baseFilename
                self.info('Log file is ' + logfile)
            except:
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

        ## new test.
        import inspect
        #func = inspect.currentframe().f_back.f_code

        #inspect.getouterframes(inspect.currentframe())
        #curframe = inspect.currentframe()
        #calframe = inspect.getouterframes(curframe, 2)
        #print('caller name:', calframe[1][3])

        #print(func.co_name)
        #print(func.co_filename)
        #print(func.co_firstlineno)
        #print(inspect.stack()[1][3])

        current_stack=inspect.stack()

        for frame in current_stack:
            if frame[3] == 'main':
                source_file=frame[1]
                break

        if source_file is None:
            top_level_program='default'
        else:
            top_level_program=os.path.basename(source_file)

        import getpass
        current_user=getpass.getuser()

        logfile=os.path.join('/tmp','ds_logging', current_user + '_' +  os.path.splitext(top_level_program)[0] + '.log')


        ## Should I find callling name, by looping through until I find 'main'?

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



class GetCredentials_old():
    """
    This will return args for user and password.
    By default it will user --user and --password, and if not found will check for env variables USER and PASSWORD, and if not found prompt.
    """

    def __init__(self, user_argname='--user',user_envvar='USER',password_argname='--password',password_envvar='PASSWORD'):
        self.user_argname=user_argname
        self.user_envvar=user_envvar
        self.password_argname=password_argname
        self.password_envvar=password_envvar
        
        

    def get_login_args(self):
        import argparse
        import getpass

        def argparser_get_credentials(args):
            args.user, args.password = login(args.user, args.password)


        def login(user, password):
            import os

            if not user:
                if self.user_envvar in os.environ:
                    user = os.environ[self.user_envvar]
                else:
                    user = input("DataStage User:") 

            if not password:
                if self.password_envvar in os.environ:
                    password = os.environ[self.password_envvar]
                else:
                    password = getpass.getpass()    

            return user,password

        parser = argparse.ArgumentParser(description="login")
        parser.set_defaults(funct_getlogon=argparser_get_credentials)
        
        # Login
        parser.add_argument(self.user_argname, dest='user', help=self.user_argname + ' .  If this argument is not passed it will be requested.')
        parser.add_argument(self.password_argname, dest='password', help=self.password_argname + ' .  If this argument is not passed it will be requested.')

        
        args, unknown = parser.parse_known_args() # use 'unknown' to handle unrecognised args

        args.funct_getlogon(args) #This line sets user dfaults

      
        return args


class GetCredentials():
    """
    Returns a parser, with arrgs for user and password added
    
    By default it will user --user and --password, and if not found will check for env variables USER and PASSWORD, and if not found prompt.
    You can specify different argnames and envvars to be used.
    """

    def __init__(self,  user_argname='--user',user_envvar='USER',password_argname='--password',password_envvar='PASSWORD'):
        self.user_argname=user_argname
        self.user_envvar=user_envvar
        self.password_argname=password_argname
        self.password_envvar=password_envvar
        
        

    def add_login_args(self, parser=None):
        """
        Add the login args to a parser. Returns a parser.

        """
        import argparse
        import getpass

        def argparser_get_credentials(args):
            args.user, args.password = login(args.user, args.password)


        def login(user, password):
            import os

            if not user:
                if self.user_envvar in os.environ:
                    user = os.environ[self.user_envvar]
                else:
                    user = input("DataStage User:") 

            if not password:
                if self.password_envvar in os.environ:
                    password = os.environ[self.password_envvar]
                else:
                    password = getpass.getpass()    

            return user,password

        if parser is None:
            # if no parser passed in, set up a new one
            parser = argparse.ArgumentParser(description="login")
        
        parser.set_defaults(funct_getlogon=argparser_get_credentials)
        
        # Login
        parser.add_argument(self.user_argname, dest='user', help=self.user_argname + ' .  If this argument is not passed it will be requested.')
        parser.add_argument(self.password_argname, dest='password', help=self.password_argname + ' .  If this argument is not passed it will be requested.')

      
        return parser

def ReplaceOldWithNewFile(orig_file='', new_temp_file=''):
    """
    Compare original file and the new temp file  ( contents and permissions).
    If they are the same, just remove the temp version. ( maybe not needed, handled in calling function)
    If they are different, backup original and then replace teh orig_file with the new_temp_file

    Return code values:
    0: No changes made
    1: Changes made
    """

    ## Well I've broken this by moving it to another module.
    ## I need to read up on logging, and logging config files
    #  https://docs.python.org/3.8/howto/logging.html#configuring-logging





    import os
    import time
    import shutil

    # If file exists, 
    try:
        type(logMessage) ## check if logMessage is already set up
    except:
        from general_functions import LogMessage
        logMessage=LogMessage() # test just using default log file

    if os.path.exists(orig_file):
    
        import filecmp
        content_matches=filecmp.cmp(orig_file,new_temp_file)
        permission_matches=os.stat(orig_file).st_mode == os.stat(new_temp_file).st_mode
        user_matches=os.stat(orig_file).st_uid == os.stat(new_temp_file).st_uid
        group_matches=os.stat(orig_file).st_gid == os.stat(new_temp_file).st_gid

        logMessage.info( 'Checking file ' + orig_file + '. content_matches:' + str(content_matches) + '; permission_matches:' + str(permission_matches) + ';  user_matches:' + str(user_matches) + ';  group_matches:' + str(group_matches))

        if content_matches and permission_matches and user_matches and group_matches:
            logMessage.info(orig_file + ' is unchanged.')
            os.remove(new_temp_file)
            return 0
        else:
            # backup the original file
            t = time.localtime()
            backupfile=orig_file + time.strftime('%Y%m%d_%H%M%S', t)
            shutil.copyfile(orig_file,backupfile)
        
    else:
        logMessage.info(orig_file + ' - does not exist. Creating new file.')
    
    ## Only got to here if does not match  (ie new or different)
    logMessage.info(orig_file + ' - has been amended. ( to match ' + new_temp_file + ' )')
    #shutil.copyfile(new_temp_file, orig_file)
    shutil.move(new_temp_file, orig_file)
    
    return 1
 
      