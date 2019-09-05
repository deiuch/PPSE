'''
Author: Denis Chernikov, B16-SE-01, Innopolis University
Python 3.7.2
'''

from enum import Enum, auto
import os
from timeit import timeit
import sys


def extend_with_spaces(to_extend, n):
    return format(to_extend, '<' + str(n))


class _BenchmarkParams(Enum):
    HELP = auto()
    FILES = auto()
    FAILED = auto()


class Benchmark:
    PY_FILE_FORMATS = ['.py']
    FAILED_WARNING = 'WARNING: This paths are either incorrect or impossible to read from:'
    TABLE_HEADERS = ['PROGRAM', 'RANK', 'TIME ELAPSED']
    TABLE_HEADER_SEP = ' | '
    TABLE_N_DIGITS_AFTER_DOT = 9

    MODULE_DESCRIPTION = '''
This program ...
'''  # TODO

    def time(script_paths, verbose=False):
        res = []

        if not verbose:
            stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        for path in script_paths:
            with open(path) as script_file:
                if verbose:
                    print('Testing: {}'.format(path))

                res.append(
                    (
                        path,
                        timeit(script_file.read(), number=1),
                    )
                )

        print()

        if not verbose:
            sys.stdout.close()
            sys.stdout = stdout

        return sorted(res, key=lambda t: t[1])


    def table_result(res):
        assert len(Benchmark.TABLE_HEADERS) > 2

        n_res = len(res)
        column_widths = []

        column_widths.append(
            max(
                len(Benchmark.TABLE_HEADERS[0]),
                max(map(lambda t: len(t[0]), res)),
            )
        )
        column_widths.append(
            max(
                len(Benchmark.TABLE_HEADERS[1]),
                len(str(n_res)),
            )
        )
        max_int_time_str_len = len(str(int(max(map(lambda t: t[1], res)))))
        max_num_len = max_int_time_str_len + Benchmark.TABLE_N_DIGITS_AFTER_DOT + 1
        column_widths.append(
            max(
                len(Benchmark.TABLE_HEADERS[2]),
                max_num_len + 1,  # because of trailing 's'
            )
        )

        res_formated = []

        for path, time in res:
            res_formated.append(
                (
                    extend_with_spaces(path, column_widths[0]),
                    ('{{:#{}.{}f}}s').format(
                        max_num_len,
                        Benchmark.TABLE_N_DIGITS_AFTER_DOT,
                    ).format(time),
                )
            )

        header = ''

        for i in range(len(column_widths)):
            if i > 0:
                header += Benchmark.TABLE_HEADER_SEP

            header += extend_with_spaces(Benchmark.TABLE_HEADERS[i], column_widths[i])

        table_lines = [header]

        for i in range(len(res)):
            cur_res = res_formated[i]
            table_lines.append(
                extend_with_spaces('', len(Benchmark.TABLE_HEADER_SEP)).join(
                    [
                        extend_with_spaces(cur_res[0], column_widths[0]),
                        extend_with_spaces(str(i + 1), column_widths[1]),
                        extend_with_spaces(cur_res[1], column_widths[2]),
                    ]
                )
            )

        return os.linesep.join(table_lines)


    def _print_failed_args(wrong_paths):
        if not len(wrong_paths):
            return

        print(Benchmark.FAILED_WARNING)

        for path in wrong_paths:
            print(path)

        print()


    def _parse_args(args=sys.argv):
        settings = {
            _BenchmarkParams.HELP: False,
            _BenchmarkParams.FILES: None,
            _BenchmarkParams.FAILED: None,
        }

        if args is None or len(args) <= 1:
            settings[_BenchmarkParams.HELP] = True
        else:
            failed = []

            def is_available_py_file(path):
                res = any(
                    path.endswith(format) for format in Benchmark.PY_FILE_FORMATS
                ) and os.access(path, os.R_OK)

                if not res:
                    failed.append(path)

                return res

            settings[_BenchmarkParams.FILES] = list(
                filter(
                    is_available_py_file,
                    map(lambda arg: arg.strip(), args[1:]),
                )
            )
            settings[_BenchmarkParams.FAILED] = failed

        return settings


    def _print_help():
        print('usage: {} [files]'.format(sys.argv[0]))
        print(Benchmark.MODULE_DESCRIPTION)


    def _exec():
        params = Benchmark._parse_args()

        if params[_BenchmarkParams.HELP]:
            Benchmark._print_help()
            return

        Benchmark._print_failed_args(params[_BenchmarkParams.FAILED])
        print(
            Benchmark.table_result(
                Benchmark.time(params[_BenchmarkParams.FILES])
            )
        )


if __name__ == "__main__":
    Benchmark._exec()
