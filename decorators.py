from functools import wraps
import shlex
import cliparser
from common import _HANDLE_ERROR, Argument, Arguments, RuleHandler
# from common import getPathFromLine
from node import Start


ARGOS_ATTR = '_Arguments'
RULES_ATTR = '_Rules'
SYNTAX_ATTR = '_Syntax'
CMD_ATTR = '_Cmd'
TREE_ATTR = '_Tree'


def _getCmdAndCliArgos(f, theInst, theLine):
    """Retrieve the command arguments stored in the command function and
    provided by @argo and @argos decorators; and the arguments passed by
    the user in the command line.
    """
    cmdArgos = getattr(f, ARGOS_ATTR, None)
    if cmdArgos is None:
        return f(theInst, theLine)
    cmdArgos.index()
    cliArgos = shlex.split(theLine)
    return cmdArgos, cliArgos


def _mapPassedArgosToCommandArgos(theRoot, theCmdArgos, theCliArgos):
    """Using the command arguments and argument values passed by the user
    in the CLI, map those using the command parsing tree in order to generate
    all arguments to be passed to the command function.
    """
    # path = getPathFromLine(theCliArgos)
    nodePath = theRoot.findPath(theCliArgos)
    # nodes = theRoot.findNodes()
    matchedNodes = list()
    for nod, val in zip(nodePath, theCliArgos):
        if '=' in val:
            _, argValue = val.split('=')
        else:
            argValue = val
        argValue = nod.Argo.Type._(argValue)
        if nod not in matchedNodes:
            nod.Argo.Value = argValue
        else:
            if type(nod.Argo.Value) == list:
                nod.Argo.Value.append(argValue)
            else:
                nod.Argo.Value = [nod.Argo.Value, argValue]
        matchedNodes.append(nod)
    useArgs = theCmdArgos.getIndexedValues()
    return useArgs


def _buildCommandParsingTree(f):
    """Build the command parsing tree using the command arguments and the
    command syntax.
    """
    root = Start()
    argos = getattr(f, ARGOS_ATTR, None)
    if argos:
        argos.index()
        rules = getattr(f, RULES_ATTR, list())
        trav = root
        for rule in rules:
            newTrav = trav.buildChildrenNodeFromRule(rule, argos)
            trav = newTrav
        setattr(f, TREE_ATTR, root)
        return True
    return _HANDLE_ERROR("Error: Building Command Parsing Tree: arguments not defined")


def params(*args):
    """Decorator that provides a gross mode for default values.
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
            except IndexError:
                _HANDLE_ERROR('too many arguments for command')

        return _wrapper

    return f_params


def arguments(*args):
    """Decorator that provides a way for typing every argument.
    """

    def f_arguments(f):

        @wraps(f)
        def _wrapper(self, theLine):
            cliArgos = shlex.split(theLine)
            if len(args) != len(cliArgos):
                _HANDLE_ERROR('Wrong number of arguments')
            else:
                try:
                    return f(self, *[x._(y) for x, y in zip(args, cliArgos)])
                except ValueError:
                    _HANDLE_ERROR('Wrong type of argument')
                except OverflowError:
                    _HANDLE_ERROR('Overflow value for argument')

        return _wrapper

    return f_arguments


def defaults(*args):
    """Decorator that provide type and default value for every argument.
    """

    def f_defaults(f):

        @wraps(f)
        def _wrapper(self, theLine):
            cliArgos = shlex.split(theLine)
            if len(args) < len(cliArgos):
                return _HANDLE_ERROR('Wrong number of arguments')
            else:
                try:
                    return f(self, *[x._(z) if z is not None else y for (x, y), z in map(None, args, cliArgos)])
                except ValueError:
                    _HANDLE_ERROR('Wrong type of argument')
                except OverflowError:
                    _HANDLE_ERROR('Overflow value for argument')

        return _wrapper

    return f_defaults


def argo(theName, theType, theDefault):
    """Decorator that provides to add an argument to a command.
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
                return _HANDLE_ERROR('Mandatory argument is not present')

    return _wrapper


def setdictos(f):
    """Decorator that setup all argument as named for a command.
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
                return _HANDLE_ERROR('Mandatory argument is not present"')

    return _wrapper


def syntax(theSyntax):
    """Decorator that setup the command syntax
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
    """

    @wraps(f)
    def _wrapper(self, theLine):

        cmdArgos, cliArgos = _getCmdAndCliArgos(f, self, theLine)

        root = getattr(f, TREE_ATTR, None)
        rules = getattr(f, RULES_ATTR, None)
        if len(cliArgos) < RuleHandler.syntaxMinArgs(rules):
            return _HANDLE_ERROR("Error: Number of Args: Too few arguments")

        useArgs = _mapPassedArgosToCommandArgos(root, cmdArgos, cliArgos)
        if all(map(lambda x: x is not None, useArgs)):
            return f(self, *useArgs)
        else:
            return _HANDLE_ERROR('Error: Mandatory argument is not present"')

    _buildCommandParsingTree(f)
    return _wrapper


def command(theModule):
    """Decorator that setup a function as a command.
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
