'''
Author: Denis Chernikov, B16-SE-01, Innopolis University
Python 3.7.2
'''

__all__ = ['reflect']

from collections import Counter
from contextlib import redirect_stdout
from enum import Enum
from inspect import signature as getsignature, getdoc, getsource
from io import StringIO, BytesIO
from os import linesep as os_linesep
from tokenize import tokenize, detect_encoding, NAME as t_name


class _PrintableAttributes(Enum):
    NAME = 'Name'
    TYPE = 'Type'
    SIGNATURE = 'Sign'
    ARGUMENTS = 'Args'
    DOC = 'Doc'
    COMPLEXITY = 'Complx'
    SOURCE = 'Source'
    OUTPUT = 'Output'


_ATTR_ENDING = ': '
_ATTR_INDENT_LEN = max(len(a.value) for a in _PrintableAttributes) + len(_ATTR_ENDING)
_ARGS_KIND_NAME_SEP = ' '
_POS_ARGS_PREFIX = 'positional'
_KEY_ARGS_PREFIX = 'key=worded'


def _indent_with(text, indent='    ', linesep=os_linesep):
    return linesep.join(indent + line for line in text.splitlines())


def _indent(text, indent_size=4, indent=' ', linesep=os_linesep):
    return _indent_with(text, indent * indent_size, linesep)


def _replace_beginning_with(new_beginning, text):
    return new_beginning + text[len(new_beginning):]


def _format_attr_content(attr, text):
    return _replace_beginning_with(
        attr.value + _ATTR_ENDING,
        _indent(text, _ATTR_INDENT_LEN),
    )


def _format_args(pos_args, key_args):
    return os_linesep.join([
        _ARGS_KIND_NAME_SEP.join([_POS_ARGS_PREFIX, str(pos_args)]),
        _ARGS_KIND_NAME_SEP.join([_KEY_ARGS_PREFIX, str(key_args)]),
    ])


def _get_complexity(src_code):
    to_count = 'print'
    encoding = detect_encoding((l.encode() for l in src_code.split(os_linesep, 1)).__next__)[0]

    with BytesIO(src_code.encode(encoding, 'ignore')) as src_stream:
        return dict(Counter(t[1] for t in tokenize(src_stream.readline)
            if t[0] is t_name and t[1] == to_count))


def _exec(func, pos_args, key_args):
    with StringIO() as my_stdout, redirect_stdout(my_stdout):
        return func(*pos_args, **key_args), my_stdout.getvalue()


#@reflect
def reflect(func):
    '''
    About `quine`...
    This is not exactly about quines.
    Because this kind of program (our decorator) should be able to print itself.
    And it cannot...
    '''
    assert callable(func)

    def print_reflected(*pos_args, **key_args):
        attr_content_getters = {
            _PrintableAttributes.NAME: lambda f: f.__name__,
            _PrintableAttributes.TYPE: lambda f: f.__class__,
            _PrintableAttributes.SIGNATURE: getsignature,
            _PrintableAttributes.ARGUMENTS: lambda _: _format_args(pos_args, key_args),
            _PrintableAttributes.DOC: getdoc,
            _PrintableAttributes.COMPLEXITY: lambda f: _get_complexity(
                attr_content_getters[_PrintableAttributes.SOURCE](f)
            ),
            _PrintableAttributes.SOURCE: getsource,
            _PrintableAttributes.OUTPUT: lambda f: _exec(f, pos_args, key_args)[1],
        }

        for attr in _PrintableAttributes:
            print(_format_attr_content(attr, str(attr_content_getters[attr](func))))

    return print_reflected


if __name__ == '__main__':
    # It is impossible for the `reflect` to reflect itself directly.
    # This is because the `reflect` decorator does not exist at the moment of usage on itself.
    # Forward declaration does not solve the problem because of how links on functions are stored in a decorator.
    #
    # Workarounds:
    # 1. Copy-paste `reflect` before itself.
    #    Not really a workaround, because it does not print ITSELF, but itself's COPY.
    # 2. Call `reflect` directly with itself as an argument
    #    Real ad-hoc workaround, because external means are used, but not the decorator syntax.

    reflect(reflect)(reflect)
