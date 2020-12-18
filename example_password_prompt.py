#!/usr/bin/env python3

"""Testing out how to get user name and password.

Should check args, then env variables, then prompt

e.g.
./example_password_prompt.py --hostName HN01 --jobName Job_1 --project-name dstage1 --ds-user username --ds-password password

"""



from general_functions import GetCredentials

def main():

    print('Hello ' + args.user + '. Your password is ' +  args.password + ' .')
    pass


if __name__ == '__main__':
    

    ## You can create the parser, using GetCredentials, or you can add to an existing parser.

    
    Credentials = GetCredentials(user_argname='--ds-user', password_argname='--ds-password')
    parser = Credentials.add_login_args()
    
    parser.add_argument("--hostName", type=str, dest="hostName", help="The hostName of the DataStage engine. e.g HN01 ", default='HN01', required=True) # Setting all to false here as it's making testing easier
    parser.add_argument("--projectName", type=str, dest="projectName", help="project to compile jobs in ", required=True)
    parser.add_argument("--jobName", action='append', type=str, dest="job_list", help="jobs to compile", required=True)
    
    args = parser.parse_args()
    args.funct_getlogon(args)

    # Code below,  that is commented out, woult create a parser and then use GetCredentials to add to the existing parser
    #import argparse
    #parser = argparse.ArgumentParser()
    #parser.add_argument("--hostName", type=str, dest="hostName", help="The hostName of the DataStage engine. e.g HN01 ", default='HN01', required=True) # Setting all to false here as it's making testing easier
    #parser.add_argument("--projectName", type=str, dest="projectName", help="project to compile jobs in ", required=True)
    #parser.add_argument("--jobName", action='append', type=str, dest="job_list", help="jobs to compile", required=True)

    #Credentials = GetCredentials(user_argname='--ds-user', password_argname='--ds-password')
    #parser = Credentials.add_login_args(parser)
    #args = parser.parse_args()
    #args.funct_getlogon(args)
    



    
    
    main()