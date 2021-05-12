#!/usr/bin/env python3


## I don't know how to do this.. some reading needed first 
## Can I setup the logMessage here , and make it available for fuctions in the script to be tested to use?

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
        from general_functions import LogMessage, getLogFile, setLogFile
        #logMessage=LogMessage(args.logfile)
        logMessage=LogMessage()  
        logMessage.setLogFile(args.logfile)


        from SetProjectParams import GetAmendedEnvVars, GetProjectParamConfig

       
          

        logMessage.info('logfile is :' + args.logfile)
        #logMessage.info('install_base is :' + args.install_base )
        #logMessage.info('template_dsparam is :' + args.template_dsparam) 
        #logMessage.info('project_list is :' + str(args.project_list) )
        #logMessage.info('standard params file is : ' + args.standard_params_file)
        #logMessage.info('project specific params file is : ' + args.project_specific_params_file)

        
        templateDSParamsPath=args.template_dsparam
        standard_params=GetProjectParamConfig(args.standard_params_file)
        standard_project_settings={}
        standard_autopurge_settings={}
        install_base=args.install_base
        temp_base='/tmp'
        project_name=str(args.project_list[0])

        #amendedEnvVars=GetAmendedEnvVars(origEnvVar={}, templateDSParamsPath=templateDSParamsPath , params_to_update=standard_params)
        amendedEnvVars,amendedProjectSettings, amendedAutoPurge =GetAmendedEnvVars(origEnvVar={},            origProjectSettings={},                    origAutoPurge={},               templateDSParamsPath=templateDSParamsPath , params_to_update=standard_params, project_settings_to_update=standard_project_settings, autopurge_settings_to_update=standard_autopurge_settings, install_base=install_base, temp_base=temp_base, project_name=project_name)
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
