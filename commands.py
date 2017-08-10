from base import Cli
from argtypes import CliType, Int, Str
import shlex
from decorators import argo, syntax, setsyntax

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

    def setupCmds(self):
        """Register all commands to be used by the command line interface.

        Returns:
            None
        """
        super(CliCommands, self).setupCmds()
        # self.addCmd('cli', self.do_cli)
        # self.addCmd('node', self.do_node)
        # self.addCmd('tenant', self.do_tenant)

    @Cli.command('the-cli')
    def do_cli(self, line):
        """This is the basic CLI command.
        \n\t(Cmd) cli arg1 arg2 arg3 ...
        """
        print 'cli arguments: {}'.format(shlex.split(line))

    @Cli.command('the-command')
    def do_command(self, line):
        """This is the basic CLI command.
        \n\t(Cmd) cli arg1 arg2 arg3 ...
        """
        print 'command arguments: {}'.format(line)

    @Cli.command('node')
    @setsyntax
    @syntax("node name [nid|nsig]?")
    @argo('name', Str, None)
    @argo('nid', Int, 0)
    @argo('nsig', Int, 0)
    def do_node(self, name, nid, nsig):
        print 'Running the node'
        print name, nid, nsig

    @Cli.command('tenant')
    @setsyntax
    @syntax("tenant tname [tid]?")
    @argo('tname', Tenant, None)
    @argo('tid', Int, 0)
    def do_tenant(self, tname, tid):
        print tname, tid


if __name__ == "__main__":
    pass
