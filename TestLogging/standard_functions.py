#!/usr/bin/env python3 
    
def getFunctionNames():
    
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