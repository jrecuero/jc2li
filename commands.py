from base import CliBase
from argtypes import Int, Str
import shlex
from decorators import argo, syntax, setsyntax

# import os
# sys.path.append(os.path.join('/Users/jorecuer', 'Repository/winpdb'))
# import rpdb2
# rpdb2.start_embedded_debugger("yaci")

argsdata = {'nameid': [{'name': 'id', 'type': Int, 'default': 0},
                       {'name': 'name', 'type': Str, 'default': 'no name'}]}


class Age(object):

    @staticmethod
    def _(val):
        try:
            if 0 < int(val) < 100:
                return int(val)
            else:
                print 'Wrong age'
                raise OverflowError
        except ValueError:
                print 'Wrong value type for age'
                raise

    @staticmethod
    def help(text):
        return 'Enter and age'

    @staticmethod
    def type():
        return int


class Room(object):

    DEFAULT = ["bedroom", "hall", "kitchen", "saloon"]

    def __init__(self, rooms=None):
        self.rooms = rooms if rooms else Room.DEFAULT

    @staticmethod
    def _(val):
        return str(val)

    def help(self, text):
        if not text:
            return '\nEnter the Room where you want to go.\n{}'.format(self.rooms)
        else:
            return None

    def complete(self, text):
        if not text:
            return Room.rooms
        else:
            return [x for x in self.rooms if x.startswith(text)]

    @staticmethod
    def type():
        return str


class Cli(CliBase):

    def setupCmds(self):
        """Register all commands to be used by the command line interface.

        Returns:
            None
        """
        super(Cli, self).setupCmds()
        # self.addCmd('cli', self.do_cli)
        # self.addCmd('node', self.do_node)
        # self.addCmd('tenant', self.do_tenant)

    @CliBase.command('the-cli')
    def do_cli(self, line):
        """This is the basic CLI command.
        \n\t(Cmd) cli arg1 arg2 arg3 ...
        """
        print 'cli arguments: {}'.format(shlex.split(line))

    @CliBase.command('the-command')
    def do_command(self, line):
        """This is the basic CLI command.
        \n\t(Cmd) cli arg1 arg2 arg3 ...
        """
        print 'command arguments: {}'.format(line)

    @CliBase.command('node')
    @setsyntax
    @syntax("node name [nid|nsig]?")
    @argo('name', Str, None)
    @argo('nid', Int, 0)
    @argo('nsig', Int, 0)
    def do_node(self, name, nid, nsig):
        print 'Running the node'
        print name, nid, nsig

    @CliBase.command('tenant')
    @setsyntax
    @syntax("tenant tname [tid]?")
    @argo('tname', Str, None)
    @argo('tid', Int, 0)
    def do_tenant(self, tname, tid):
        print tname, tid


if __name__ == "__main__":
    pass
