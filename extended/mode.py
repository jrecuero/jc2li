from base import CliBase


class Mode(CliBase):

    def do_command(self, line):
        """Command inside a mode.
        """
        print 'this is a command'
