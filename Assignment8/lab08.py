### Python Programming for Software Engineers
### Assignment 8
### 'Happy PEPer'
###   Eugene Zuev, Tim Fayz


# Denis Chernikov


# Task 1 (0 points)
# ----------------------------------------------
# Read funny PEP20 (The Zen of Python)


# 1. If you had to chose only one rule which one you would prefer?
# ANSWER: --------------------------------------
# The 20th one :D
# But better one is (probably):
# There should be one-- and preferably only one --obvious way to do it.


# Task 2-5 (10 points)
# ----------------------------------------------
# Read PEP08 (Style Guide for Python Code)


# 1. What's the reason to limit all the lines to 72-79 characters long?
# ANSWER: --------------------------------------
# This is because the width of the text field of the editor may be
# different, and not always as long as your screen.  This length is the
# most optimal  for having a room for code and still being able to see
# the whole line inside the window without horizontal scrolling or text
# wrapping.  It is important for old screens, exotic text editors, or
# cases when there are several text fields open side-by-side, like when
# more than one file is open, or file history with differences between
# time stemps is reviewed, etc.

# 1.1 Em..sorry, I forgot! What are 72 and 79 lengths exactly for?
# ANSWER: --------------------------------------
# 72 is for non-code entities like comments, doc-strings, etc.
# 79 is for other cases.


# 2. How would you reformat this according to PEP08?
# Well..do I really need a backslash somewhere here?
# ANSWER: --------------------------------------
# No. :D


def stupid_function_written_by_someone(
        argument_one, argument_two,
        keywordarg_one="1", keywordarg_two="2",
        **something_else):
    pass


# 2.1 Could you provide a code example where the backslash is needed?
# (do not copy paste from PEP itself, ok? - that's forbiden)
# ANSWER: --------------------------------------
assert 12345678901234567890123456789 != 98765432109876543210987654321, \
    'Some strange integers that were supposed to be not equal ARE equal'


# (From now on, stick to 79.  Reformat all the rest.  And please, do not
# make it manually!  One would expect you to simply use IDE feature or
# plugin)


# 3. Is that correct according to PEP08?
# Restructure if necessary.


def func_1(args):
    pass


class Class1():
    pass


def func_2(args):
    pass


class Class2():
    pass


# 4. What's wrong here?
# Restructure if necessary.
# ANSWER: --------------------------------------
# Assuming the line with this comment to be above the first in the file
import os
import subprocess
import sys

# 4.1 Can I import modules somewhere in the middle? Is it good as for PEP08?
# ANSWER: --------------------------------------
# You can import in the middle.  But PEP8 restricts a place and order of
# imports in the program.  Imports should be placed at the top of the
# file grouped accroding to their rules.

# 4.2 Is it good to do this? If it isn't, why not?
from os import *
# ANSWER: --------------------------------------
# *Assuming this code example is placed at the top of a file.*
# It is bad according to PEP8.
# This construct imports an implicit list of symbols, which makes it not
# obvious and inconsistent which names are actually included and which
# of them are really used or thought to be used, but actually not.

# 4.3 What is relative and absolute imports? Which one is preferred and why?
# ANSWER: --------------------------------------
# Relative imports are the import constructs with an imported entity
# denoted starting with dot, which means that it should be searched
# across the siblings of a current module.  Absolute imports are the
# ones describing an importing entity through the import system
# configured ways.
#
# It is preferred to use absolute imports due to better readability and
# better behaving (less dependent on how the import system works).


# 5. Can I use non-latin identifiers according to PEP08? Does it run btw?
имя_пользователя = "John"
user_name = "John"
# ANSWER: --------------------------------------
# By PEP8, you are not restricted in a set of characters allowed in an
# identifier except by the set of language restrictions, unless you are
# writing a code for the Python standard library, which forces ASCII to
# be used.  The same policy is recommended for open source projects with
# a global audience.
#
# This code should run, assuming file encoding is recognized as UTF-8.


# 6. What's the matter here?
# Restructure according to PEP08.
play_on_numbers = (11229065982633
                   - 11229065982633
                   + 11229065982633 * 11229065982633 / (11229065982633 // 5)
                   + 11229065982633)


# 7. What's wrong here? Fix it according to PEP08.


def counter(start, step=10, end=100) -> int:
    print(start)
    if start >= end:
        return 100
    return counter(start + step, step)


# 8. Is it well-formed comment? Reformat accroding to PEP08


def func():
    """
    This comment doesn't mean anything Nick. But still there is some
    hidden, insidious trick! Please, just make it more thick!
    """
    pass


# 9. Which is preferable?


def func(a): return a * a  # 1 or


func = lambda a: a*a # 2
# ANSWER: --------------------------------------
# 1 is preferable.

# 9.1 Why?
# ANSWER: --------------------------------------
# At least for traceback printing, where you will get a function name
# instead of pure `<lambda>`.


# 10. Accordign to section:
# https://www.python.org/dev/peps/pep-0008/#naming-conventions

# 10.1 Which naming style would you prefer and why?
# (eg CamelCase or lowercase or mixedCase etc)
# ANSWER: --------------------------------------
# Personally, I prefer CamelCase due to it's readability and
# consistency in upper case usage.

# 10.2 Which var name of these two would you choose
# being stuck to CamelCase as your primary naming style?
# NFSReader or NfsReader?
# ANSWER: --------------------------------------
# `NFSReader`. It is stated in PEP8 to preserve letter cases for
# acronyms.

# 10.3 Should somehow class and variable names differ?
# ANSWER: --------------------------------------
# Yes. By PEP8, the preferred naming style for classes is
# CapWords (CamelCase), but for variables it is lowercase with
# underscores.

# 10.4 Imagine we need, by some significant reason, to use var names
# that clash with Python keywords (say, 'class' and 'else').
# What can we do according to PEP08?


def foo():
    class_ = ''
    else_ = 0
    pass
