#!/usr/bin/env python3 


import os 
import subprocess

import re

# Make a copy of my env
my_env = os.environ.copy()

# Alter that copy
my_env["PATH"] = os.pathsep.join(["/opt/myapp/", my_env["PATH"]])

# Run a subprocess with that env 
result = subprocess.run(['env'], env=my_env, capture_output=True)



result2=(re.search(r"(PATH)", result.stdout.decode()))
#print(result2.group())

print(result2[1])

## Try setting the timeout variable - so process gets killed if it hangs
result = subprocess.run(['sleep','2'], env=my_env, capture_output=True, timeout=10)
# Nice  - now how do you do error handling again?


result = subprocess.run(['pwd'], env=my_env, capture_output=True, cwd='/tmp' )
print(result.stdout)


subprocess.run()