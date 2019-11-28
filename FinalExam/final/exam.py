# Task 1
# ----------------------------------------
# line 31,34: Documentation is written in a wrong format,
# should be:
def Do_Eget(donec, arg):
    """
    Do_Eget returns lorem ipsum... (up to 72 chars in a line)
    elit. Aenean egestas...
    """

# line 34: Function name (not really the mistake, but may be a reason
# of choosing better naming convention).  Also it is very
# non-descriptive.

# line 35,36: imports not at the very top of the file, should be:
# ASSUMING this line to be the first above the file top...
import os
import sys

# line 38: comment is too far from the code line (should be 2 spaces)

# line 41: uniform usage of indentation for subsections is required

# line 44: spaces around the assign operator should be present

# line 48: too many spaces, and same as for line 41

# line 56: too long line, keyworded comparison is prefered

# line 57: same as line 44

# line 68: no single space after comma in arguments list

# line 78: unnecessary spaces around parameters

# line 83: same as line 78, single quoted strings are prefered



# Task 2
# ----------------------------------------
def yields():
    try:
        c = 1
        b = 0
        if not c == (not b):
            yield 0
        else:
            1/0
            yield 0
        try:
            yield 0
        except ZeroDivisionError:
            yield 0
            raise IOError
            yield 0
        except:
            yield 0
        yield 0
    except Exception:
        try:
            1/0
        except ZeroDivisionError:
            yield 1
        yield 2
    except:
        yield 0
    yield 3 or (yield 0)
    try:
        x = 1
        yield 4
    finally:
        return (yield 5)
    yield 0


print(list(yields()))



# Task 3
# ----------------------------------------
class Ranger:
    def __init__(self, first, last, step):
        # Assume this limitations of the interface
        assert first is not None and len(first) == 1
        assert last is not None and len(last) == 1
        assert step is not None and step > 0

        self._first = first
        self._last = last
        self._step = step

    def __iter__(self):
        self._cur_asc = self._first
        self._cur_des = self._last

        return self

    def _increment(s, step):
        return chr(ord(s) + step)

    def __next__(self):
        first = self._first
        last = self._last
        step = self._step
        cur_asc = self._cur_asc
        cur_des = self._cur_des

        if (cur_asc > last or cur_des < first):
            raise StopIteration

        result = cur_asc + cur_des
        self._cur_asc = Ranger._increment(cur_asc, step)
        self._cur_des = Ranger._increment(cur_des, -step)

        return result


for ll in Ranger('a', 'g', step=2):
    print(ll)



# Task 4
# ----------------------------------------
# ASSUMING this line to be the first above the file top...
from functools import reduce
res = (
    reduce(lambda x, y: x + y,
        filter(lambda n: n > -10 and n < -2,
            map(lambda n: n - n* 2,
                [i for i in range(4, 16 + 1, 2)])))
    + 18)

print(res)



# Task 5
# ----------------------------------------
# ASSUMING this line to be the first above the file top...
import datetime

class BlockDivByZero:
    def __init__(self, description, log_path):
        self._desc = description
        self._log_path = log_path

    def __enter__(self):
        self._file = open(self._log_path, 'a')
        print('Enter..')

    def __exit__(self, type, value, traceback):
        file = self._file

        if type is not None:
            msg = 'Error: ' + self._desc + ', line ' + str()
            print(msg)
            timestamp = datetime.datetime.now()
            file.write('[' + str(timestamp) + '] ' + msg + '\n')

        file.close()
        print('Exit..')
        return True


with BlockDivByZero("division by zero", "report.txt"):
    print("Let's try")
    x = 1/0
    print("Unreachable")
print("Reachable")
