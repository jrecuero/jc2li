from __future__ import unicode_literals
from functools import wraps, partial
import sys
import os
import inspect
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
logger = loggerator.getLoggerator(MODULE)


class Cli(object):
    """Cli class is the base class for any class that will implement
    commands to be used by the command line interface.
    """

    _WALL = {}
    CLI_STYLE = style_from_dict({Token.Toolbar: '#ffffff italic bg:#007777',
                                 Token.RPrompt: 'bg:#ff0066 #ffffff', })

    class CliCompleter(Completer):
        """CliCompleter class provide completion to any entry in the command line.

        This class should make use of every completer for command arguments.
        """

        def __init__(self, theCli):
            """CliCompleter initialization method.

            Args:
                theCli (Cli) : Cli instance.
            """
            self._nodepath = None
            self._cli = theCli

        def get_completions(self, document, completeEvent):
            """Method that provides completion for any input in the command line.

            Args:
                document (Document) : Document instance with command line input data.
                compleEvent (CompleteEvent) : Event with iinput information

            Returns:
                Completion : Completion instance with data to be completed.
            """
            self._nodepath = None
            wordBeforeCursor = document.get_word_before_cursor(WORD=True)
            if ' ' not in document.text:
                matches = [m for m in self._cli.Cmds if m.startswith(wordBeforeCursor)]
                for m in matches:
                    yield Completion(m, start_position=-len(wordBeforeCursor))
            else:
                lineList = document.text.split()
                lastToken = lineList[-1] if document.text[-1] != ' ' else ' '
                cmdLabel = lineList[0]
                cmd = self._cli.getCmdCb(cmdLabel)
                # Required for partial methods
                if hasattr(cmd, 'func'):
                    cmd = cmd.func
                root = getattr(cmd, TREE_ATTR, None)
                journal = self._cli.Journal
                _, cliArgos = journal.getCmdAndCliArgos(cmd, None, " ".join(lineList[1:]))
                nodePath = None
                childrenNodes = None
                try:
                    nodePath = root.findPath(cliArgos)
                    if not nodePath:
                        self._nodepath = [root, ]
                    if nodePath and document.text[-1] == ' ':
                        self._nodepath = nodePath
                    childrenNodes = self._nodepath[-1].getChildrenNodes() if self._nodepath else root.getChildrenNodes()
                    if childrenNodes:
                        helps = [c.Argo.Completer.help(lastToken) for c in childrenNodes]
                        self._cli.ToolBar = " | ".join(helps)
                        for child in childrenNodes:
                            matches = child.Argo.Completer.complete(document, lastToken)
                            for i, m in enumerate(matches):
                                yield Completion(m, start_position=-len(wordBeforeCursor))
                                # TODO: Remove help displayed in the completer
                                # yield Completion(m,
                                #                  start_position=-len(wordBeforeCursor),
                                #                  display_meta=helps[i])
                except Exception as ex:
                    logger.error('{0}, {1}'.format(ex, ex.__traceback__.tb_lineno))
                    pass
                logger.debug('completer cmd: {0}'.format(cmd))
                logger.debug('document text is "{}"'.format(document.text))
                logger.debug('last document text is [{}]'.format(lineList[-1]))
                logger.debug('children nodes are {}'.format(childrenNodes))
                if childrenNodes:
                    logger.debug('children nodes are {}'.format([x.Name for x in childrenNodes]))
                logger.debug('nodePath is {}'.format(nodePath))
                if nodePath:
                    logger.debug('nodePath is {}'.format([x.Name for x in nodePath]))
                if self._nodepath:
                    logger.debug('self._nodepath is {}'.format(self._nodepath))
                    logger.debug('self._nodepath is {}'.format([x.Name for x in self._nodepath]))

    def __init__(self):
        """Cli class initialization method.
        """
        self._cmd = None
        self._lastCmd = None
        self._toolbarStr = None
        self._rpromptStr = None
        self._promptStr = "> "
        self.__commands = {}
        self._journal = Journal()
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
        """Get property that returns _toolbar attribute.

        Returns:
            str : String with string to be displayed in the ToolBar.
        """
        return self._toolbarStr if self._toolbarStr else ''

    @ToolBar.setter
    def ToolBar(self, theStr):
        """Set property that sets a new vale for _toolbar attribute.

        Args:
            theStr (str) : New string to be displayed in the ToolBar.
        """
        self._toolbarStr = theStr

    @property
    def Prompt(self):
        """Get property that returns _toolbar attribute.

        Returns:
            str : String with string to be displayed in the Prompt.
        """
        return self._promptStr if self._promptStr else ''

    @Prompt.setter
    def Prompt(self, theStr):
        """Set property that sets a new vale for _toolbar attribute.

        Args:
            theStr (str) : New string to be displayed in the RPrompt.
        """
        self._promptStr = theStr

    @property
    def RPrompt(self):
        """Get property that returns _toolbar attribute.

        Returns:
            str : String with string to be displayed in the RPrompt.
        """
        return self._rpromptStr if self._rpromptStr else ''

    @RPrompt.setter
    def RPrompt(self, theStr):
        """Set property that sets a new vale for _toolbar attribute.

        Args:
            theStr (str) : New string to be displayed in the RPrompt.
        """
        self._rpromptStr = theStr

    @property
    def Cmds(self):
        """Get property that returns keys for _cmdDict attribute

        Returns:
            list : List with all command labels.
        """
        return self.__commands.keys()

    @property
    def Journal(self):
        """Get property that returns the Journal instance.

        Returns:
            Journal : Journal instance.
        """
        return self._journal

    def getCmdCb(self, theCmd):
        """Get the command callback for the given command label.

        Args:
            theCmd (str) : String with the command label.

        Returns:
            func : callback function for the given command.
        """
        cmdEntry = self.__commands.get(theCmd, (None, None))
        return cmdEntry[0]

    def getCmdDesc(self, theCmd):
        """Get the command description for the given command label.

        Args:
            theCmd (str) : String with the command label.

        Returns:
            str : description for the given command.
        """
        cmdEntry = self.__commands.get(theCmd, (None, None))
        return cmdEntry[1]

    def isCmd(self, theCmd):
        """Returns if the given command label is found in the list of available
        commands.

        Args:
            theCmd (str) : Command label to check as an availbale command.

        Returns:
            boolean : True if command label is found, False else.
        """
        return theCmd in self.Cmds

    def addCmd(self, theCmd, theCmdCb, theDesc=""):
        """Adds a new entry to the command dictionary.

        Args:
            theCmd (str) : String with the command label.
            theCmdCb (func) : Function with the command callback.

        Returns:
            boolean : True if command was added.
        """
        if self.isCmd(theCmd):
            logger.warning('[{}] Command [{}] already present.'.format(MODULE, theCmd))
        self.__commands[theCmd] = (theCmdCb, theDesc)

        # At this point, inject the context in every argument attributes using
        # theCmdCb.func._Arguments._arguments[#].Completer. That should work
        # only for those with _Arguments attribute inside theCmdCb.func.
        if hasattr(theCmdCb, 'func') and hasattr(theCmdCb.func, '_Arguments'):
            for argument in theCmdCb.func._Arguments.Arguments:
                argument.Journal = self.Journal

        return True

    def execCmd(self, theCmd, theUserInput):
        """Executes the command callback for the given command label.

        Args:
            theCmd (str) : Command label for the command to execute.
            theUserInput (str) : String with the command line input.

        Returns:
            object : value returned by the command callback.
        """
        cmdCb = self.getCmdCb(theCmd)
        if cmdCb:
            return cmdCb(theUserInput)

    def extend(self, name, func):
        """Class method that allows to extend the class with new commands.

        Args:
            name (str) : name for the new command.
            func (function) : function for the new command.

        Returns:
            boolean : True if command was added, False, else
        """
        funcName = 'do_{}'.format(name)
        if getattr(self, funcName, None):
            return False
        setattr(self, 'do_{}'.format(name), func)
        self.addCmd(name, func)
        return True

    def extends(self, cmds):
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
            rets.update({c['name']: self.extend(c['name'], c['cmd'])})
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
        """
        sys.exit(0)

    def do_help(self, line):
        """Command that displays all possible commands.
        """
        for cmd in self.Cmds:
            print('- {0} : {1}'.format(cmd, self.getCmdDesc(cmd)))

    def do_syntax(self, line):
        """Command that displays syntax for possible commands.
        """
        for cmd in self.Cmds:
            cmdCb = self.getCmdCb(cmd)
            # Required for partial methods.
            if hasattr(cmdCb, '_Syntax'):
                print('> {0}'.format(cmdCb._Syntax))
            elif hasattr(cmdCb, 'func') and hasattr(cmdCb.func, '_Syntax'):
                print('> {0}'.format(cmdCb.func._Syntax))
            else:
                print('> {0}'.format(cmd))

    def do_shell(self, line):
        """Comand that runs a shell command when "shell" is entered.

        Args:
            line (str): string entered in the command line.
        """
        print("running shell command:", line)
        output = os.popen(line).read()
        print(output)

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

    def postcmd(self, line):
        """Method to be called after any command is being processed.

        Args:
            line (str): string entered in the command line.
        """
        pass

    def getBottomToolbarTokens(self, theCli):
        """Method that provides data and format to be displayed in the ToolBar.

        Args:
            theCli (CommandLineInterface) : CommandLineInterface instance.

        Returns:
            list : list with data to be displayed in the ToolBar.
        """
        return [(Token.Toolbar, '{}'.format(self.ToolBar)), ]

    def getRPromptTokens(self, theCli):
        return [(Token.RPrompt, '{}'.format(self.RPrompt)), ]

    def getPromptTokens(self, theCli):
        return [(Token.Prompt, '{}'.format(self.Prompt)), ]

    def setupCmds(self):
        """Register all commands to be used by the command line interface.

        Returns:
            None
        """
        self.addCmd('exit', self.do_exit, self.do_exit.__doc__)
        self.addCmd('help', self.do_help, self.do_help.__doc__)
        self.addCmd('syntax', self.do_syntax, self.do_syntax.__doc__)
        self.addCmd('shell', self.do_shell, self.do_help.__doc__)

        klassName = self.__class__.__name__
        _calls = self._WALL.get(klassName, [])
        for name, funcCb, desc in _calls:
            logger.debug('{0}::setupCmds add command {1}::{2}'.format(klassName, name, funcCb))
            self.addCmd(name, partial(funcCb, self), desc)

    def run(self, thePrompt=None):
        self.ToolBar = 'Enter a valid command'
        if thePrompt is not None:
            self.Prompt = thePrompt
        userInput = prompt(history=FileHistory('history.txt'),
                           auto_suggest=AutoSuggestFromHistory(),
                           completer=Cli.CliCompleter(self),
                           # lexer=SqlLexer,
                           get_bottom_toolbar_tokens=self.getBottomToolbarTokens,
                           get_rprompt_tokens=self.getRPromptTokens,
                           get_prompt_tokens=self.getPromptTokens,
                           style=self.CLI_STYLE,
                           # validator=CliValidator(),
                           refresh_interval=1)
        return userInput

    def cmdloop(self, thePrompt=None):
        """Method that is called to wait for any user input.
        """
        while True:
            userInput = self.run(thePrompt)
            # print(userInput)
            if userInput:
                lineAsList = userInput.split()
                cmd = lineAsList[0]
                if self.isCmd(cmd):
                    self.execCmd(cmd, ' '.join(lineAsList[1:]))
                self.LastCmd = userInput

    @staticmethod
    def command(theLabel=None, theDesc=None):
        """Decorator that setup a function as a command.

        Args:
            theModule (class) : class name where this command is being added.
        """

        def f_command(f):

            @wraps(f)
            def _wrapper(self, *args, **kwargs):
                return f(self, *args, **kwargs)

            logger.debug(f, "YELLOW")
            moduleName = sys._getframe(1).f_code.co_name
            Cli._WALL.setdefault(moduleName, [])
            if theDesc is not None:
                desc = theDesc
            else:
                # if the wrapper is not a <method> or a <function> it is a
                # partial function, so the __doc__ is inside 'func' attribute.
                if inspect.ismethod(_wrapper) or inspect.isfunction(_wrapper):
                    desc = _wrapper.__doc__
                else:
                    desc = _wrapper.func.__doc__
            labelFromSyntax = getattr(f, '_Syntax', None)
            label = f.__name__ if labelFromSyntax is None else labelFromSyntax.split()[0]
            Cli._WALL[moduleName].append((theLabel if theLabel else label, _wrapper, desc))
            return _wrapper

        return f_command
