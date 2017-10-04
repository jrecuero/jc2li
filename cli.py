import os
import sys
from base import CliBase
from argtypes import Str
from decorators import setsyntax, syntax, argo
from common import SYNTAX_ATTR


class Cli(CliBase):
    """Cli class is the base class for any class that will implement
    commands to be used by the command line interface.
    """

    def __init__(self, include_basic=True):
        """Cli class initialization method.

        Args:
            include_basic (bool) : Flag that marks if the Cli class basic\
                    methods (exit, help, syntax and shell) should be included\
                    as commands for any derived class.
        """
        super(Cli, self).__init__()
        # This is required to add the Cli class method to any derived
        # class.
        if include_basic:
            self.extend_commands_from_class('Cli')

    @CliBase.command('exit')
    def do_exit(self, line):
        """Command that exit the CLI when "exit" is entered.

        Exit the application to the operating system.
        """
        sys.exit(0)

    @CliBase.command()
    @setsyntax
    @syntax('help [name]?')
    @argo('name', Str, 'None')
    def do_help(self, name):
        """Command that displays all possible commands.
        """
        if name == 'None':
            for command in self.commands:
                print('- {0} : {1}'.format(command, self.get_command_desc(command)))
        else:
            print('- {0} : {1}'.format(name, self.get_command_desc(name)))

    @CliBase.command('syntax')
    def do_syntax(self, line):
        """Command that displays syntax for possible commands.

        Args:
            line (str): string entered in the command line.
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
            line (str): String with shell command to be executed.
        """
        print("running shell command:", line)
        output = os.popen(line).read()
        print(output)

    @CliBase.command()
    @setsyntax
    @syntax('import filename')
    @argo('filename', Str, None)
    def do_import(self, filename):
        """Command that imports commands from a JSON file.

        Args:
            filename (str) : String with the filename to import.
        """
        self.load_commands_from_file(filename)
