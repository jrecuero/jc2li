import os
from cmd import Cmd
import shlex


class CliBase(Cmd, object):

    @classmethod
    def extend(cls, name, func):
        funcName = 'do_{}'.format(name)
        if getattr(cls, funcName, None):
            return False
        setattr(cls, 'do_{}'.format(name), func)
        return True

    @classmethod
    def extends(cls, cmds):
        rets = {}
        for c in cmds:
            rets.update({c['name']: cls.extend(c['name'], c['cmd'])})
        return rets

    def emptyline(self):
        pass

    def do_exit(self, line):
        """Exit."""
        return True

    def do_custom_help(self, line):
        """Custom help."""
        print "Custom Help for {}".format(line)

    def do_EOF(self, line):
        """Exit."""
        return True

    def do_shell(self, line):
        "Run a shell command"
        print "running shell command:", line
        output = os.popen(line).read()
        print output

    def precmd(self, line):
        if line:
            listline = line.split()
            if '-' in listline[0]:
                listline[0] = listline[0].replace('-', '_')
            newline = ' '.join(listline)
        else:
            newline = line
        return super(CliBase, self).precmd(newline)

    def printHelp(self, text, line, help):
        if help:
            print help
            print self.prompt + line,

    def getCompleteArgs(self, text, line, command):
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
