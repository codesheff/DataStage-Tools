#!/usr/bin/env python3

def my_decorator(func):
    """
    Decorator Function
    """

    def wrapper():
        """
        Return String F-I-B_O-N-A-C-C-I
        """

        # Do something before
        #result= func()
        # Do something after\
        return "F-I-B_O-N-A-C-C-I"
    
    return wrapper



def pfib():
    """
    Return Fibanacci
    """

    return 'Fibanacci'



print('Using normal function')
print(pfib())


print('Assign function to be the return of my_decorator')
pfib = my_decorator(pfib)
print(pfib())


print('Do the same, but with the decorator syntax')

@my_decorator
def pfib():
    """
    Return Fibanacci
    """

    return 'Fibanacci'

print(pfib())
print(pfib)
