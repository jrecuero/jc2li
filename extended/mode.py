from base import Cli


class Mode(Cli):

    def do_command(self, line):
        """Command inside a mode.
        """
        print 'this is a command'
