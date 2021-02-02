#!/usr/bin/env python3

import unittest

import datastage_functions




class TestGetDSAdminNames(unittest.TestCase):
    def test_correct_version_xml(self):

        """
        Environment variables: unset   
        Args : default names
        """
       
        version_xml='/iis/01/InformationServer/Version.xml'
        admin_name='dsadm'
        self.assertEqual(datastage_functions.GetDSAdminName(version_xml), admin_name)
        

class TestGetProjectPath(unittest.TestCase):
    def test_existing_project(self):

        version_xml='/iis/01/InformationServer/Version.xml'
        dshome='/iis/test/InformationServer/Server/DSEngine'
        dsadm_user='dsadm'
        project='dstage1'
        expected_path='/iis/01/InformationServer/Server/Projects/dstage1'

        self.assertEqual(datastage_functions.GetProjectPath(project_name='dstage1',dsadm_user='dsadm', dshome='/iis/01/InformationServer/Server/DSEngine'), expected_path)



if __name__ == '__main__':
    # begin the unittest.main()
    import sys
    scriptname=sys.argv[0]
    sys.argv=[''] 
    sys.argv[0]=scriptname
    unittest.main()