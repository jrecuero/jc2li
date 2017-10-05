import os
import sys
from base import CliBase
from argtypes import Str, Int
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
        # This is required to add the Cli class method to any derived class.
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

    @CliBase.command()
    @setsyntax
    @syntax('syntax [name]?')
    @argo('name', Str, 'None')
    def do_syntax(self, name):
        """Command that displays syntax for possible commands.

        Args:
            line (str): string entered in the command line.
        """
        for command in self.commands:
            if name == 'None' or name == command:
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

    @CliBase.command("start-recording")
    def do_start_recording(self, line):
        """Starts recording commands.
        """
        print('start-recording commands')
        self.start_recording()

    @CliBase.command("stop-recording")
    def do_stop_recording(self, line):
        """Stops recording commands.
        """
        print('stop-recording commands')
        self.stop_recording()

    @CliBase.command()
    @setsyntax
    @syntax('display-recording [start]? [end]?')
    @argo('start', Int, 0)
    @argo('end', Int, -1)
    def do_display_recording(self, start, end):
        """Displays recording commands.

        Args:
            start (int) : Integer with first command to display.

            end (int) : Integer with last command to display.
        """
        end = None if end == -1 else end
        print("display-recording from {0} to {1}".format(start, end))
        self.display_recording(start, end)

    @CliBase.command()
    @setsyntax
    @syntax('clear-recording [start]? [end]?')
    @argo('start', Int, 0)
    @argo('end', Int, -1)
    def do_clear_recording(self, start, end):
        """Clears recording commands.

        Args:
            start (int) : Integer with first command to clear.

            end (int) : Integer with last command to clear.
        """
        end = None if end == -1 else end
        print("clear-recording from {0} to {1}".format(start, end))
        self.clear_recording(start, end)

    @CliBase.command()
    @setsyntax
    @syntax('save-recording filename [start]? [end]?')
    @argo('filename', Str, None)
    @argo('start', Int, 0)
    @argo('end', Int, -1)
    def do_save_recording(self, filename, start, end):
        """Saves recording commands.

        Args:
            filename (str) : String with the file to save commands.

            start (int) : Integer with first command to save.

            end (int) : Integer with last command to save.
        """
        end = None if end == -1 else end
        print("save-recording to {0} from {1} to {2}".format(filename, start, end))
        self.save_recording(filename, start, end)
