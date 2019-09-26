'''
Author: Denis Chernikov, B16-SE-01, Innopolis University
Python 3.7.2
'''

__all__ = [
    'stat_object',
    'stat_complexity',
]

# ------------------------------ REFLECT ------------------------------

from collections import Counter
from contextlib import redirect_stdout
from enum import Enum
from inspect import signature as getsignature, getdoc, getsource
from io import StringIO, BytesIO
from os import linesep as os_linesep
from tokenize import tokenize, detect_encoding, NAME as t_name

# ------------------------------ HALSTEAD ------------------------------

import ast
from collections import Counter
from enum import Enum
from functools import lru_cache, reduce
from math import log2
from os import linesep
from sys import argv, stdin
from tokenize import COMMENT as t_comment, tokenize

from inspect import getsourcefile


#######################################################################
# ------------------------------ REFLECT ------------------------------
#######################################################################


class _PrintableAttributes(Enum):
    NAME = 'Name'
    TYPE = 'Type'
    SIGNATURE = 'Sign'
    ARGUMENTS = 'Args'
    DOC = 'Doc'
    # COMPLEXITY = 'Complx'
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


def stat_object(func):
    assert callable(func)

    def reflect(*pos_args, **key_args):
        print({
            attr.value: {
                _PrintableAttributes.NAME: lambda f: f.__name__,
                _PrintableAttributes.TYPE: lambda f: f.__class__,
                _PrintableAttributes.SIGNATURE: getsignature,
                _PrintableAttributes.ARGUMENTS: lambda _: _format_args(pos_args, key_args),
                _PrintableAttributes.DOC: getdoc,
                # _PrintableAttributes.COMPLEXITY: lambda f: _get_complexity(
                #     attr_content_getters[_PrintableAttributes.SOURCE](f)
                # ),
                _PrintableAttributes.SOURCE: getsource,
                _PrintableAttributes.OUTPUT: lambda f: _exec(f, pos_args, key_args)[1],
            }[attr](func)
            for attr in _PrintableAttributes
        })

    return reflect


########################################################################
# ------------------------------ HALSTEAD ------------------------------
########################################################################


# XXX: changing anything here check if η_1 and η_2 in Halstead need changes
class _Countable(Enum):
    # Operators
    IF = 'if'
    ELIF = 'elif'
    ELSE = 'else'
    TRY = 'try'
    FOR = 'for'
    WITH = 'with'
    RETURN = 'return'
    DEF = 'def'
    IMPORT = 'import'
    EXCEPT = 'except'
    CALL = 'calls'
    ARITHMETIC = 'arithmetic'
    LOGIC = 'logic'
    ASSIGNMENT = 'assign'

    # Operands
    DOCSTRING = 'docstrings'
    COMMENT = 'inlinedocs'
    LITERAL = 'literals'
    ENTITY = 'entities'
    ARGUMENT = 'args'


_OPERATORS = [
    _Countable.IF,
    _Countable.ELIF,
    _Countable.ELSE,
    _Countable.TRY,
    _Countable.FOR,
    _Countable.WITH,
    _Countable.RETURN,
    _Countable.DEF,
    _Countable.IMPORT,
    _Countable.EXCEPT,
    _Countable.CALL,
    _Countable.ARITHMETIC,
    _Countable.LOGIC,
    _Countable.ASSIGNMENT,
]

_OPERANDS = [
    _Countable.DOCSTRING,
    _Countable.COMMENT,
    _Countable.LITERAL,
    _Countable.ENTITY,
    _Countable.ARGUMENT,
]


def _bytes_line_iterator(bs):
    for line in bs.splitlines(True):
        yield line

    while True:
        yield b''


class Halstead:
    def __init__(self, input_stream, filename='<unknown>'):
        self._counter = Counter()
        self.__extract_values(input_stream, filename)


    class __HalsteadNodeVisitor(ast.NodeVisitor):
        def __init__(self, halstead_obj):
            self._counter = halstead_obj._counter


        def __try_count_docstring(self, node):
            try:
                ast.get_docstring(node)
                self._counter[_Countable.DOCSTRING] += 1
            except TypeError:
                pass


        def visit_If(self, node, is_elif=False):
            self._counter[_Countable.ELIF if is_elif else _Countable.IF] += 1

            else_closure = node.orelse

            if len(else_closure) == 1 and type(else_closure[0]) is ast.If:
                self.visit(node.test)
                for n in node.body: self.visit(n)
                self.visit_If(else_closure[0], True)
            else:
                if len(else_closure):
                    self._counter[_Countable.ELSE] += 1

                self.generic_visit(node)


        def visit_IfExp(self, node):
            self._counter[_Countable.IF] += 1
            self._counter[_Countable.ELSE] += 1
            self.generic_visit(node)


        def visit_Try(self, node):
            self._counter[_Countable.TRY] += 1
            self.generic_visit(node)


        def visit_For(self, node):
            self._counter[_Countable.FOR] += 1
            self.generic_visit(node)


        def visit_AsyncFor(self, node):
            self.visit_For(node)


        def visit_ListComp(self, node):
            self.visit_For(node)


        def visit_SetComp(self, node):
            self.visit_For(node)


        def visit_DictComp(self, node):
            self.visit_For(node)


        def visit_GeneratorExp(self, node):
            self.visit_For(node)


        def visit_With(self, node):
            self._counter[_Countable.WITH] += 1
            self.generic_visit(node)


        def visit_AsyncWith(self, node):
            self.visit_With(node)


        def visit_Return(self, node):
            self._counter[_Countable.RETURN] += 1
            self.generic_visit(node)


        def visit_Import(self, node):
            self._counter[_Countable.IMPORT] += 1
            self.generic_visit(node)


        def visit_ImportFrom(self, node):
            self.visit_Import(node)


        def visit_ExceptHandler(self, node):
            self._counter[_Countable.EXCEPT] += 1
            self.generic_visit(node)


        def visit_BinOp(self, node):
            if type(node.op) in [ast.Add, ast.Sub, ast.Div, ast.Mult]:
                self._counter[_Countable.ARITHMETIC] += 1

            self.generic_visit(node)


        def visit_Compare(self, node):
            if len(node.ops) == 1 and type(node.ops[0]) in [ast.Eq, ast.NotEq]:
                self._counter[_Countable.LOGIC] += 1

            self.generic_visit(node)


        def visit_BoolOp(self, node):
            if type(node.op) is ast.And:
                self._counter[_Countable.LOGIC] += 1

            self.generic_visit(node)


        def visit_UnaryOp(self, node):
            if type(node.op) is ast.Not:
                self._counter[_Countable.LOGIC] += 1

            self.generic_visit(node)


        def visit_Module(self, node):
            self.__try_count_docstring(node)
            self.generic_visit(node)


        def visit_FunctionDef(self, node):
            self.__try_count_docstring(node)
            self._counter[_Countable.DEF] += 1
            self._counter[_Countable.ENTITY] += 1
            self.generic_visit(node)


        def visit_AsyncFunctionDef(self, node):
            self.visit_FunctionDef(node)


        def visit_ClassDef(self, node):
            self.visit_FunctionDef(node)


        def visit_Assign(self, node):
            self._counter[_Countable.ASSIGNMENT] += 1
            self._counter[_Countable.ENTITY] += 1
            self.generic_visit(node)


        # TODO: discuss
        # def visit_AugAssign(self, node):
        #     self.visit_Assign(node)


        def visit_AnnAssign(self, node):
            self.visit_Assign(node)


        def visit_Num(self, node):
            self._counter[_Countable.LITERAL] += 1
            self.generic_visit(node)


        def visit_Str(self, node):
            self.visit_Num(node)


        def visit_Bytes(self, node):
            self.visit_Str(node)


        def visit_JoinedStr(self, node):
            self.visit_Str(node)


        def visit_Call(self, node):
            self._counter[_Countable.CALL] += 1
            self._counter[_Countable.ARGUMENT] += len(node.args) + len(node.keywords)
            self.generic_visit(node)


        def visit_Index(self, node):
            self._counter[_Countable.ARGUMENT] += 1
            self.generic_visit(node)


        def visit_Slice(self, node):
            if node.lower:
                self._counter[_Countable.ARGUMENT] += 1
            if node.upper:
                self._counter[_Countable.ARGUMENT] += 1
            if node.step:
                self._counter[_Countable.ARGUMENT] += 1
            self.generic_visit(node)


    def __count_inline_comments(self, readline):
        for toknum, *_ in tokenize(readline):
            if toknum == t_comment:
                self._counter[_Countable.COMMENT] += 1


    def __extract_values(self, input_stream, filename):
        source = input_stream.read()

        Halstead.__HalsteadNodeVisitor(self).visit(ast.parse(source, filename))

        self.__count_inline_comments(_bytes_line_iterator(source).__next__)


    @lru_cache()
    def η_1(self):
        return 20  # TODO: calculate


    @lru_cache()
    def η_2(self):
        return len(_OPERANDS)


    def __sum_counters(self, keys):
        return reduce(lambda a, b: a + b, (self._counter[k] for k in keys))


    @lru_cache()
    def N_1(self):
        return self.__sum_counters(_OPERATORS)


    @lru_cache()
    def N_2(self):
        return self.__sum_counters(_OPERANDS)


    @lru_cache()
    def vocabulary(self):
        return self.η_1() + self.η_2()


    @lru_cache()
    def length(self):
        return self.N_1() + self.N_2()


    @lru_cache()
    def calc_length(self):
        η_1, η_2 = self.η_1(), self.η_2()
        return η_1 * log2(η_1) + η_2 * log2(η_2)


    @lru_cache()
    def volume(self):
        return self.length() * log2(self.vocabulary())


    @lru_cache()
    def difficulty(self):
        return self.η_1() / 2 * self.N_2() / self.η_2()


    @lru_cache()
    def effort(self):
        return self.difficulty() * self.volume()


    def report(self):
        return {
            'operators': self._report_operators(),
            'operands': self._report_operands(),
            'program': self._report_program(),
        }


    def _report_operators(self):
        return {
            **{op.value: self._counter[op] for op in _OPERATORS},
            'N1': self.N_1()
        }


    def _report_operands(self):
        return {
            **{op.value: self._counter[op] for op in _OPERANDS},
            'N2': self.N_2()
        }


    def _report_program(self):
        return {f.__name__: f() for f in [
            self.vocabulary,
            self.length,
            self.calc_length,
            self.volume,
            self.difficulty,
            self.effort,
        ]}


    def __repr__(self):
        return '{{η₁: {}, η₂: {}, N₁: {}, N₂: {}}}'.format(
            self.η_1(),
            self.η_2(),
            self.N_1(),
            self.N_2(),
        )


    def __main__():
        is_file_provided = len(argv) > 1
        filename = argv[1] if is_file_provided else '<input>'
        input_stream = open(argv[1], 'rb') if is_file_provided else stdin.buffer

        print(Halstead(input_stream, filename).report())

        if is_file_provided:
            input_stream.close()


def stat_complexity(obj):
    def print_complexity():
        print(Halstead(BytesIO(bytes(getsource(obj), 'utf-8'))).report(), getsourcefile(obj))

    return print_complexity


def report_object(obj):
    return obj  # TODO


def report_complexity(obj):
    return obj  # TODO
