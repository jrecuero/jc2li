from functools import wraps
import shlex
from collections import OrderedDict
import cliparser


def _checkArgNameInRule(rule, argname):
    if rule['type'] == '1' and rule['args'] == argname:
        return True
    return False


def _syntaxMinArgs(rules):
    counter = sum([1 if rule['type'] in '1+' else 0 for rule in rules])
    return counter


def _HANDLE_ERROR(st):
    print st
    return None


def lineSplit(line, instr=False):
    """Split line in arguments.
    TODO: Use shlex.split() method instead of.
    """
    part = line.partition('"')
    if '"' in part[1]:
        if instr:
            return [part[0]] + lineSplit(part[2], False)
        else:
            return part[0].split() + lineSplit(part[2], True)
    else:
        return part[0].split()


def linesplit(f):

    @wraps(f)
    def _wrapper(self, line):
        return f(self, shlex.split(line))

    return _wrapper


def params(*args):
    """Decorator that provides a gross mode for default values.
    """

    def f_params(f):

        @wraps(f)
        def _wrapper(self, line):
            passArgs = shlex.split(line)
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
        def _wrapper(self, line):
            passargs = shlex.split(line)
            if len(args) != len(passargs):
                _HANDLE_ERROR('Wrong number of arguments')
            else:
                try:
                    return f(self, *[x._(y) for x, y in zip(args, passargs)])
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
        def _wrapper(self, line):
            passargs = shlex.split(line)
            if len(args) < len(passargs):
                return _HANDLE_ERROR('Wrong number of arguments')
            else:
                try:
                    return f(self, *[x._(z) if z is not None else y for (x, y), z in map(None, args, passargs)])
                except ValueError:
                    _HANDLE_ERROR('Wrong type of argument')
                except OverflowError:
                    _HANDLE_ERROR('Overflow value for argument')

        return _wrapper

    return f_defaults


def argo(thename, thetype, thedefault):
    """Decorator that provides to add an argument to a command.
    """

    def f_argo(f):

        @wraps(f)
        def _wrapper(self, *args):
            return f(self, *args)
        fargs = getattr(_wrapper, '_arguments', [])
        fargs.insert(0, {'name': thename, 'type': thetype, 'default': thedefault})
        setattr(_wrapper, '_arguments', fargs)

        return _wrapper

    return f_argo


def argos(theargos):
    """Decorator that provides to create a group of arguments to a command.
    """

    def f_setjson(f):

        @wraps(f)
        def _wrapper(self, *args):
            return f(self, *args)

        fargs = getattr(_wrapper, '_arguments', [])
        for arg in reversed(theargos):
            fargs.insert(0, arg)
        setattr(_wrapper, '_arguments', fargs)
        return _wrapper

    return f_setjson


def setargos(f):
    """Decorator that setup all argument for a command.
    """

    @wraps(f)
    def _wrapper(self, line):
        fargs = getattr(f, '_arguments', None)
        if fargs is None:
            return f(self, line)
        else:
            passargs = shlex.split(line)
            defargs = [(x['type'], x['default']) for x in fargs]
            useargs = [x._(z) if z is not None else y for (x, y), z in map(None, defargs, passargs)]
            if all(map(lambda x: x is not None, useargs)):
                return f(self, *useargs)
            else:
                return _HANDLE_ERROR('Mandatory argument is not present')

    return _wrapper


def setdictos(f):
    """Decorator that setup all argument as named for a command.
    """

    @wraps(f)
    def _wrapper(self, line):
        fargs = getattr(f, '_arguments', None)
        if fargs is None:
            return f(self, line)
        else:
            passargs = shlex.split(line)
            dictargs = OrderedDict()
            for x in fargs:
                dictargs.update({x['name']: {'type': x['type'], 'value': x['default']}})
            for index, passarg in enumerate(passargs):
                if '=' in passarg:
                    argname, argvalue = passarg.split('=')
                    argentry = dictargs.get(argname, None)
                    if argentry is not None:
                        argentry['value'] = argentry['type']._(argvalue)
                else:
                    entry = fargs[index]
                    dictargs[entry['name']]['value'] = entry['type']._(passarg)
            useargs = [y['value'] for x, y in dictargs.items()]
            if all(map(lambda x: x is not None, useargs)):
                return f(self, *useargs)
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
    def _wrapper(self, line):
        fargs = getattr(f, '_arguments', None)
        if fargs is None:
            return f(self, line)
        passargs = shlex.split(line)
        rules = getattr(f, '_rules', None)
        if len(passargs) < _syntaxMinArgs(rules):
            return _HANDLE_ERROR("Error: Number of Args: Too few arguments")
        dictargs = OrderedDict()
        for x in fargs:
            dictargs.update({x['name']: {'type': x['type'],
                                         'value': x['default'],
                                         'matched': 0, }})
        ruleIndex = 0
        listKeys = list(dictargs)
        foundCounter = 0
        for index, passarg in enumerate(passargs):
            rule = rules[ruleIndex]
            if rule['type'] == '0':
                return _HANDLE_ERROR("Error: End rule found: Too many arguments")
            elif rule['type'] == '1':
                key = listKeys[index]
                dictargs[key]['value'] = dictargs[key]['type']._(passarg)
                dictargs[key]['matched'] = 1
            # elif rule['type'] == '?':
            else:
                if '=' in passarg:
                    argname, argvalue = passarg.split('=')
                    argRules = rule['args']
                    found = False
                    for travRule in argRules:
                        if _checkArgNameInRule(travRule, argname):
                            argentry = dictargs.get(argname, None)
                            if argentry is not None:
                                if argentry['matched'] == 0:
                                    argentry['value'] = argentry['type']._(argvalue)
                                elif argentry['matched'] == 1:
                                    argentry['value'] = [argentry['value'],
                                                         argentry['type']._(argvalue)]
                                else:
                                    argentry['value'].append(argentry['type']._(argvalue))
                                argentry['matched'] += 1
                            found = True
                            foundCounter += 1
                            break
                    if rule['type'] == '?' and found and foundCounter > 1:
                        return _HANDLE_ERROR('Error: Too many arguments')
                    elif rule['type'] == '+' and foundCounter == 0:
                        return _HANDLE_ERROR('Error: too few arguments')
                else:
                    return _HANDLE_ERROR('Error: Invalid named argument')
            if (rule['type'] in '1?') or \
               (rule['type'] in '*+' and not found):
                ruleIndex += 1
                foundCounter = 0
        useargs = [y['value'] for x, y in dictargs.items()]
        if all(map(lambda x: x is not None, useargs)):
            return f(self, *useargs)
        else:
            return _HANDLE_ERROR('Error: Mandatory argument is not present"')

    return _wrapper


def command(module):
    """Decorator that setup a function as a command.
    """

    def f_command(f):

        @wraps(f)
        def _wrapper(self, line):
            return f(self, line)

        module.extend(f.func_name, _wrapper)
        return _wrapper

    return f_command


def mode(parent, module, prompt=None):
    """Decorator that setup a function as a mode.
    """

    if prompt is None:
        prompt = module.__name__

    def f_command(f):

        @wraps(f)
        def _wrapper(self, line):
            return f(self, line)
            mode = module()
            mode.prompt = '({}) '.format(prompt)
            mode.cmdloop()

        parent.extend(f.func_name, _wrapper)
        return _wrapper

    return f_command
