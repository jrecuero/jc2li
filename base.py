from __future__ import unicode_literals
from functools import wraps
import sys
import os
# import shlex
import loggerator
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
# from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.token import Token
from prompt_toolkit.styles import style_from_dict
from common import TREE_ATTR
from journal import Journal

MODULE = 'BASE'


logger = loggerator.getLoggerator('base')


class Cli(object):
    """Cli class is the base class for any class that will implement
    commands to be used by the command line interface.
    """

    COMMANDS = {}

    TOOLBAR_STYLE = style_from_dict({Token.Toolbar: '#ffffff italic bg:#007777', })

    class CliCompleter(Completer):

        def __init__(self, theCli):
            self._nodepath = None
            self._cli = theCli

        def get_completions(self, document, completeEvent):
            wordBeforeCursor = document.get_word_before_cursor(WORD=True)
            if ' ' not in document.text:
                matches = [m for m in Cli.Cmds() if m.startswith(wordBeforeCursor)]
                for m in matches:
                    yield Completion(m, start_position=-len(wordBeforeCursor))
            else:
                lineList = document.text.split()
                cmdLabel = lineList[0]
                cls, cmd = Cli.getCmdCb(cmdLabel)
                root = getattr(cmd, TREE_ATTR, None)
                journal = Journal()
                _, cliArgos = journal.getCmdAndCliArgos(cmd, None, " ".join(lineList[1:]))
                nodePath = None
                childrenNodes = None
                try:
                    nodePath = root.findPath(cliArgos)
                    if not nodePath:
                        self._nodepath = [root, ]
                    if nodePath and document.text[-1] == ' ':
                        self._nodepath = nodePath
                    childrenNodes = self._nodepath[0].getChildrenNodes() if self._nodepath else root.getChildrenNodes()
                    if childrenNodes:
                        self._cli.ToolBar = childrenNodes[0].Argo.Completer.help(lineList[-1])
                        matches = childrenNodes[0].Argo.Completer.complete(lineList[-1])
                        for m in matches:
                            yield Completion(m, start_position=-len(wordBeforeCursor))
                except:
                    pass
                logger.debug('last document text is [{}]'.format(lineList[-1]))
                logger.debug('children nodes are {}'.format(childrenNodes))
                logger.debug('nodePath is {}'.format(nodePath))
                logger.debug('self._nodepath is {}'.format(self._nodepath))

    def __init__(self):
        """Cli class initialization method.
        """
        self._cmd = None
        self._lastCmd = None
        self._toolbarStr = None
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

    @property
    def ToolBar(self):
        return self._toolbarStr if self._toolbarStr else ''

    @ToolBar.setter
    def ToolBar(self, theStr):
        self._toolbarStr = theStr

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
        return cls.COMMANDS.get(theCmd, (None, None))

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
    def addCmd(cls, theCmd, theCmdCb, theCls=None):
        """Adds a new entry to the command dictionary.

        Args:
            theCmd (str) : String with the command label.
            theCmdCb (func) : Function with the command callback.

        Returns:
            boolean : True if command was added.
        """
        if cls.isCmd(theCmd):
            logger.warning('[{}] Command [{}] already present.'.format(MODULE, theCmd))
        cls.COMMANDS[theCmd] = (theCls, theCmdCb)
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
        cls, cmdCb = cls.getCmdCb(theCmd)
        if cmdCb:
            return cmdCb(cls, theUserInput) if cls else cmdCb(theUserInput)

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
        return [(Token.Toolbar, '{}'.format(self.ToolBar)), ]

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
            # self.ToolBar = 'Command: {} '.format(self.LastCmd)
            self.ToolBar = 'Enter a valid command'
            userInput = prompt('{}'.format(thePrompt),
                               history=FileHistory('history.txt'),
                               auto_suggest=AutoSuggestFromHistory(),
                               completer=Cli.CliCompleter(self),
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

    @classmethod
    def command(cls, theLabel=None):
        """Decorator that setup a function as a command.

        Args:
            theModule (class) : class name where this command is being added.
        """

        def f_command(f):

            @wraps(f)
            def _wrapper(self, *args, **kwargs):
                return f(self, *args, **kwargs)

            logger.debug(f, "YELLOW")
            logger.debug(dir(f), "YELLOW")
            cls.addCmd(theLabel if theLabel else f.func_name, _wrapper, cls)
            return _wrapper

        return f_command
