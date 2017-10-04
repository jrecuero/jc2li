import os
import sys
from functools import partial
from base import CliBase
from common import SYNTAX_ATTR


class Cli(CliBase):
    """Cli class is the base class for any class that will implement
    commands to be used by the command line interface.
    """

    def __init__(self, include_basic=True):
        """Cli class initialization method.

        Args:
            include_basic (bool) : Flag that marks if the Cli class basic
            methods (exit, help, syntax and shell) should be included as
            commands for any derived class.
        """
        super(Cli, self).__init__()
        # This is required to add the Cli class method to any derived
        # class.
        if include_basic:
            for name, func_cb, desc in self._WALL.get('Cli', []):
                self.add_command(name, partial(func_cb, self), desc)

    @CliBase.command('exit')
    def do_exit(self, line):
        """Command that exit the CLI when "exit" is entered.

        Exit the application to the operating system.

        Args:
            line (str): string entered in the command line.

        Returns:
            :any:`None`
        """
        sys.exit(0)

    @CliBase.command('help')
    def do_help(self, line):
        """Command that displays all possible commands.

        Args:
            line (str): string entered in the command line.

        Returns:
            :any:`None`
        """
        for command in self.commands:
            print('- {0} : {1}'.format(command, self.get_command_desc(command)))

    @CliBase.command('syntax')
    def do_syntax(self, line):
        """Command that displays syntax for possible commands.

        Args:
            line (str): string entered in the command line.

        Returns:
            :any:`None`
        """
        for command in self.commands:
            command_cb = self.get_command_cb(command)
            # Required for partial methods.
            if hasattr(command_cb, SYNTAX_ATTR):
                print('> {0}'.format(getattr(command_cb, SYNTAX_ATTR)))
            elif hasattr(command_cb, 'func') and hasattr(command_cb.func, SYNTAX_ATTR):
                print('> {0}'.format(getattr(command_cb.func, SYNTAX_ATTR)))
            else:
                print('> {0}'.format(command))

    @CliBase.command('shell')
    def do_shell(self, line):
        """Comand that runs a shell command when "shell" is entered.

        Args:
            line (str): string entered in the command line.

        Returns:
            :any:`None`
        """
        print("running shell command:", line)
        output = os.popen(line).read()
        print(output)
