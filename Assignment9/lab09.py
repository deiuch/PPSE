### Python Programming for Software Engineers
### Assignment 9
### 'While Iterating Iterable Iterator'
###   Eugene Zuev, Tim Fayz

# Task 1
# ----------------------------------------------
# list comprehension
squares1 = [n * n for n in range(100)]
# parenthesized generator expression
squares2 = (n * n for n in range(100))

print(list(squares1))
print(list(squares2))

# 1. Both produce the same results. What's the difference?
# ANSWER: --------------------------------------
# `squares1' is already the list, and there's no need to construct a list out
# of it.  Just some unnecessary copying.

# 2. Seems like I don't really need to use list() for `square1`. Why?
# ANSWER: --------------------------------------
# List comprehension expression is equivalent to placing a generator expression
# into the constructor of a `list'.  Therefore, variable `squares1' is already
# pointing to a list object.

# 3. Show the memory usage for `square1` and `square2`.
# ANSWER: --------------------------------------
import sys
print('Memory usage of `squares1`:',
      sys.getsizeof([n * n for n in range(100)]) + sys.getsizeof(list(squares1)))
# Memory usage of `squares1`: 968
print('Memory usage of `squares2`:',
      sys.getsizeof((n * n for n in range(100))) + sys.getsizeof(list(squares2)))
# Memory usage of `squares1`: 100

# 4. Show the number of calls required to produce both lists.
# ANSWER: --------------------------------------
import profile
profile.run('list([n * n for n in range(100)])')  # 5 function calls...
profile.run('list((n * n for n in range(100)))')  # 105 function calls...
# (difference should be significant)


# Task 2
# ----------------------------------------------
# Using `while True`, next() and try/except block "re-implement" for loop
# ANSWER: --------------------------------------
def _for(iterable):
    g = iterable if hasattr(iterable, '__next__') else (e for e in iterable)
    try:
        while True:
            print(next(g))
    except StopIteration:
        pass


squares1 = [n * n for n in range(100)]
squares2 = (n * n for n in range(100))

# both have to produce the same output where each prints out all the numbers
_for(squares1)
_for(squares2)


# Task 3 (almost for free)
# ----------------------------------------------
# Absolutely bright example courteously adapted from PEP 255:
def f():
    try:
        yield 1
        try:
            yield 2
            1/0
            yield 0
        except ZeroDivisionError:
            yield 3
            raise
            yield 0
        except:
            yield 0
        yield 0
    except:
        yield 4
    yield 5
    try:
        x = 1  # should be 6, but will not be printed
    finally:
       yield 6
    yield 7

print(list(f()))
# [1, 1, 1, 1, 1, 1, 1]

# (being honest with yourself,
#  without looking at aforementioned PEP, and
#  without using Python interpreter)
# Rewrite numbers according to execution order just using your brain.
# For unreachable yields use 0 instead of 1.
# Wrong answers will not be degraded (only lack of *any* answer).

# Seems like the execution context stored between each next(f()) call.
# Could you kindly shed a light on the place where the context is stored?
# ANSWER: --------------------------------------
# Executing `f()', where `f' is a generator fabric (for instance, generator
# function), we get an object of type `generator', which contains all the
# information abut the state of the generator.


# Task 4
# ----------------------------------------------
# For a given function:
def fn():
    return 1 + (yield 2)

print(next(fn()))
print(next(fn()))

# Explain why this function works and always produces 2?
# ANSWER: --------------------------------------
# `fn()` is creating a generator object, `next(fn())` takes the first element
# of this generator, which is taken from the `yield 2` expression.
# In the second print statement, we create the new generator object, which has
# it's own independent state, and `fn' is executed from the beginning.

# Is it possible to produce 3? If yes, why? If it isn't, why?
# ANSWER: --------------------------------------
# It is possible since `yield' used as an expression is returning an object that
# was passed to the `send' method of the generator.
# This is an example assuming that used Python implementation allows an expression
# in a return statement, and that it will be returned as a consequent element
# (not CPython case):
#>>> g = fn()
#>>> two = next(g)
#>>> three = g.send(two)
#>>> print(three)  # 3
# For CPython, `return' places it's expression into the `StopIteration' raised
# at the end of the generator execution.
#>>> g = fn()
#>>> two = next(g)
#>>> try:
#>>>     three = g.send(two)
#>>> except StopIteration as e:
#>>>     print(e)  # 3


# Task 5
# ----------------------------------------------
# Why starting from Python 2.5 yield became available inside try/finally block?
# Or (if you prefer) put it other way around -- why was it forbidden there?

# ANSWER: --------------------------------------
# Before Python 2.5, authors of the language was aware of the possibility of the
# generator to not be continued from the `yield` inside the `try' clause of the
# try/finally statement since generator is not obligated to continue the execution
# till the end.  This created a "hole" where the `finally' clause that is required
# to execute on any exit of try/finally will not be actually executed.
# In 2.5, generators have got a new method `close()`, which helps to overcome this
# issue.

# Where to start?! I guess here: https://docs.python.org/2.5/ref/yield.html


# References
# ----------------------------------------------
# https://www.python.org/dev/peps/pep-0255/
# https://www.python.org/dev/peps/pep-0234/
