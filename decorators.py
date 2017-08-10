from functools import wraps
import cliparser
from common import Argument, Arguments
from common import ARGOS_ATTR, RULES_ATTR, SYNTAX_ATTR, CMD_ATTR, TREE_ATTR
from journal import Journal

MODULE = 'DECORATOR'


def argo(theName, theType, theDefault, **kwargs):
    """Decorator that provides to add an argument to a command.

    Args:
        theName (str) : argument name. This will be used when making any
        reference to this argument
        theType (object) : argument type, it should be a class name.
        theDefault (object) : default value for the argument.
        theCompleter (object) : argument completer instance
    """

    def f_argo(f):

        @wraps(f)
        def _wrapper(self, *args):
            return f(self, *args)
        cmdArgos = getattr(_wrapper, ARGOS_ATTR, Arguments())
        kwargs.setdefault('theDefault', theDefault)
        cmdArgos.insertArgument(Argument(theName, theType, **kwargs))
        setattr(_wrapper, ARGOS_ATTR, cmdArgos)

        return _wrapper

    return f_argo


def argos(theArgos):
    """Decorator that provides to create a group of arguments to a command.

    Args:
        theArgos (list) : list of arguments configured as @argo.
    """

    def f_setargos(f):

        @wraps(f)
        def _wrapper(self, *args):
            return f(self, *args)

        cmdArgos = getattr(_wrapper, ARGOS_ATTR, Arguments())
        for arg in theArgos.reversed():
            cmdArgos.insert(arg)
        setattr(_wrapper, ARGOS_ATTR, cmdArgos)
        return _wrapper

    return f_setargos


def syntax(theSyntax):
    """Decorator that setup the command syntax

    Command syntax use these rules:

        - Mandatory positional argumetns only can be entered first, and it is
        enough with the argument name.
        - Any optional argument that can be entered or not, should be defined
        in this way: [ <arg-name> ]?
        - Any optional argument that can be entered or not, or multiple times
        should be defined in this way: [ <arg-name> ]*
        - Any mandatory argument that has to be entered, but it can be entered
        multiple times and after any optional argument, should be defined in
        this way: [ <arg-name> ]+
        - <arg-name> is the argument name that is provided in teh @argo
        decorator.
        - Several optional arguments can be defined, usign "|" to separate
        them. For example: [ arg1 | arg2 ]? defines taht arg1 or arg2 or no
        argument should be entered at that point. This can be used only for
        argument defined wit "?", "*" or "+"

    Args:
        theSyntax (str) : string with the command syntax.
    """

    def f_syntax(f):

        @wraps(f)
        def _wrapper(self, *args):
            return f(self, *args)

        cmd, rules = cliparser.processSyntax(theSyntax)
        setattr(_wrapper, SYNTAX_ATTR, theSyntax)
        setattr(_wrapper, CMD_ATTR, cmd)
        setattr(_wrapper, RULES_ATTR, rules)

        return _wrapper

    return f_syntax


def setsyntax(f):
    """Decorator that setup the command syntax

    Before the command function is called is called, it uses the syntax rules
    created for the information provided by the @syntax decorator, so it will
    assign properly all commands arguments and it will return any error with
    any command argument entered improperly. Argument type is provided for
    values being entered, and default values are provided for any optional
    argument not being entered.
    """

    journal = Journal()

    @wraps(f)
    def _wrapper(self, theLine):
        useArgs = journal.buildCommandArgumentsFromSyntax(f, self, theLine)
        if useArgs is not None:
            return f(self, *useArgs)

    root = journal.buildCommandParsingTree(f)
    setattr(_wrapper, TREE_ATTR, root)
    return _wrapper


def command(theModule, theLabel=None):
    """Decorator that setup a function as a command.

    Args:
        theModule (class) : class name where this command is being added.
    """

    def f_command(f):

        @wraps(f)
        def _wrapper(self, theLine):
            return f(self, theLine)

        theModule.extend(theLabel if theLabel else f.func_name, _wrapper)
        return _wrapper

    return f_command


def mode(theParent, theModule, thePrompt=None):
    """Decorator that setup a function as a mode.

    This will create a new set of commands to be executed. It can have
    a new prompt and we will need a way to exit and come back to the parent
    set of commands.

    Args:
        theParent (class) : class name under where mode will be added.
        theModule (class) : class name for the mode
        thePrompt (str) : string to be used as a new prompt.

    """

    if thePrompt is None:
        thePrompt = theModule.__name__

    def f_command(f):

        @wraps(f)
        def _wrapper(self, theLine):
            return f(self, theLine)
            mode = theModule()
            mode.prompt = '({}) '.format(thePrompt)
            mode.cmdloop()

        theParent.extend(f.func_name, _wrapper)
        return _wrapper

    return f_command
