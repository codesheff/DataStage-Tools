#!/usr/bin/env python3 


def xor_encode(secret_text):
    """
    Encode text to the xor encoding used by WAS
    """
    import base64

    # Create a byte array, containing the characters xor'ed with underscore
    xor_byte_array=bytearray([])
    for char in secret_text:
        decimalOfChar=ord(char)
        decimalOfUnderScore=ord('_')

        xor_value = decimalOfChar ^ decimalOfUnderScore
        xor_byte_array.append(xor_value)
   
    ## use base64 to encode it, and then decode those bytes as ascii  
    encoded_secret_text='{xor}' + base64.encodebytes(xor_byte_array).decode('ascii').rstrip()
       
    return encoded_secret_text

def xor_decode(encoded_text):
    """
    Decode xor encoded text
    """
    import base64
    
    #remove initial {xor} if it exists
    if encoded_text[0:5].lower() == '{xor}':
        encoded_text = encoded_text[5:]

    
    #Convert to bytes, and then pass to base64.decodebytes
    try:
        decoded_bytes = base64.decodebytes(bytes(encoded_text, 'ascii'))
    except:
        import sys
        sys.exit("Unable to decode the input string. Is it valid base64?") 
    

    ## Now do the xor with the underscore on each byte
    decoded_text_byte_array=bytearray([])
    decimalOfUnderScore=ord('_')
    for byte in decoded_bytes:
        xored_byte = byte ^ decimalOfUnderScore
        decoded_text_byte_array.append(xored_byte)

    ## convert the bytes to string using ascii
    return decoded_text_byte_array.decode('ascii').rstrip()

    
def HandleInputParameters():

    import os
    import argparse
    # To read, and look at mutually exclusive arrgs  https://linuxconfig.org/how-to-use-argparse-to-parse-python-scripts-parameters
    
    # Create top level parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-text", type=str, dest="input_text", help="The string to be encoded or decoded", required=True) # Setting all to false here as it's making testing easier
    
    mutually_exclusive = parser.add_mutually_exclusive_group()
    mutually_exclusive.add_argument("--encode", action="store_const", const='encode', help="Encode the supplied string", required=False) # Setting all to false here as it's making testing easier
    mutually_exclusive.add_argument("--decode", action="store_const", const='decode', help="Decode the supplied string", required=False) # Setting all to false here as it's making testing easier
    
 
    return parser
    


def main():
    
    parser=HandleInputParameters()
    global args 
    args = parser.parse_args()
    import sys

    ## if --encode option passed in, encode the text
    if args.encode == 'encode':
        print(xor_encode( args.input_text) )
    elif args.decode == 'decode':
        print(xor_decode( args.input_text) )
    else:
        sys.exit("\n Unhandled request.\n") 


if __name__=="__main__":
    main()
