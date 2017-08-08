from base import CliBase
from argtypes import Int, Str
import shlex
from decorators import params, arguments, defaults, argo, setargos, setdictos
from decorators import syntax, setsyntax

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
        self.addCmd('cli', self.do_cli)
        self.addCmd('the-name', self.do_thename)
        self.addCmd('command', self.do_command)
        self.addCmd('card', self.do_card)
        self.addCmd('dict-card', self.do_dictocard)
        self.addCmd('enter', self.do_enter)
        self.addCmd('node', self.do_node)
        self.addCmd('tenant', self.do_tenant)

    def do_cli(self, line):
        """This is the basic CLI command.
        \n\t(Cmd) cli arg1 arg2 arg3 ...
        """
        print 'cli arguments: {}'.format(shlex.split(line))

    @params("CLI command", 0)
    def do_thename(self, name, id):
        """Set a name and id.
        """
        print 'You entered name: {} and id: {}'.format(name, id)

    @arguments(Int, Str, Age)
    def do_command(self, id, name, age):
        """Command with typed arguments.
        """
        print 'id: {}, name: {}, age: {}'.format(id, name, age)

    @defaults((Int, 0), (Str, 'no name'), (Age, 30))
    def do_card(self, id, name, age):
        """Command with default typed arguments.
        """
        print 'CARD id: {}, name: {}, age: {}'.format(id, name, age)

    @setargos
    @argo('id', Int, 0)
    @argo('name', Str, 'jose carlos')
    @argo('age', Age, 30)
    def do_thecard(self, id, name, age):
        """Command with  arguments as decorators.
        """
        print 'THE CARD id: {}, name: {}, age: {}'.format(id, name, age)

    @setdictos
    @argo('id', Int, 0)
    @argo('name', Str, 'jose carlos')
    @argo('age', Age, 30)
    def do_dictocard(self, id, name, age):
        """Command with arguments as dictionary decorators.
        """
        print 'DICTO CARD id: {}, name: {}, age: {}'.format(id, name, age)

    # @setdictos
    # @argos(argsdata['nameid'])
    # def do_jsoncard(self, id, name):
    #     """Command with arguments as json decorators.
    #     """
    #     print 'JSON CARD id: {}, name: {}'.format(id, name)

    # @setdictos
    # @argos(argsdata['nameid'])
    # @argo('age', Age, 30)
    # def do_jsoncard2(self, id, name, age):
    #     """Command with arguments as json decorators.
    #     """
    #     print 'JSON CARD 2 id: {}, name: {}, age: {}'.format(id, name, age)

    # @setdictos
    # @argo('nat', Str, "american")
    # @argos(argsdata['nameid'])
    # @argo('age', Age, 30)
    # def do_jsoncard3(self, nat, id, name, age):
    #     """Command with arguments as json decorators.
    #     """
    #     print 'JSON CARD 3 nationality: {}, id: {}, name: {}, age: {}'.format(nat, id, name, age)

    @setdictos
    @argo('place', Room(["garage", "yard"]), "garage")
    @argo('id', Int(), 0)
    def do_enter(self, place, id):
        """Enter in a place command.
        """
        print 'Enter in {} at {}'.format(place, id)

    @setsyntax
    @syntax("node name [nid|nsig]?")
    @argo('name', Str, None)
    @argo('nid', Int, 0)
    @argo('nsig', Int, 0)
    def do_node(self, name, nid, nsig):
        print name, nid, nsig

    @syntax("tenant tname [tid]?")
    @setdictos
    @argo('tname', Str, None)
    @argo('tid', Int, 0)
    def do_tenant(self, tname, tid):
        print self.do_tenant._Syntax
        print self.do_tenant._Cmd
        print self.do_tenant._Rules
        print tname, tid


if __name__ == "__main__":
    pass
