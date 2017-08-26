from base import Cli
from argtypes import CliType, Int, Str
import shlex
from decorators import argo, syntax, setsyntax
import loggerator

MODULE = 'COMMANDS'
logger = loggerator.getLoggerator('base')

# import os
# sys.path.append(os.path.join('/Users/jorecuer', 'Repository/winpdb'))
# import rpdb2
# rpdb2.start_embedded_debugger("yaci")


class Tenant(CliType):

    DEFAULT = ["COMMON", "DEFAULT", "SINGLE", "MULTI"]

    def __init__(self, **kwargs):
        """Tenant class initialization method.
        """
        super(Tenant, self).__init__(**kwargs)
        tenants = kwargs.get('theTenants', None)
        self._tenants = tenants if tenants else Tenant.DEFAULT

    def _helpStr(self):
        """Method that should return default string to be displayed as help.

        Returns:
            str : string with default help.
        """
        return 'Enter the Tenant where you want to go.'

    def complete(self, text):
        """Method that returns the completion for the given argument.

        Args:
            text (str): last token in the line being entered.

        Returns:
            str : string with completion to send to the display.
        """
        if not text:
            return self._tenants
        else:
            return [x for x in self._tenants if x.startswith(text)]


class CliCommands(Cli):

    @Cli.command('the-cli')
    def do_cli(self, line):
        """This is the basic CLI command:\t(Cmd) cli arg1 arg2 arg3 ...
        """
        print('cli arguments: {}'.format(shlex.split(line)))

    @Cli.command('the-command')
    @setsyntax
    @syntax("the-command [info|tid]?")
    @argo('info', Str, "solo")
    @argo('tid', Int, 0)
    def do_command(self, info, tid):
        """This is the basic CLI command.
        """
        print('command arguments: {}'.format((info, tid)))

    @Cli.command('node')
    @setsyntax
    @syntax("node name [nid|nsig]?")
    @argo('name', Str, None)
    @argo('nid', Int, 0)
    @argo('nsig', Int, 0)
    def do_node(self, name, nid, nsig):
        """Just display a node.
        """
        print('Running the node')
        print(name, nid, nsig)

    @Cli.command('tenant')
    @setsyntax
    @syntax("tenant tname [tid]?")
    @argo('tname', Tenant, None)
    @argo('tid', Int, 0)
    def do_tenant(self, tname, tid):
        """Display tenant information.
        """
        print(tname, tid)


if __name__ == "__main__":
    pass
