from __future__ import unicode_literals
import sys
import os
# import shlex
import loggerator
from clierror import CliException
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
# from prompt_toolkit.completion import Completer, Completion
# from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.token import Token
from prompt_toolkit.styles import style_from_dict

MODULE = 'BASE'


logger = loggerator.getLoggerator('base')


class CliBase(object):
    """CliBase class is the base class for any class that will implement
    commands to be used by the command line interface.
    """

    COMMANDS = {}

    TOOLBAR_STYLE = style_from_dict({Token.Toolbar: '#ffffff italic bg:#007777', })

    def __init__(self):
        """CliBase class initialization method.
        """
        self._cmd = None
        self._lastCmd = None
        self.setupCmds()

    @property
    def Cmd(self):
        """Get property that returns _cmd attribute.

        Returns:
            str : String with the command entered.
        """
        return self._cmd

    @Cmd.setter
    def Cmd(self, theCmd):
        """Set property that sets a new value for _cmd attribute.

        Args:
            theCmd (str) : String with new command entered.
        """
        self._cmd = theCmd

    @property
    def LastCmd(self):
        """Get property that returns _lastCmd attribute.

        Returns:
            str : String with the last command entered.
        """
        return self._lastCmd

    @LastCmd.setter
    def LastCmd(self, theCmd):
        """Set property that sets a new value for _lastCmd attribute.

        Args:
            theCmd (str) : String with the new last command.
        """
        self._lastCmd = theCmd

    @classmethod
    def Cmds(cls):
        """Get property that returns keys for _cmdDict attribute

        Returns:
            list : List with all command labels.
        """
        return cls.COMMANDS.keys()

    @classmethod
    def getCmdCb(cls, theCmd):
        """Get the command callback for the given command label.

        Args:
            theCmd (str) : String with the command label.

        Returns:
            func : callback function for the given command.
        """
        return cls.COMMANDS.get(theCmd, None)

    @classmethod
    def isCmd(cls, theCmd):
        """Returns if the given command label is found in the list of available
        commands.

        Args:
            theCmd (str) : Command label to check as an availbale command.

        Returns:
            boolean : True if command label is found, False else.
        """
        return theCmd in cls.Cmds()

    @classmethod
    def addCmd(cls, theCmd, theCmdCb):
        """Adds a new entry to the command dictionary.

        Args:
            theCmd (str) : String with the command label.
            theCmdCb (func) : Function with the command callback.

        Returns:
            boolean : True if command was added.
        """
        if cls.isCmd(theCmd):
            raise CliException(MODULE, 'Command [{}] already present.'.format(theCmd))
        cls.COMMANDS[theCmd] = theCmdCb
        return True

    @classmethod
    def execCmd(cls, theCmd, theUserInput):
        """Executes the command callback for the given command label.

        Args:
            theCmd (str) : Command label for the command to execute.
            theUserInput (str) : String with the command line input.

        Returns:
            object : value returned by the command callback.
        """
        cmdCb = cls.getCmdCb(theCmd)
        if cmdCb:
            return cmdCb(theUserInput)

    @classmethod
    def extend(cls, name, func):
        """Class method that allows to extend the class with new commands.

        Args:
            name (str) : name for the new command.
            func (function) : function for the new command.

        Returns:
            boolean : True if command was added, False, else
        """
        funcName = 'do_{}'.format(name)
        if getattr(cls, funcName, None):
            return False
        setattr(cls, 'do_{}'.format(name), func)
        cls.addCmd(name, func)
        return True

    @classmethod
    def extends(cls, cmds):
        """Class method that allows to extend the class with the list of
        commands given.

        Args:
            cmds (list) : list of dictionaries with name and function for
            every command.

        Returns:
            list : list of booleans, with True for every command being
            added and False for those which failed.
        """
        rets = {}
        for c in cmds:
            rets.update({c['name']: cls.extend(c['name'], c['cmd'])})
        return rets

    def emptyline(self):
        """Method that don't provide any action when <CR> is entered in an
        empty line.

        By default, the same command is executed when just <CR> is entered,
        but we don't want that behavior.
        """
        pass

    def do_exit(self, line):
        """Command that exit the CLI when "exit" is entered.

        Args:
            line (str): string entered in the command line.
        """
        sys.exit(0)

    def do_shell(self, line):
        """Comand that runs a shell command when "shell" is entered.

        Args:
            line (str): string entered in the command line.
        """
        print "running shell command:", line
        output = os.popen(line).read()
        print output

    def precmd(self, line):
        """Method to be called before any command is being processed.

        Args:
            line (str): string entered in the command line.
        """
        pass

    def onecmd(self, str):
        """Method to be called when any command is being processed.

        Args:
            line (str): string entered in the command line.
        """
        pass

    def post(self, line):
        """Method to be called after any command is being processed.

        Args:
            line (str): string entered in the command line.
        """
        pass

    def getBottomToolbarTokens(self, cli):
        # cmd = cli.current_buffer.history.strings[-1]
        # cmd = '' if cmd == 'exit' else cmd
        return [(Token.Toolbar, 'Command: {} '.format(self.LastCmd)), ]

    def setupCmds(self):
        """Register all commands to be used by the command line interface.

        Returns:
            None
        """
        self.addCmd('exit', self.do_exit)

    def cmdloop(self, thePrompt):
        """Method that is called to wait for any user input.

        Args:
            thePrompt (str) : string with the prompt for the command line.
        """
        while True:
            userInput = prompt('{}'.format(thePrompt),
                               history=FileHistory('history.txt'),
                               auto_suggest=AutoSuggestFromHistory(),
                               # completer=CliCompleter(),
                               # lexer=SqlLexer,
                               get_bottom_toolbar_tokens=self.getBottomToolbarTokens,
                               style=self.TOOLBAR_STYLE,
                               # validator=CliValidator(),
                               refresh_interval=1)
            print(userInput)
            if userInput:
                lineAsList = userInput.split()
                cmd = lineAsList[0]
                if self.isCmd(cmd):
                    self.execCmd(cmd, ' '.join(lineAsList[1:]))
                self.LastCmd = userInput
