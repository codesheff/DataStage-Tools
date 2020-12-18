#!/usr/bin/env python3


## I don't know how to do this.. some reading needed first 

import unittest

from general_functions import GetCredentials

class TestPassUserAndPasswordArgs(unittest.TestCase):
    def test_pass_in_both_defaultname(self):

        """
        Environment variables: unset   
        Args : default names
        """

        
        arguments='--user ' + arg_username + ' --password ' + arg_password
        sys.argv=[]
        sys.argv.append(scriptname)
        sys.argv+=arguments.split()

        Credentials = GetCredentials(user_argname='--user')
        ds_login_args = Credentials.add_login_args().parse_args()
        ds_login_args.funct_getlogon(ds_login_args)
        
        self.assertEqual(ds_login_args.user, arg_username)
        self.assertEqual(ds_login_args.password, arg_password)

    def test_pass_in_both_newnames(self):

        
        """
        Environment variables: unset   
        Args : Specify names
        """

    
        arguments=arg_alternative_user_name + ' ' + arg_username + ' ' + arg_alternative_password_name + ' '  + arg_password
        sys.argv=[]
        sys.argv.append(scriptname)
        
        sys.argv+=arguments.split()

        Credentials = GetCredentials(user_argname=arg_alternative_user_name,password_argname=arg_alternative_password_name)
        
        ds_login_args = Credentials.add_login_args().parse_args()
        ds_login_args.funct_getlogon(ds_login_args)
        
        self.assertEqual(ds_login_args.user, arg_username)
        self.assertEqual(ds_login_args.password, arg_password)

    def test_os_var(self):

        """ 
        Set environment variables - standard
        Do not pass in args
        """


        import os 
        arguments=''
        sys.argv=[]
        sys.argv.append(scriptname)
        sys.argv+=arguments.split()
        
        os.environ['USER']=envvar_username
        os.environ['PASSWORD']=envvar_password
        

        Credentials = GetCredentials()
        
        ds_login_args = Credentials.add_login_args().parse_args()
        ds_login_args.funct_getlogon(ds_login_args)
        
        self.assertEqual(ds_login_args.user, envvar_username)
        self.assertEqual(ds_login_args.password, envvar_password)

    def test_arrgs_and_env_var(self):

        """ 
        Set environment variables - standard
        Pass in args
        Args should overriee env vars.
        """


        import os 
        arguments='--user ' + arg_username + ' --password ' + arg_password
        sys.argv=[]
        sys.argv.append(scriptname)

        
        sys.argv+=arguments.split()
               
        os.environ['USER']=envvar_username
        os.environ['PASSWORD']=envvar_password
        

        Credentials = GetCredentials()
        
        ds_login_args = Credentials.add_login_args().parse_args()
        ds_login_args.funct_getlogon(ds_login_args)
        
        self.assertEqual(ds_login_args.user, arg_username)
        self.assertEqual(ds_login_args.password, arg_password)
    
import sys

scriptname=sys.argv[0]
sys.argv=[''] 
sys.argv[0]=scriptname

envvar_username='EnvUserName1'
envvar_password='EnvPassword1'
arg_username='ArgUserName1'
arg_password='ArgPassword1'
arg_alternative_user_name='--ds-user'
arg_alternative_password_name='--ds-password'
unittest.main()



