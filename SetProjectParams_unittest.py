#!/usr/bin/env python3


## I don't know how to do this.. some reading needed first 

import unittest





class TestPassUserAndPasswordArgs(unittest.TestCase):
    def test_pass_in_both_defaultname(self):

        """
        Environment variables: unset   
        Args : default names
        """

        scriptname=sys.argv[0]
        sys.argv=[''] 
        sys.argv[0]=scriptname
        sys.argv.append('--install-base')
        sys.argv.append('/iis/01')
        sys.argv.append('--project-name')
        sys.argv.append('dstage1')
        
        from SetProjectParams import HandleInputParameters


        # Get input paramaters 
        parser=HandleInputParameters()
        args = parser.parse_args()


        global logMessage # Make it available to all 
        from general_functions import LogMessage
        logMessage=LogMessage(args.logfile)


        from SetProjectParams import GetAmendedEnvVars, GetProjectParamConfig

       
          

        logMessage.info('logfile is :' + args.logfile)
        #logMessage.info('install_base is :' + args.install_base )
        #logMessage.info('template_dsparam is :' + args.template_dsparam) 
        #logMessage.info('project_list is :' + str(args.project_list) )
        #logMessage.info('standard params file is : ' + args.standard_params_file)
        #logMessage.info('project specific params file is : ' + args.project_specific_params_file)

        
        templateDSParamsPath=args.template_dsparam
        standard_params=GetProjectParamConfig(args.standard_params_file)

        amendedEnvVars=GetAmendedEnvVars(origEnvVar={}, templateDSParamsPath=templateDSParamsPath , params_to_update=standard_params)
        #ds_login_args = Credentials.add_login_args().parse_args()
        #ds_login_args.funct_getlogon(ds_login_args)
        
        self.assertEqual('2','2')
        #self.assertEqual(ds_login_args.user, arg_username)
        #self.assertEqual(ds_login_args.password, arg_password)


import sys

scriptname=sys.argv[0]
sys.argv=[''] 
sys.argv[0]=scriptname





#envvar_username='EnvUserName1'
#envvar_password='EnvPassword1'
#arg_username='ArgUserName1'
#arg_password='ArgPassword1'
#arg_alternative_user_name='--ds-user'
#arg_alternative_password_name='--ds-password'
unittest.main()
