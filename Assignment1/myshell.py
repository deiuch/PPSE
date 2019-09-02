'''
Author: Denis Chernikov, B16-SE-01, Innopolis University
'''

from datetime import datetime
from enum import Enum
import os
import subprocess
import sys
from typing import Optional, Tuple


class CustomCommands(Enum):
    CHANGE_DIR = 'cd'
    EXIT = 'exit'


class MyShell():
    SHELL_NAME: str = 'myshell'
    LOG_FILE_PATH: str = SHELL_NAME + '.log'
    ERR_FILE_PATH: str = SHELL_NAME + '.stderr'
    CHANGE_DIR_ERROR_MSG: bytes = b'The system cannot find the path specified.\n'
    EXIT_MESSAGE: bytes = b'Goodbye!\n'


    def __init__(self):
        self._exited: bool = False


    def _shorten_path(path: str) -> str:
        '''
        Cut every section in the file path down to 1 character (or 2 if starts with '.').
        '''
        return os.sep.join(
            map(
                lambda substr: substr[:2] if substr[0] == '.' else substr[0],
                os.path.normpath(path).split(os.sep),
            )
        )


    def _get_prompt() -> str:
        '''
        Get the prompt text of MyShell.
        '''
        return (
            '{} [{}]: '
                .format(MyShell.SHELL_NAME, MyShell._shorten_path(os.getcwd()))
        )


    def _separate_callee_and_args(command: str) -> Tuple[str, Optional[str]]:
        '''
        Separate the command into the callee and it's arguments.
        '''
        res = command.strip().split(' ', 1)

        while len(res) < 2:
            res.append(None)

        return tuple(res)


    def _log_action(callee: str, args: str, stdout: bytes, pid: int, exit_code: int, cwd: str = '') -> None:
        '''
        Write an action info into the log file.

        Note: if a file should be placed somewhere else than the CWD, pass the `cwd` argument.
        '''
        with open(os.path.join(cwd, MyShell.LOG_FILE_PATH), 'ab') as log_file:
            log_file.write(
                '[{}]\n* cmd: {}\n* args: {}\n* pid: {}\n* exit: {}\n* stdout:\n'
                    .format(datetime.utcnow(), callee, args, pid, exit_code).encode()
            )
            log_file.write(stdout)
            log_file.write(b'\n=========================\n')


    def _handle_subprocess(callee: str, args: str) -> None:
        '''
        Run given callee as a subprocess, handle it's output streams and log it.

        Note: `stderr` stream will be written to the corresponding file in CWD.
        '''
        cmd_proc = subprocess.Popen(
            ' '.join([callee, args]) if args else callee,
            shell=True,
            stdin=sys.stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        out_bytes = b''

        while True:
            out_char = cmd_proc.stdout.read(1)  # Less efficient, but more flexible
            out_bytes += out_char
            sys.stdout.buffer.write(out_char)

            if out_char == b'' and cmd_proc.poll() is not None:
                break

        err_bytes = cmd_proc.stderr.read()
        if err_bytes:
            with open(MyShell.ERR_FILE_PATH, 'ab') as err_file:
                err_file.write(err)

        MyShell._log_action(
            callee,
            args,
            out_bytes,
            cmd_proc.pid,
            cmd_proc.poll(),
        )


    def _execute_cd(path: str) -> None:
        '''
        Execute `cd` command (will change CWD) and log it.

        Note: logging will be done into the previous CWD's log.
        '''
        success: bool = True
        old_dir: str = os.getcwd()

        if path:
            try:
                os.chdir(path)
            except FileNotFoundError:
                sys.stdout.buffer.write(MyShell.CHANGE_DIR_ERROR_MSG)
                success = False

        MyShell._log_action(
            CustomCommands.CHANGE_DIR.value,
            path,
            b'' if success else MyShell.CHANGE_DIR_ERROR_MSG,
            None,
            0 if success else 1,
            old_dir,
        )


    def _execute_exit(self) -> None:
        '''
        Execute `exit` command (will set exit flag for the shell) and log it.

        Note: sets `_exited` flag.
        '''
        sys.stdout.buffer.write(MyShell.EXIT_MESSAGE)
        # exit()  # Not recommended to use because caller will terminate too
        self._exited = True

        MyShell._log_action(
            CustomCommands.EXIT.value,
            None,
            MyShell.EXIT_MESSAGE,
            None,
            None,
        )


    def _execute_command(self, command: str) -> None:
        '''
        Execute the given command.

        Note: command will be logged if this functionality is implemented for the command.
        '''
        callee, args = MyShell._separate_callee_and_args(command)

        try:
            {
                CustomCommands.CHANGE_DIR: lambda: MyShell._execute_cd(args),
                CustomCommands.EXIT: self._execute_exit,
            }[CustomCommands(callee)]()
        except (KeyError, ValueError):
            MyShell._handle_subprocess(callee, args)


    def run(self) -> None:
        '''
        Run MyShell's main loop.

        Note: loop breaks on `_exited` flag set.
        '''
        while not self._exited:
            try:
                self._execute_command(input(MyShell._get_prompt()))

            except (EOFError, KeyboardInterrupt):
                self._execute_exit()
                break

        self._exited = False


if __name__ == '__main__':
    MyShell().run()
