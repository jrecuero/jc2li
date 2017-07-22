from collections import OrderedDict


def _HANDLE_ERROR(st):
    print st
    return None


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


if __name__ == '__main__':
    pass
