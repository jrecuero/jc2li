import os
from cmd import Cmd
import shlex
import loggerator


logger = loggerator.getLoggerator('base')


class CliBase(Cmd, object):
    """CliBase class is the base class for any class that will implement
    commands to be used by the command line interface.
    """

    @classmethod
    def extend(cls, name, func):
        """Class method that allows to extend the class with new commands.

        Args:
            name (str) : name for the new command.
            func (function) : function for the new command.

        Returns:
            boolean : True if command was added, False, else
        """
        funcName = 'do_{}'.format(name)
        if getattr(cls, funcName, None):
            return False
        setattr(cls, 'do_{}'.format(name), func)
        return True

    @classmethod
    def extends(cls, cmds):
        """Class method that allows to extend the class with the list of
        commands given.

        Args:
            cmds (list) : list of dictionaries with name and function for
            every command.

        Returns:
            list : list of booleans, with True for every command being
            added and False for those which failed.
        """
        rets = {}
        for c in cmds:
            rets.update({c['name']: cls.extend(c['name'], c['cmd'])})
        return rets

    def emptyline(self):
        """Method that don't provide any action when <CR> is entered in an
        empty line.

        By default, the same command is executed when just <CR> is entered,
        but we don't want that behavior.
        """
        pass

    def do_exit(self, line):
        """Command that exit the CLI when "exit" is entered.

        Args:
            line (str): string entered in the command line.
        """
        return True

    def do_EOF(self, line):
        """Exit the CLI with <CTRL-D>

        Args:
            line (str): string entered in the command line.
        """
        return True

    def do_custom_help(self, line):
        """Help to be displayed for "custom" command.

        Args:
            line (str): string entered in the command line.
        """
        print "Custom Help for {}".format(line)

    def do_shell(self, line):
        """Comand that runs a shell command when "shell" is entered.

        Args:
            line (str): string entered in the command line.
        """
        print "running shell command:", line
        output = os.popen(line).read()
        print output

    def precmd(self, line):
        """Method to be called before any command is being processed.

        In this case, it will allow to replace "-" with "_", so
        commands can use "-" character.

        Args:
            line (str): string entered in the command line.
        """
        if line:
            listline = line.split()
            if '-' in listline[0]:
                listline[0] = listline[0].replace('-', '_')
            newline = ' '.join(listline)
        else:
            newline = line
        return super(CliBase, self).precmd(newline)

    def onecmd(self, str):
        try:
            return super(CliBase, self).onecmd(str)
        except Exception as ex:
            logger.display(ex.message)

    def printHelp(self, text, line, help):
        """Displays help.

        Args:
            text (str): last token entered
            line (str): string entered in the command line.
            help (str): help strin to be displayed
        """
        if help:
            print help
            print self.prompt + line,

    def getCompleteArgs(self, text, line, command):
        """Custom completer for the given command.

        This method will provide help and completion when entering arguments
        for the given command.

        Args:
            text (str): last token entered
            line (str): string entered in the command line.
            command (function): completer for the given command to be called
            to complete possible arguemnts.
        """
        linelist = shlex.split(line)
        processArgoNo = len(linelist) - 1
        linelastchat = line[-1]
        if linelastchat == ' ':
            processArgoNo += 1
        dictargs = getattr(command, '_arguments', None)
        if dictargs:
            argotype = dictargs[processArgoNo - 1]['type']
        else:
            argotype = None
        return processArgoNo, argotype
