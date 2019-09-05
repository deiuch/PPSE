'''
Author: Denis Chernikov, B16-SE-01, Innopolis University
Python 3.7.2
'''

from collections import Counter
import dis
from enum import Enum, auto
from functools import reduce
import marshal
import os
import py_compile
import sys


class BytecodeHelper:
    BIN_HEADER_LENGTH = 16  # Version-dependent
    COMPILE_OUT_PATH = 'out.pyc'
    TMP_FILE_NAME = '__tmp__.py'
    TABLE_COLUMN_WIDTH = 11
    TABLE_HEADER_SEP = ' | '
    TABLE_FIRST_HEADER = 'INSTRUCTION'


    def print(data_info):
        data_kind, data = data_info
        for instruction in BytecodeHelper._get_instructions(data_kind, data):
            print(instruction.opname, instruction.argval)


    def _get_instructions(data_kind, data):
        if data_kind is BytecodeHelperFormats.SCRIPT:
            with open(data, 'r') as script:
                code_obj = script.read()

        elif data_kind is BytecodeHelperFormats.BINARY:
            with open(data, 'rb') as bin_file:
                bin_file.read(BytecodeHelper.BIN_HEADER_LENGTH)  # Skip header
                code_obj = marshal.load(bin_file)

        else:  # BytecodeHelperFormats.STRING
            code_obj = data

        return dis.get_instructions(code_obj)


    def compile(data_info):
        data_kind, data = data_info
        assert data_kind is not BytecodeHelperFormats.BINARY

        file_path = data if data_kind is BytecodeHelperFormats.SCRIPT else BytecodeHelper.TMP_FILE_NAME

        if data_kind is BytecodeHelperFormats.STRING:
            with open(file_path, 'w') as out_file:
                out_file.write(data)

        py_compile.compile(file_path, BytecodeHelper.COMPILE_OUT_PATH)

        if data_kind is BytecodeHelperFormats.STRING:
            os.remove(file_path)


    def compare(data_list):
        amounts = {}

        for data_type, data in data_list:
            amounts[data] = Counter(
                op.opname for op in BytecodeHelper._get_instructions(data_type, data)
            )

        print(
            BytecodeHelper.TABLE_HEADER_SEP.join(
                format(s, '.'.join([str(BytecodeHelper.TABLE_COLUMN_WIDTH)] * 2)) for s
                    in [BytecodeHelper.TABLE_FIRST_HEADER] + [t[1] for t in data_list]
            )
        )

        ops_sum = reduce(lambda x, y: x + y, amounts.values())
        sorted_ops = sorted(ops_sum.keys(), key=lambda k: ops_sum[k], reverse=True)

        for op in sorted_ops:
            print(
                (' ' * len(BytecodeHelper.TABLE_HEADER_SEP)).join(
                    format(str(s), '.'.join([str(BytecodeHelper.TABLE_COLUMN_WIDTH)] * 2)) for s
                        in [op] + [amounts[t[1]][op] for t in data_list]
                )
            )


class BytecodeHelperFormats(Enum):
    SCRIPT = '-py'
    BINARY = '-pyc'
    STRING = '-s'


class _BytecodeHelperParams(Enum):
    HELP = auto()
    ACTION = auto()
    DATA = auto()
    ERROR = auto()


class _BytecodeHelperActions(Enum):
    COMPILE = 'compile'
    PRINT = 'print'
    COMPARE = 'compare'


class _BytecodeHelperErrors(Enum):
    WRONG_ACTION = 'Provided action is not supported'
    NOT_ENOUGH_ARGS = 'Too few arguments are provided for a given action'
    TOO_MUCH_ARGS = 'Too much arguments are provided for a given action'
    FORMAT_MISSING_DATA = 'There is no corresponding data for a given format specifier'
    WRONG_DATA_FORMAT = 'Provided data format is not supported'
    UNSUPPORTED_DATA_FORMAT = 'Provided data format is not supported by given action'
    INACCESSIBLE_FILE = 'Provided file does not exist or impossible to read'


class _BytecodeHelperArgsParser:
    def parse_args(args=sys.argv):
        settings = {
            _BytecodeHelperParams.HELP: False,
            _BytecodeHelperParams.ACTION: None,
            _BytecodeHelperParams.DATA: None,
            _BytecodeHelperParams.ERROR: None,
        }

        if args is None or len(args) <= 1:
            settings[_BytecodeHelperParams.HELP] = True
        else:
            try:
                mode = _BytecodeHelperActions(args[1])
                {
                    _BytecodeHelperActions.COMPILE: _BytecodeHelperArgsParser._parse_compile_mode_args,
                    _BytecodeHelperActions.PRINT: _BytecodeHelperArgsParser._parse_print_mode_args,
                    _BytecodeHelperActions.COMPARE: _BytecodeHelperArgsParser._parse_compare_mode_args,
                }[mode](settings, args[2:])
                settings[_BytecodeHelperParams.ACTION] = mode
            except ValueError:
                settings[_BytecodeHelperParams.ERROR] = (
                    _BytecodeHelperErrors.WRONG_ACTION,
                    args[1],
                )

        return settings


    def _parse_compile_mode_args(settings, args):
        if not args:
            settings[_BytecodeHelperParams.ERROR] = (
                _BytecodeHelperErrors.NOT_ENOUGH_ARGS,
                None,
            )
            return

        if len(args) > 2:
            settings[_BytecodeHelperParams.ERROR] = (
                _BytecodeHelperErrors.TOO_MUCH_ARGS,
                None,
            )
            return

        param, data = _BytecodeHelperArgsParser._parse_format_and_data(args, False)
        settings[param] = data


    def _parse_print_mode_args(settings, args):
        if not args:
            settings[_BytecodeHelperParams.ERROR] = (
                _BytecodeHelperErrors.NOT_ENOUGH_ARGS,
                None,
            )
            return

        if len(args) > 2:
            settings[_BytecodeHelperParams.ERROR] = (
                _BytecodeHelperErrors.TOO_MUCH_ARGS,
                None,
            )
            return

        param, data = _BytecodeHelperArgsParser._parse_format_and_data(args)
        settings[param] = data


    def _parse_compare_mode_args(settings, args):
        if not args:
            settings[_BytecodeHelperParams.ERROR] = (
                _BytecodeHelperErrors.NOT_ENOUGH_ARGS,
                None,
            )
            return

        n_args = len(args)
        files = []

        for i in range(0, len(args), 2):
            to_parse = [args[i]]

            if i + 1 < n_args:
                to_parse.append(args[i + 1])

            param, data = _BytecodeHelperArgsParser._parse_format_and_data(to_parse)

            if param is _BytecodeHelperParams.ERROR:
                settings[param] = data
                return

            files.append(data)

        if len(files) < 2:
            settings[_BytecodeHelperParams.ERROR] = (
                _BytecodeHelperErrors.NOT_ENOUGH_ARGS,
                None,
            )
            return

        settings[_BytecodeHelperParams.DATA] = files


    def _parse_format_and_data(args, is_binary_supported=True):
        try:
            format, data = args
        except ValueError:
            return (
                _BytecodeHelperParams.ERROR,
                (
                    _BytecodeHelperErrors.FORMAT_MISSING_DATA,
                    args[0],
                ),
            )

        try:
            format_enumed = BytecodeHelperFormats(format)
        except ValueError:
            return (
                _BytecodeHelperParams.ERROR,
                (
                    _BytecodeHelperErrors.WRONG_DATA_FORMAT,
                    format,
                ),
            )

        if not is_binary_supported and format_enumed is BytecodeHelperFormats.BINARY:
            return (
                _BytecodeHelperParams.ERROR,
                (
                    _BytecodeHelperErrors.UNSUPPORTED_DATA_FORMAT,
                    format,
                ),
            )

        if format_enumed is not BytecodeHelperFormats.STRING and not os.access(data, os.R_OK):
            return (
                _BytecodeHelperParams.ERROR,
                (
                    _BytecodeHelperErrors.INACCESSIBLE_FILE,
                    data,
                ),
            )

        return (
            _BytecodeHelperParams.DATA,
            (
                format_enumed,
                data,
            ),
        )


class _BytecodeHelperExec:
    MODULE_DESCRIPTION = '''
This program ...

compile
    -py file.py     compile file into bytecode and store it as file.pyc
    -s "src"        compile src into bytecode and store it as out.pyc

print
    -py src.py      produce human-readable bytecode from python file
    -pyc src.pyc    produce human-readable bytecode from compiled .pyc file
    -s "src"        produce human-readable bytecode from normal string

compare -format src [-format src]+
                    produce bytecode comparison for giving sources
                    (supported formats -py, -pyc, -s)
'''  # TODO


    def _handle_args_error(error):
        kind, data = error
        print(kind.value, data, sep=': ')  # TODO: make more informative


    def _print_help():
        print('usage: {} -py src.py'.format(sys.argv[0]))
        print(_BytecodeHelperExec.MODULE_DESCRIPTION)


    def _exec():
        params = _BytecodeHelperArgsParser.parse_args()

        if params[_BytecodeHelperParams.ERROR]:
            _BytecodeHelperExec._handle_args_error(params[_BytecodeHelperParams.ERROR])
        elif params[_BytecodeHelperParams.HELP]:
            _BytecodeHelperExec._print_help()
        else:
            {
                _BytecodeHelperActions.COMPILE: BytecodeHelper.compile,
                _BytecodeHelperActions.PRINT: BytecodeHelper.print,
                _BytecodeHelperActions.COMPARE: BytecodeHelper.compare,
            }[params[_BytecodeHelperParams.ACTION]](params[_BytecodeHelperParams.DATA])


if __name__ == "__main__":
    _BytecodeHelperExec._exec()
