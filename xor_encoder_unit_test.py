import unittest
import xor_encoder

class TestStandardEncode(unittest.TestCase):
    def test_function_encode(self):
        """
        Test calling the encode function directly
        """
        decoded_text ='WebAs'
        encoded_text='{xor}CDo9Hiw=' ## Should I include the new line?? 
        result = xor_encoder.xor_encode(decoded_text) 
        
        self.assertEqual(encoded_text, result)
    
    
    def test_function_decode(self):  
        """
        Test calling the denode function directly
        """     
        decoded_text ='WebAs'
        encoded_text='{xor}CDo9Hiw=' ## Should I include the new line?? 
        

        result = xor_encoder.xor_decode(encoded_text) 
        
        self.assertEqual(decoded_text, result)

    def test_script_encode(self):       
        """
        Test calling the script using the --encode option
        """
        decoded_text ='WebAs'
        encoded_text='{xor}CDo9Hiw=' ## Should I include the new line?? 

        import subprocess

        cmd='./xor_encoder.py --input-text "' + decoded_text + '" --encode'
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = p.communicate() 
        result=out.decode('ascii').rstrip()

        self.assertEqual(encoded_text, result)

    def test_script_decode(self):       
        """
        Test calling the script using the --encode option
        """
        decoded_text ='WebAs'
        encoded_text='{xor}CDo9Hiw=' ## Should I include the new line?? 

        import subprocess

        cmd='./xor_encoder.py --input-text "' + encoded_text + '" --decode'
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = p.communicate() 
        result=out.decode('ascii').rstrip()

        self.assertEqual(decoded_text, result)
        
    def test_script_invalid_base64_decode(self):       
        """
        Test calling the script using the --decode option with invalid data
        """
        decoded_text ='WebAs'
        invalid_base64=decoded_text
        encoded_text='{xor}CDo9Hiw=' ## Should I include the new line?? 

        import subprocess

        cmd='./xor_encoder.py --input-text "' + invalid_base64 + '" --decode'
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE)
        out, err = p.communicate() 
        result=out.decode('ascii').rstrip()

        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(err.decode('ascii').rstrip(), 'Unable to decode the input string. Is it valid base64?')

    def test_script_invalid_encode_and_decode_option(self):       
        """
        Test calling the script using the --decode option with invalid data
        """
        decoded_text ='WebAs'
        invalid_base64=decoded_text
        encoded_text='{xor}CDo9Hiw=' ## Should I include the new line?? 

        import subprocess

        cmd='./xor_encoder.py --input-text "' + invalid_base64 + '" --decode --encode'
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE)
        out, err = p.communicate() 
        result=out.decode('ascii').rstrip()

        self.assertNotEqual(p.returncode, 0)
       
unittest.main()


#argv1 = ['--input-text', "WebAs", "--encode"]
#result = xor_encoder.main() 
#import subprocess
#cmd='./xor_encoder.py --input-text "WebAs" --encode'
#p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
#out, err = p.communicate() 
#result=out.decode('ascii')

#print(str(result))

