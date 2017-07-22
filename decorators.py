from functools import wraps
import shlex
import cliparser
from common import _HANDLE_ERROR, Argument, Arguments


def _checkForInnerRule(thRule):
    return thRule['type'] in '?*+' or type(thRule['args']) == list


def _checkArgNameInRule(thRule, theArgname):
    if thRule['type'] == '1' and thRule['args'] == theArgname:
        return True
    return False


def _syntaxMinArgs(theRules):
    counter = sum([1 if rule['type'] in '1+' else 0 for rule in theRules])
    return counter


def _processInnerRule(theRule, thePassArg, theArgs, theFoundCounter):
    argName, argValue = thePassArg.split('=')
    argRules = theRule['args'] if type(theRule['args']) == list else [theRule, ]
    found = False
    for travRule in argRules:
        if _checkForInnerRule(travRule):
            for innerRule in travRule['args']:
                found, theFoundCounter = _processInnerRule(innerRule, thePassArg, theArgs, theFoundCounter)
                if found:
                    break
        elif _checkArgNameInRule(travRule, argName):
            argEntry = theArgs.getArgoFromName(argName)
            if argEntry is not None:
                if argEntry.Matched == 0:
                    argEntry.Value = argEntry.Type._(argValue)
                elif argEntry.Matched == 1:
                    argEntry.Value = [argEntry.Value, argEntry.Type._(argValue)]
                else:
                    argEntry.Value.append(argEntry.Type._(argValue))
                argEntry.Matched += 1
            found = True
            theFoundCounter += 1
        if found:
            break
    if theRule['type'] == '+' and theFoundCounter == 0:
        return _HANDLE_ERROR('Error: too few arguments'), None
    return found, theFoundCounter


def _checkMoveToNextRule(theRule, theFound):
    return (theRule['type'] in '1?') or (theRule['type'] in '*+' and not theFound)


def lineSplit(theLine, theInstr=False):
    """Split theLine in arguments.
    TODO: Use shlex.split() method instead of.
    """
    part = theLine.partition('"')
    if '"' in part[1]:
        if theInstr:
            return [part[0]] + lineSplit(part[2], False)
        else:
            return part[0].split() + lineSplit(part[2], True)
    else:
        return part[0].split()


def linesplit(f):

    @wraps(f)
    def _wrapper(self, theLine):
        return f(self, shlex.split(theLine))

    return _wrapper


def params(*args):
    """Decorator that provides a gross mode for default values.
    """

    def f_params(f):

        @wraps(f)
        def _wrapper(self, theLine):
            passArgs = shlex.split(theLine)
            useArgs = list(args)
            try:
                for i, v in enumerate(passArgs):
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
            passArgs = shlex.split(theLine)
            if len(args) != len(passArgs):
                _HANDLE_ERROR('Wrong number of arguments')
            else:
                try:
                    return f(self, *[x._(y) for x, y in zip(args, passArgs)])
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
            passArgs = shlex.split(theLine)
            if len(args) < len(passArgs):
                return _HANDLE_ERROR('Wrong number of arguments')
            else:
                try:
                    return f(self, *[x._(z) if z is not None else y for (x, y), z in map(None, args, passArgs)])
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
        fArgs = getattr(_wrapper, '_Arguments', Arguments())
        fArgs.insertArgument(Argument(theName, theType, theDefault))
        setattr(_wrapper, '_Arguments', fArgs)

        return _wrapper

    return f_argo


def argos(theArgos):
    """Decorator that provides to create a group of arguments to a command.
    """

    def f_setargos(f):

        @wraps(f)
        def _wrapper(self, *args):
            return f(self, *args)

        fArgs = getattr(_wrapper, '_Arguments', Arguments())
        for arg in theArgos.reversed():
            fArgs.insert(arg)
        setattr(_wrapper, '_Arguments', fArgs)
        return _wrapper

    return f_setargos


def setargos(f):
    """Decorator that setup all argument for a command.
    """

    @wraps(f)
    def _wrapper(self, theLine):
        fArgs = getattr(f, '_Arguments', None)
        if fArgs is None:
            return f(self, theLine)
        else:
            fArgs.index()
            passArgs = shlex.split(theLine)
            defArgs = [(x.Type, x.Default) for x in fArgs.arguments]
            useArgs = [x._(z) if z is not None else y for (x, y), z in map(None, defArgs, passArgs)]
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
        fArgs = getattr(f, '_Arguments', None)
        if fArgs is None:
            return f(self, theLine)
        else:
            fArgs.index()
            passArgs = shlex.split(theLine)
            for index, passArg in enumerate(passArgs):
                if '=' in passArg:
                    argName, argValue = passArg.split('=')
                    argEntry = fArgs.getArgoFromName(argName)
                    if argEntry is not None:
                        argEntry.Value = argEntry.Type._(argValue)
                else:
                    entry = fArgs.getArgoFromIndex(index)
                    fArgs.setIndexedValueFromName(entry.Name, entry.Type._(passArg))
            useArgs = fArgs.getIndexedValues()
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
        setattr(_wrapper, '_syntax', theSyntax)
        setattr(_wrapper, '_cmd', cmd)
        setattr(_wrapper, '_rules', rules)

        return _wrapper

    return f_syntax


def setsyntax(f):
    """Decorator that setup the command syntax
    """

    @wraps(f)
    def _wrapper(self, theLine):
        fArgs = getattr(f, '_Arguments', None)
        if fArgs is None:
            return f(self, theLine)
        fArgs.index()
        passArgs = shlex.split(theLine)
        rules = getattr(f, '_rules', None)
        if len(passArgs) < _syntaxMinArgs(rules):
            return _HANDLE_ERROR("Error: Number of Args: Too few arguments")
        ruleIndex = 0
        foundCounter = 0
        for index, passArg in enumerate(passArgs):
            rule = rules[ruleIndex]
            found = False
            if rule['type'] == '0':
                return _HANDLE_ERROR("Error: End rule found: Too many arguments")
            elif rule['type'] == '1' and '=' not in passArg:
                matchArg = fArgs.getArgoFromIndex(index)
                fArgs.setIndexedValueFromIndex(index, matchArg.Type._(passArg))
                matchArg.Matched = 1
            else:
                if '=' in passArg:
                    found, foundCounter = _processInnerRule(rule, passArg, fArgs, foundCounter)
                else:
                    return _HANDLE_ERROR('Error: Invalid named argument')
            if not found:
                ruleIndex += 1
                foundCounter = 0
        useArgs = fArgs.getIndexedValues()
        if all(map(lambda x: x is not None, useArgs)):
            return f(self, *useArgs)
        else:
            return _HANDLE_ERROR('Error: Mandatory argument is not present"')

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
