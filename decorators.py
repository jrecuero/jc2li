__docformat__ = 'restructuredtext en'

#------------------------------------------------------------------------------
#  _                            _
# (_)_ __ ___  _ __   ___  _ __| |_ ___
# | | '_ ` _ \| '_ \ / _ \| '__| __/ __|
# | | | | | | | |_) | (_) | |  | |_\__ \
# |_|_| |_| |_| .__/ \___/|_|   \__|___/
#             |_|
#------------------------------------------------------------------------------
#
from functools import wraps
import cliparser
from arguments import Argument, Arguments
from common import ARGOS_ATTR, RULES_ATTR, SYNTAX_ATTR, CMD_ATTR, TREE_ATTR
from journal import Journal
import shlex


#------------------------------------------------------------------------------
#
#   ___ ___  _ __  ___| |_ __ _ _ __ | |_ ___
#  / __/ _ \| '_ \/ __| __/ _` | '_ \| __/ __|
# | (_| (_) | | | \__ \ || (_| | | | | |_\__ \
#  \___\___/|_| |_|___/\__\__,_|_| |_|\__|___/
#
#------------------------------------------------------------------------------
#
MODULE = 'CLI.decorator'


#------------------------------------------------------------------------------
#            _                     _   _
#  ___ _   _| |__  _ __ ___  _   _| |_(_)_ __   ___  ___
# / __| | | | '_ \| '__/ _ \| | | | __| | '_ \ / _ \/ __|
# \__ \ |_| | |_) | | | (_) | |_| | |_| | | | |  __/\__ \
# |___/\__,_|_.__/|_|  \___/ \__,_|\__|_|_| |_|\___||___/
#
#------------------------------------------------------------------------------
#
def argo(name, type, default, **kwargs):
    """Decorator that provides to add an argument to a command.

    Args:
        name (str) : argument name. This will be used when making any
        reference to this argument
        type (object) : argument type, it should be a class name.
        default (object) : default value for the argument.
        completer (object) : argument completer instance

    Returns:
        func : Function wrapper.
    """

    def f_argo(f):

        @wraps(f)
        def _wrapper(self, *args):
            return f(self, *args)
        cmd_argos = getattr(_wrapper, ARGOS_ATTR, Arguments())
        kwargs.setdefault('default', default)
        cmd_argos.insert_argument(Argument(name, type, **kwargs))
        setattr(_wrapper, ARGOS_ATTR, cmd_argos)

        return _wrapper

    return f_argo


def argos(arg_list):
    """Decorator that provides to create a group of arguments to a command.

    Args:
        arg_list (list) : list of arguments configured as @argo.

    Returns:
        func : Function wrapper.
    """

    def f_setargos(f):

        @wraps(f)
        def _wrapper(self, *args):
            return f(self, *args)

        cmd_argos = getattr(_wrapper, ARGOS_ATTR, Arguments())
        for arg in reversed(arg_list):
            cmd_argos.insert_argument(Argument(arg['name'], arg['type'], default=arg['default']))
        setattr(_wrapper, ARGOS_ATTR, cmd_argos)
        return _wrapper

    return f_setargos


def syntax(syntax_str):
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

    - <arg-name> is the argument name that is provided in teh @argo decorator.

    - Several optional arguments can be defined, usign "|" to separate
        them. For example: [ arg1 | arg2 ]? defines taht arg1 or arg2 or no
        argument should be entered at that point. This can be used only for
        argument defined wit "?", "*" or "+"

    Args:
        syntax_str (str) : string with the command syntax.

    Returns:
        func : Function wrapper.
    """

    def f_syntax(f):

        @wraps(f)
        def _wrapper(self, *args):
            return f(self, *args)

        cmd, rules = cliparser.process_syntax(syntax_str)
        setattr(_wrapper, SYNTAX_ATTR, syntax_str)
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

    Args:
        f (func) : Function to be decorated.

    Returns:
        func : Function wrapper.
    """

    journal = Journal()

    @wraps(f)
    def _wrapper(self, line):
        if getattr(f, RULES_ATTR, None) is None:
            use_args, cli_args = journal.build_command_arguments_from_args(f, line)
        else:
            cli_args = None
            use_args = journal.build_command_arguments_from_syntax(f, self, line)
        if use_args is not None:
            if cli_args:
                return f(self, *use_args, cli_args)
            else:
                return f(self, *use_args)

    if getattr(_wrapper, RULES_ATTR, None) is not None:
        root = journal.build_command_parsing_tree(f)
        setattr(_wrapper, TREE_ATTR, root)
    return _wrapper
