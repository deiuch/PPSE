'''
Author: Denis Chernikov, B16-SE-01, Innopolis University
Python 3.7.2
'''

from reflect import reflect


@reflect
def foo(bar1, bar2=""):
    """
    This function does nothing useful
    :param bar1: description
    :param bar2: description
    """
    print("some\nmultiline\noutput")


print('Example of usage of the decorator `reflect`')
print()
foo(None, bar2="")
