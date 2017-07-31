from functools import wraps
import shlex
import cliparser
from common import Argument, Arguments
from common import ARGOS_ATTR, RULES_ATTR, SYNTAX_ATTR, CMD_ATTR
from journal import Journal
from clierror import CliException

MODULE = 'DECORATOR'


def params(*args):
    """Decorator that provides a gross mode for default values.

    Args:
        args (list) : default values for every argument to be passed to the
        command
    """

    def f_params(f):

        @wraps(f)
        def _wrapper(self, theLine):
            cliArgos = shlex.split(theLine)
            useArgs = list(args)
            try:
                for i, v in enumerate(cliArgos):
                    useArgs[i] = v
                return f(self, useArgs[0], useArgs[1])
            except IndexError as ex:
                raise CliException(MODULE,
                                   'Too many arguments for command: {}'.format(f.func_name[3:]),
                                   ex.message)

        return _wrapper

    return f_params


def arguments(*args):
    """Decorator that provides a way for typing every argument.

    Args:
        args (list) : type for every argument to be passed to the command.
    """

    def f_arguments(f):

        @wraps(f)
        def _wrapper(self, theLine):
            cliArgos = shlex.split(theLine)
            if len(args) != len(cliArgos):
                raise CliException(MODULE, 'Wrong number of arguments')
            else:
                try:
                    return f(self, *[x._(y) for x, y in zip(args, cliArgos)])
                except ValueError as ex:
                    raise CliException(MODULE,
                                       'Wrong type of argument for command: {}'.format(f.func_name[3:]),
                                       ex.message)
                except OverflowError as ex:
                    raise CliException(MODULE,
                                       'Overflow value for argument for command: {}'.format(f.func_name[3:]),
                                       ex.message)

        return _wrapper

    return f_arguments


def defaults(*args):
    """Decorator that provide type and default value for every argument.

    Args:
        args (list) : pair with the type an the default value for every
        argument to be passed to the command.
    """

    def f_defaults(f):

        @wraps(f)
        def _wrapper(self, theLine):
            cliArgos = shlex.split(theLine)
            if len(args) < len(cliArgos):
                raise CliException(MODULE,
                                   'Wrong number of arguments for command: {}'.format(f.func_name[3:]))
            else:
                try:
                    return f(self, *[x._(z) if z is not None else y for (x, y), z in map(None, args, cliArgos)])
                except ValueError as ex:
                    raise CliException(MODULE,
                                       'Wrong type of argument for command: {}'.format(f.func_name[3:]),
                                       ex.message)
                except OverflowError as ex:
                    raise CliException(MODULE,
                                       'Overflow value for argument for command: {}'.format(f.func_name[3:]),
                                       ex.message)

        return _wrapper

    return f_defaults


def argo(theName, theType, theDefault):
    """Decorator that provides to add an argument to a command.

    Args:
        theName (str) : argument name. This will be used when making any
        reference to this argument
        theType (object) : argument type, it should be a class name.
        theDefault (object) : default value for the argument.
    """

    def f_argo(f):

        @wraps(f)
        def _wrapper(self, *args):
            return f(self, *args)
        cmdArgos = getattr(_wrapper, ARGOS_ATTR, Arguments())
        cmdArgos.insertArgument(Argument(theName, theType, theDefault))
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


def setargos(f):
    """Decorator that setup all argument for a command.

    Before the command function is called, it types every type argument to
    the type provided in the @argo decorator and the default values for those
    arguments not entered by the user in the command line.
    """

    @wraps(f)
    def _wrapper(self, theLine):
        cmdArgos = getattr(f, ARGOS_ATTR, None)
        if cmdArgos is None:
            return f(self, theLine)
        else:
            cmdArgos.index()
            cliArgos = shlex.split(theLine)
            defArgs = [(x.Type, x.Default) for x in cmdArgos.Arguments]
            useArgs = [x._(z) if z is not None else y for (x, y), z in map(None, defArgs, cliArgos)]
            if all(map(lambda x: x is not None, useArgs)):
                return f(self, *useArgs)
            else:
                raise CliException(MODULE,
                                   'Mandatory argument is not present  for command: {}'.format(f.func_name[3:]))

    return _wrapper


def setdictos(f):
    """Decorator that setup all argument as named for a command.

    Before the command function is called, it types every type argument to
    the type provided in the @argo decorator and the default values for those
    arguments not entered by the user in the command line. Moreover it allows
    the use of named attributes at any point when entering the command. Named
    arguments are in the format <argument-name>=<argument-value>, where
    <argument-name> is the value provided in the @argo decorator for the
    "name" attribute.
    """

    @wraps(f)
    def _wrapper(self, theLine):
        cmdArgos = getattr(f, ARGOS_ATTR, None)
        if cmdArgos is None:
            return f(self, theLine)
        else:
            cmdArgos.index()
            cliArgos = shlex.split(theLine)
            for index, passArg in enumerate(cliArgos):
                if '=' in passArg:
                    argName, argValue = passArg.split('=')
                    argEntry = cmdArgos.getArgoFromName(argName)
                    if argEntry is not None:
                        argEntry.Value = argEntry.Type._(argValue)
                else:
                    entry = cmdArgos.getArgoFromIndex(index)
                    cmdArgos.setIndexedValueFromName(entry.Name, entry.Type._(passArg))
            useArgs = cmdArgos.getIndexedValues()
            if all(map(lambda x: x is not None, useArgs)):
                return f(self, *useArgs)
            else:
                raise CliException(MODULE,
                                   'Mandatory argyments is not present for command: {}'.format(f.func_name[3:]))

    return _wrapper


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

    journal.buildCommandParsingTree(f)
    return _wrapper


def command(theModule):
    """Decorator that setup a function as a command.

    Args:
        theModule (class) : class name where this command is being added.
    """

    def f_command(f):

        @wraps(f)
        def _wrapper(self, theLine):
            return f(self, theLine)

        theModule.extend(f.func_name, _wrapper)
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
