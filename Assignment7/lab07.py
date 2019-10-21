### Python Programming for Software Engineers
### Assignment 7
### 'Lambda De Parser'
###   Eugene Zuev, Tim Fayz
###   Special thanks to Ivan Tkachenko

# Denis Chernikov

# Task 1
# ----------------------------------------------
# Given the following:
f = lambda x, y: x * y

# 1. Rewrite to its logical equivalence using ordinary funcion definition(s)
# ANSWER: --------------------------------------
def f(x, y):
    return x * y


# Task 2
# ----------------------------------------------
# Given the following:
f = lambda x: (lambda y: (lambda z: x + y + z))

# 1. How would you call it to get the result of `x + y + z`?
# ANSWER: --------------------------------------
x, y, z = 1, 2, 3  # for the code to be able to execute
f(x)(y)(z)

# 2. Rewrite it using only one lambda expression and show how to call it
# ANSWER: --------------------------------------
f = lambda x, y, z: x + y + z
f(x, y, z)


# Task 3
# ----------------------------------------------
# Given the following:
(lambda b = (lambda *c: print(c)): b("a", "b"))()

# 1. What happens here? Rewrite it so that the code can be
# understood by a normal or your mate who has no idea what the lambda is!
# Provide comments, neat formatting and a bit more meaningful var names.

# ANSWER: --------------------------------------

def printArgsAsTuple(*args):
    '''
    Print all arguments provided to the stdout as being tied by a tuple.
    Used as default for an argument of the `callWithTwoStrings` function.
    '''
    print(args)


def callWithTwoStrings(func = printArgsAsTuple):
    '''
    Call `func` with arguments `"a"` and `"b"`.
    By default, argument `func` is `printArgsAsTuple` function object.
    '''
    first_string = 'a'
    second_string = 'b'
    func(first_string, second_string)


# `callWithTwoStrings` is called with default argument equal to `printArgsAsTuple`.
# It just prints strings hardcoded in it as placed in a tuple object (variadic arguments).
# `('a', 'b')`
callWithTwoStrings()


# Task 4 (soft)
# ----------------------------------------------
# What are the main restrictions on the lambda?
# Provide "If yes, why? If not, why not?" for each of the following:
# 1. Does lambda restrict side effects?
# 2. Does lambda restrict number of allowed statements?
# 3. Does lambda restrict assignments?
# 4. Does lambda restrict number of return values?
# 5. Does lambda restrict the use of default arguments values?
# 6. Does lambda restrict possible function signatures?

# ANSWERS: -------------------------------------

# 1. No. But it really depends on the definition of side effect.
#    If we'll consider any change of data not belonging to the functor context,
#    then it is really allowed in lambda through calls to other functions
#    making side effects, like `print`.
#>>> lambda: print('Hello, world!')

# 2. Yes. It is 0. By grammar definition of the language, only expressions are
#    allowed to be a body of a lambda expression.
#>>> lambda: return 1  # WRONG!
#>>> lambda: if True: 1 else: 2  # WRONG!
#>>> lambda: 1 if True else 2  # OK, since this is an expression
#>>> lambda: print('Hello!'); print('Bye-Bye!')  # OK, but `;` ends a statement enclosing lambda

# 3. Yes. This is implied by the rule of only expressions to be a body of a
#    lambda expression, which is not the case of any of the assignment statements.
#>>> s = ''
#>>> lambda: s = 'Hello, world!'  # WRONG!

# 4. Yes. It is 1. By grammar definition, lambda body should consist of a single
#    expression. This implies a single return value. But we can overcome it using
#    data structures like tuples.
#>>> lambda: 1  # only one return expression
#>>> lambda: 1; 2  # `2` is not a part of the lambda
#>>> lambda: 1, 2  # this is the tuple of the functor and the integer
#>>> lambda: (1, 2)  # this is one of the ways of handling multiple returns through a data structure

# 5. No. Default arguments' usage rules are exactly the same as for the ordinary
#    function statements.
#>>> lambda x=1: x ** x
#>>> lambda y=lambda z=lambda: 1: z() + 1: y() + 2
#>>> l = lambda a, b=1, c=2: a + b / c  # may be called like `l(0, c=32, b=64)`

# 6. No. Rules of signature definitions of lambda expressions are exactly the same
#    as for the ordinary function statements.
#>>> lambda a, b='c', *d, **e: print(a, b, c, d, e)


# Task 5
# ----------------------------------------------
# Given the following:
(lambda f = (lambda a: (lambda b: print(list(map(lambda x: x+x, a+b))))):
f((1,2,3))((4,5,6)))()

# 1. What happens here? Do the same as in Task 3 and
# enumerate order of execution using (1,2,3...) in comments

# ANSWER: --------------------------------------

def concatAndTwiceAndPrintList(a):
    '''
    Returns a function that sums an argument `a` with it's own argument `b`,
    twices each element of the result and prints it as a list.
    Suitable for carrying.
    '''
    def concatAndTwiceAndPrintList2(b):
        '''
        Sums an argument `a` from the outer scope with an argument `b`,
        twices each element of the result and prints it as a list.
        '''
        def twice(x):
            '''
            Return a twiced argument `x` (added to itself).
            '''
            return x + x  # 8

        concatenated = a + b  # 6
        generator = map(twice, concatenated)  # 7
        mapping_result_as_list = list(generator)  # 9
        print(mapping_result_as_list)  # 10

    return concatAndTwiceAndPrintList2  # 5


def callWithTwoTuples(func=concatAndTwiceAndPrintList):
    '''
    Call carried `func` with two tuples as arguments: `(1,2,3)` and `(4,5,6)`.
    By default, argument `func` is `concatAndTwiceAndPrintList` function object.
    '''
    first_tuple = (1, 2, 3)  # 2
    second_tuple = (4, 5, 6)  # 3
    func(first_tuple)(second_tuple)  # 4


# `callWithTwoTuples` is called with default argument equal to `concatAndTwiceAndPrintList`.
# It calls carried function with two tuples of three integers each, concatenates them,
# twices each number and prints the resulting sequence as a list.
# `[2, 4, 6, 8, 10, 12]`
callWithTwoTuples()  # 1


# 2. Why does map() requires list() call?
# ANSWER: --------------------------------------
# Map is implemented (under the hood) just like any other generator.
# It returns an object which has a method `__next__` returning a next element of the sequence.
# But function `print` is not expecting a generator. It will print it's raw representation.
# And the actual expected behavior is to see what is the result of mapping.
# Finally, `list` datatype constructor may have an iterable as it's argument.
# This allows us to successfully convert a result of a `map` call to look like a usual list.
