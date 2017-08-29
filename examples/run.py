import sys
cliPath = '..'
sys.path.append(cliPath)

from base import Cli
from argtypes import Int, Str
from decorators import argo, syntax, setsyntax


class RunCli(Cli):

    def setupCmds(self):
        super(RunCli, self).setupCmds()

    def do_start(self, theLine):
        print('start application with {0}'.format(theLine))

    @Cli.command()
    @setsyntax
    @syntax("run name [version]?")
    @argo('name', Str, None)
    @argo('version', Int, 0)
    def do_run(self, name, version):
        print("run application {0} version{1}".format(name, version))

    @Cli.command()
    @setsyntax
    @syntax("play name")
    @argo('name', Str, None)
    def do_play(self, name):
        print("play {0}".format(name))
        playCli = RunCli()
        try:
            playCli.cmdloop('PLAY# ')
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    cli = RunCli()
    try:
        cli.cmdloop('RUN# ')
    except KeyboardInterrupt:
        pass
