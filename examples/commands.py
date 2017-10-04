from cli import Cli
from argtypes import CliType, Int, Str
import shlex
from decorators import argo, syntax, setsyntax
import loggerator

MODULE = 'CliCommands'
LOGGER = loggerator.getLoggerator(MODULE)

# import sys
# import os
# sys.path.append(os.path.join('/Users/jorecuer', 'Repository/winpdb-1.4.8'))
# import rpdb2
# rpdb2.start_embedded_debugger("jc2li")


class T_Tenant(CliType):

    DEFAULT = ["COMMON", "DEFAULT", "SINGLE", "MULTI"]

    def __init__(self, **kwargs):
        super(T_Tenant, self).__init__(**kwargs)
        self._tenants = T_Tenant.DEFAULT

    def _help_str(self):
        return 'Enter the Tenant where you want to go.'

    def get_complete_list(self, document, text):
        _tenants = self.argo.journal.get_from_cache('tenants')
        if _tenants is not None:
            self._tenants = _tenants
        return self._tenants


class T_System(CliType):

    def __init__(self, **kwargs):
        super(T_System, self).__init__(**kwargs)
        self._systems = kwargs.get('systems', [])

    def _help_str(self):
        return 'Enter the system name'

    def get_complete_list(self, document, text):
        LOGGER.debug('calling get_complete_list and return {0}'.format(self._systems), 'YELLOW')
        return self._systems


class CliCommands(Cli):

    def __init__(self):
        super(CliCommands, self).__init__()
        self.journal.set_to_cache('tenants', ["COMMON", "COMMONALITY", "COMMONWARE", "COMMUT"])

    @Cli.command('the-cli')
    def do_cli(self, line):
        """This is the basic CLI command:\t(Cmd) cli arg1 arg2 arg3 ...
        """
        print('cli arguments: {}'.format(shlex.split(line)))

    @Cli.command('the-command')
    @setsyntax
    @syntax("the-command [tid]?")
    @argo('tid', Int, 0)
    def do_command(self, info):
        """This is the basic CLI command.
        """
        print('command arguments: {}'.format((info)))

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
    @argo('tname', T_Tenant, None)
    @argo('tid', Int, 0)
    def do_tenant(self, tname, tid):
        """Display tenant information.
        """
        print(tname, tid)

    @Cli.command('interface')
    @setsyntax
    @syntax("interface name [iid|iname]!")
    @argo('name', T_Tenant, None)
    @argo('iid', Int, 0)
    @argo('iname', Str, 'if')
    def do_interface(self, name, iid, iname):
        """Display tenant information.
        """
        print('interface is {0} {1} | {2}'.format(name, iid, iname))

    @Cli.command('leaf')
    @setsyntax
    @syntax('leaf name [lid laddr]+')
    @argo('name', Str, None)
    @argo('lid', Int, "1")
    @argo('laddr', Int, "0")
    def do_leaf(self, name, lid, laddr):
        """Display leaf information.
        """
        print('leaf {0} has id {1} with address {2}'.format(name, lid, laddr))

    @Cli.command()
    @setsyntax
    @syntax('spine name [sid saddr]?')
    @argo('name', Str, None)
    @argo('sid', Int, "0")
    @argo('saddr', Str, "1.1.1.1")
    def do_spine(self, name, sid, saddr):
        """Display spine information.
        """
        print('spine {0} has id {1} with address {2}'.format(name, sid, saddr))

    @Cli.command()
    @setsyntax
    @syntax('config name [tname | system]?')
    @argo('name', Str, None)
    @argo('tname', T_Tenant, 'COMMON')
    @argo('system', T_System, 'localhost', completer_kwargs={'systems': ['localhost', 'remote']})
    def do_configure(self, name, tname, system):
        """Display tenant or system configuration.
        """
        print('configure {0} tenant {1} or system {2}'.format(name, tname, system))

    @Cli.command()
    @setsyntax
    @syntax('dbg name [options]@')
    @argo('name', Str, None)
    @argo('options', Str, 'None')
    def do_dbg(self, name, options):
        """Display dbg information
        """
        print('dbg {0} options {1}'.format(name, options))
