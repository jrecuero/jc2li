from commands import Cli
import os
from importlib import import_module
import readline
import loggerator


class Completer(object):
    """Completer Class provides a completer for a command.
    """

    def __init__(self, old):
        self.old = old

    def complete(self, text, state):
        if '-' in text:
            text = text.replace('-', '_')
        return self.old(text, state)


if __name__ == '__main__':
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

    # old_delims = readline.get_completer_delims()
    # readline.set_completer(new_completer)
    # readline.set_completer_delims(old_delims.replace('-', '_'))

    logger = loggerator.getLoggerator('cli')
    logger.info("CLI APPLICATION", extended=(('FG', 'BLUE'), ('BG', 'YELLOW'), ))
    logger.info("---------------", "RED")

    directory = 'extended'
    files = [f[:-3] for f in os.listdir(directory) if ('.py' == f[-3:])]
    for f in files:
        mod = import_module('{}.{}'.format(directory, f))
        if getattr(mod, 'TO_EXTEND', None):
            Cli.extends(mod.TO_EXTEND)
    cli = Cli()
    completer = Completer(cli.complete)
    cli.complete  = completer.complete
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print ""
        pass
    # cli.do_tenant("COMMON 1")
    # cli.do_node("common nsig='jose'")
