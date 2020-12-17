#!/usr/bin/env python3

import argparse
import getpass

def parse_args_login():
    parser = argparse.ArgumentParser(description="login")
    parser.set_defaults(funct=argparser_credentialhandler)
    
    # Login
    
    parser.add_argument('-u', dest='user', help='user.  If this argument is not passed it will be requested.')
    parser.add_argument('-p', dest='password', help='password.  If this argument is not passed it will be requested.')

    
    args, unknown = parser.parse_known_args() # use 'unknown' to handle unrecognised args

    print(args.user)
    args.funct(args)

    return args

def parse_args_normal():
    parser = argparse.ArgumentParser(description="normal")
    #parser.set_defaults(funct=argparser_handler)
    
    #--hostName
    parser.add_argument("--hostName", type=str, dest="hostName", help="The hostName of the DataStage engine. e.g HN01 ", default='HN01', required=True) # Setting all to false here as it's making testing easier
    parser.add_argument("--project-name", type=str, dest="project_list", help="project to compile jobs in ", required=True)
    parser.add_argument("--jobName", action='append', type=str, dest="job_list", help="jobs to compile", required=True)

    args = parser.parse_args()
    #args.funct(args)

    return args

def argparser_credentialhandler(args):
    args.user, args.password = login(args.user, args.password)
    print('Hi')


def login(user, password):
    if not user:
        user = input("User:") 
    if not password:
        password = getpass.getpass()    
    print("user:", user)
    print("password:", password)
    return user,password


def main():
    print('User name is : ' + login_args.user)
    print('Password  is : ' + login_args.password)
    pass


if __name__ == '__main__':
    login_args = parse_args_login()
    
    args2 = parse_args_normal()
    

    main()