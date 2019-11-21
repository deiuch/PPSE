### Python Programming for Software Engineers
### Assignment 10
### '(Anniversary) Inverse of Assignment 10'
###   Eugene Zuev, Tim Fayz

# Here is your story:
# It is 2005. Recently, you've got your dream job offer from one of the
# best "Big Five" tech company. More than that, you've been immediately
# accepted as a Lead Developer! Isn't it cool..huh? BUT! Here is the
# trick.. Your manager (as it turns out after a month of normal
# operation) is a real pro butt! The story doesn't tell us if he was a
# Lead Developer too. What we know, however, is that he is most certainly
# the one who had been doing "mission critical tasks" at the very
# beggining of the company. He [as our course suggests] loves Python more
# than his wife and always keep in touch with the latest news stories.
# [btw...the reason he gave up his original job is a decision to stop
# h***ing his own brain and let others do that instead. Maybe he tired in
# general or that's a priority change. Nobody knows now...] So now, on
# the same cool Reddit channel he once heard there is an upcoming PEP 343
# that introduces a "with" statement. "What's THAT, man!?" -- he
# wondered. The old pro immediately realizes whatever it is he wants it
# to be integrated as a "new great technology" [but yet keeping his own
# hands clean]. So the choice WHO will teach others to use this statement
# (and adopt it into an existing code base) fell on YOU. [That may sound
# strange] but now he wants you to prepare a set of tasks to be sure that
# the aforementioned PEP 343 was read, consumed and understood by all
# department developers. As an example -- how these all should look like
# -- the old pro referenced back to well-known assignments 7 till 9.
# Moreover, he decided to entitle most of the tasks to mix his own
# intentions. As it turns out (again) he is a sly one. Our pro butt wants
# a "special edition" of your working where all the answers are given in
# advance! [most probably to "save" his time of doing it by hands; which
# is a bad idea anyway...] As you may guess, he set up a deadline ['cause
# you know...he is a manager] that you are supposed to meet! It's Nov 21,
# 10:35AM [just in case you have forgotten.] He absolutely can't keep his
# patience of waiting for your tasks! And the ultimate moment where he
# will proudly spread them over the department uttering "This is how we
# stay on cutting-edge!"
# End of the story.
# You can begin now...


# Introduction (an abstract)
# ----------------------------------------------
def file_example():
    with open('cool_file_name.format') as my_file:
        my_file.write('Hello, world!')
    pass  # No need to close the file, it will not be accessible since this line


def iostream_example():
    # from contextlib import redirect_stdout
    # from io import StringIO
    my_stdout = StringIO()
    with redirect_stdout(my_stdout):
        print('Hello, world!')
    pass  # Here `my_stdout` will contain the string 'Hello, world!', and nothing will go to the stdio


def combined_example():
    # from contextlib import redirect_stdout
    with open('my.log') as log_file, redirect_stdout(log_file):
        print('16:34:50 - printed this log')
    pass  # All the `print`ed text will go to the file `my.log`


# Task 1 (demonstrates the benefits of using with)
# ----------------------------------------------
# Write the analog of the `with` statement in terms of `try` statement.
# Describe the benefits that you're getting out of using `with`.
# ANSWER: --------------------------------------

# Instead of this context manager some existing may be used
class MyCoolContextManager:
    def __enter__(self):
        pass

    def __exit__(self):
        pass


__mng = MyCoolResource()
__resource = __mng.__enter__()
# `with` allows us to not write this terrible `try/finally` guards
try:
    pass  # some actions with this resource
finally:
    __mng.__exit__(__resource)  # this will happen in any case


# Task 2 (demonstrates how to use several nested with's)
# ----------------------------------------------
# Give an example of nested `with` statements. Try to optimize this using
# only one `with` statement. See the syntax description of the `with`
# statement.
# ANSWER: --------------------------------------
from io import StringIO

with StringIO() as my_stdout:
    with redirect_stdout(my_stdout):
        print('Hellom world!')

with StringIO() as my_stdout, redirect_stdout(my_stdout):
    print('Hellom world!')


# Task 3 (demonstrates how to create your own context manager)
# ----------------------------------------------
# Statement `with` is using some special methods to manage the resource.
# Implement a class that will reflect this methods and will be suitable
# for use in the `with` statement. Search `Context Manager` for details.
# ANSWER: --------------------------------------
class MyCoolResource:
    def close(self):
        pass


class MyCoolContextManager2:
    def __enter__(self):
        return MyCoolResource()

    def __exit__(self, resource):
        resource.close()


# Task 4 (demonstrates exception handling)
# ----------------------------------------------
# Provide a couple of examples showing what happens if an exception will
# occur before the end of using of some resource. The first example
# should NOT use the `with` statement, but the second should. Totally,
# this examples should show the difference between the cases where you
# do not take care of deallocation for ALL cases (just start using and
# then end using), and where you use some smart language mechanics.
# ANSWER: --------------------------------------
def exception_example1():
    f = open('abcde.txt')
    f.write('Heeey!')
    raise RuntimeError()  # oops! File will stay open...
    f.close()


def exception_example2():
    with open('fghij.txt') as f:
        f.write('Heeey!')
        raise RuntimeError()  # File will be definitely closed


# Task 5 (your own)
# ----------------------------------------------
# Reconstruct your own Context Manager like `redirect_stdout`, but which
# should take a path to the file, open it and write all the text given
# to the `print` function to this file, and at the end closes this file.
# P.S.: be honest and do not look at the original implementation from
# the library :D
# ANSWER: --------------------------------------
class MyCoolLogger:
    def __enter__(self, path):
        # return self.file := open(path)
        self.file = open(path)
        return self.file

    def __exit__(self):
        self.file.close()
