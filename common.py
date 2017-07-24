from functools import wraps
import shlex
from collections import OrderedDict


def _HANDLE_ERROR(st):
    print st
    return None


def lineSplit(theLine, theInstr=False):
    """Split theLine in arguments.
    TODO: Use shlex.split() method instead of.
    """
    part = theLine.partition('"')
    if '"' in part[1]:
        if theInstr:
            return [part[0]] + lineSplit(part[2], False)
        else:
            return part[0].split() + lineSplit(part[2], True)
    else:
        return part[0].split()


def linesplit(f):

    @wraps(f)
    def _wrapper(self, theLine):
        return f(self, shlex.split(theLine))

    return _wrapper


def getPathFromLine(theLine):
    path = list()
    for arg in theLine:
        if '=' in arg:
            argName, _ = arg.split('=')
            path.append(argName)
        else:
            path.append(arg)
    return path


class Argument(object):

    def __init__(self, theName, theType, theDefault=None):
        self._name = theName
        self._type = theType
        self._default = theDefault
        self._value = theDefault
        self._matched = 0

    @property
    def Name(self):
        return self._name

    @property
    def Type(self):
        return self._type

    @property
    def Default(self):
        return self._default

    @property
    def Value(self):
        return self._value

    @Value.setter
    def Value(self, theValue):
        self._value = theValue

    @property
    def Matched(self):
        return self._matched

    @Matched.setter
    def Matched(self, theValue):
        self._matched = theValue


class Arguments(object):

    def __init__(self):
        self._arguments = []
        self._indexed = None

    @property
    def arguments(self):
        return self._arguments

    @property
    def Indexed(self):
        return self._indexed

    @Indexed.setter
    def Indexed(self, theValue):
        self._indexed = theValue

    def addArgument(self, theArgument):
        self.arguments.append(theArgument)

    def insertArgument(self, theArgument):
        self.arguments.insert(0, theArgument)

    def reversed(self):
        return reversed(self.arguments)

    def getArgoFromIndex(self, theIndex):
        return self.arguments[theIndex]

    def getArgoFromName(self, theName):
        return self.Indexed.get(theName, None)

    def index(self):
        self.Indexed = OrderedDict()
        for arg in self.arguments:
            arg.Value = arg.Default
            arg.Matched = 0
            self.Indexed.update({arg.Name: arg})

    def setIndexedValueFromIndex(self, theIndex, theValue):
        arg = self.getArgoFromIndex(theIndex)
        arg.Value = theValue

    def setIndexedValueFromName(self, theName, theValue):
        arg = self.getArgoFromName(theName)
        arg.Value = theValue

    def getIndexedValues(self):
        return [arg.Value for name, arg in self.Indexed.items()]

    def getNames(self):
        return list(self.Indexed)


class RuleHandler(object):

    @staticmethod
    def checkForInnerRule(theRule):
        return theRule['type'] in '?*+' or type(theRule['args']) == list

    @staticmethod
    def checkArgNameInRule(theRule, theArgname):
        if theRule['type'] == '1' and theRule['args'] == theArgname:
            return True
        return False

    @staticmethod
    def syntaxMinArgs(theRules):
        counter = sum([1 if rule['type'] in '1+' else 0 for rule in theRules])
        return counter

    @staticmethod
    def getArgsFromRuleAsList(theRule):
        return theRule['args'] if type(theRule['args']) == list else [theRule, ]

    @staticmethod
    def getArgsFromRule(theRule):
        return theRule['args']

    @staticmethod
    def getCounterFromRule(theRule):
        return theRule['counter']

    @staticmethod
    def traverseArgsInRule(theRule):
        for rule in theRule['args']:
            yield rule

    @staticmethod
    def isOnlyOneRule(theRule):
        return theRule['type'] == '1'

    @staticmethod
    def isEndRule(theRule):
        return theRule['type'] == '0'

    @staticmethod
    def isZeroOrOneRule(theRule):
        return theRule['type'] == '?'

    @staticmethod
    def isZeroOrMoreRule(theRule):
        return theRule['type'] == '*'

    @staticmethod
    def isOneOrMoreRule(theRule):
        return theRule['type'] == '+'


if __name__ == '__main__':
    pass
