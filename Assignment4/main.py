'''
Author: Denis Chernikov, B16-SE-01, Innopolis University
Python 3.7.4
'''

__all__ = ['Halstead']

import ast
from collections import Counter
from enum import Enum
from functools import lru_cache, reduce
from math import log2
from os import linesep
from sys import argv, stdin
from tokenize import COMMENT, tokenize



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
            if toknum == COMMENT:
                self._counter[_Countable.COMMENT] += 1


    def __extract_values(self, input_stream, filename):
        source = input_stream.read()

        visitor = Halstead.__HalsteadNodeVisitor(self)
        source_ast = ast.parse(source, filename)
        visitor.visit(source_ast)

        self.__count_inline_comments(_bytes_line_iterator(source).__next__)


    @lru_cache()
    def η_1(self):
        return 20  # TODO: calculate


    @lru_cache()
    def η_2(self):
        return 5  # TODO: calculate


    @lru_cache()
    def N_1(self):
        return reduce(lambda a, b: a + b, (self._counter[k] for k in _OPERATORS))


    @lru_cache()
    def N_2(self):
        return reduce(lambda a, b: a + b, (self._counter[k] for k in _OPERANDS))


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
        return (linesep * 2).join([
            self._report_operators(),
            self._report_operands(),
            self._report_program(),
        ])


    def _report_operators(self):
        res = '[operators]'

        for op in _OPERATORS:
            res += linesep + '{}: {}'.format(op.value, self._counter[op])

        res += linesep + 'N1: ' + str(self.N_1())

        return res


    def _report_operands(self):
        res = '[operands]'

        for op in _OPERANDS:
            res += linesep + '{}: {}'.format(op.value, self._counter[op])

        res += linesep + 'N2: ' + str(self.N_2())

        return res


    def _report_program(self):
        res = '[program]'
        funcs = [
            self.vocabulary,
            self.length,
            self.calc_length,
            self.volume,
            self.difficulty,
            self.effort,
        ]

        for f in funcs:
            res += linesep + '{}: {}'.format(f.__name__, f())

        return res


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


if __name__ == '__main__':
    Halstead.__main__()
