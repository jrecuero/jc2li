from decorators import command, mode, setargos, argo, setdictos
from argtypes import Int, Str
from commands import CliCommands
from mode import Mode


def look(self, line):
    """Look around.
    """
    print 'This is an extended method: look'


def take(self, line):
    """Take something.
    """
    print 'This is an extended method: take'


def inmode(self, line):
    """Enter in a mode.
    """
    inmode = Mode()
    inmode.prompt = '(in-mode) '
    inmode.cmdloop()


@mode(CliCommands, Mode, 'inner-mode')
def innermode(self, line):
    """Mode defined with @mode decorator.
    """
    print 'Running inner mode'


@mode(CliCommands, Mode)
def defaultmode(self, line):
    """Mode defined with @mode decorator.
    """
    print 'Running default mode'


@command(Mode)
def up(self, line):
    """This is mode command defined in the parent.
    """
    print 'Command defined in parent'


@command(CliCommands)
def sit(self, line):
    """This is a command defined.
    """
    print 'Command defined'


@command(CliCommands)
@setargos
@argo('name', Str, 'no name')
@argo('place', Str, 'no place')
def down(self, name, place):
    """Down command
    """
    print 'Down Command: {} in {}'.format(name, place)


@command(CliCommands)
@setdictos
@argo('id', Int, None)
@argo('name', Str, 'no name')
def left(self, id, name):
    """Left command
    """
    print 'Left Command [{}] : {}'.format(id, name)


@command(CliCommands)
@setargos
@argo('id', Int, None)
@argo('name', Str, None)
def right(self, id, name):
    """Right command
    """
    print 'Right Command [{}] : {}'.format(id, name)


TO_EXTEND = [{'name': 'look', 'cmd': look},
             {'name': 'take', 'cmd': take},
             {'name': 'inmode', 'cmd': inmode}]
