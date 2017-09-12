from collections import OrderedDict


class Argument(object):
    """Argument class is used to store all information related with any unique
    command argument.

    It keeps the argument name, which will be used in the Command Line when it
    is entered by the user, the type of argument and the default value if no
    value is entered by the user.

    Moreover it keeps some other internal information like the actual value
    for the argument, and if the argument has already been entered, in which
    case it will be passed to the command function as a list.
    """

    def __init__(self, theName, theType, **kwargs):
        """Argument class initialization method.

        Args:
            theName (str) : String with the argument name.
            theType (type) : Argument type (class name).
            theDefault (object) : Default value for the argument.
            theCompleter (object) : Argument completer instance.

        Returns:
            None
        """
        self._name = theName
        self._type = theType
        self._default = kwargs.get('theDefault', None)
        self._value = kwargs.get('theDefault', None)
        completerKlass = kwargs.get('theCompleter', None)
        self._completer = completerKlass(theArgo=self) if completerKlass else theType(theArgo=self)
        self._matched = 0
        self._journal = None

    @property
    def Name(self):
        """Get property that returns the _name attribute.

        Returns:
            str : string with the argument name.
        """
        return self._name

    @property
    def Type(self):
        """Get property that returns the _type attribute.

        Returns:
            type : class for the argument name.
        """
        return self._type

    @property
    def Default(self):
        """Get property that returns the _default attribute.

        Returns:
            object : default value for the argument.
        """
        return self._default

    @property
    def Value(self):
        """Get property that returns the _value attribute.

        Returns:
            object : Default value for the argument.
        """
        return self._value

    @Value.setter
    def Value(self, theValue):
        """Set property that sets the value for the _value attribute.

        Args:
            theValue (object) : Value to set the _value attribute.

        Returns:
            None
        """
        self._value = theValue

    @property
    def Matched(self):
        """Get property that returns the _matched attribute.

        Returns:
            int : number of times the arguments was matched in the command line.
        """
        return self._matched

    @property
    def Journal(self):
        """Get property that returns the _journal attribute.

        Returns:
            Journal : journal instance.
        """
        return self._journal

    @Journal.setter
    def Journal(self, theValue):
        """Set property that set the value for the _journal attribute.

        Args:
            theValue (Journal) : journal instance.
        """
        self._journal = theValue

    @Matched.setter
    def Matched(self, theValue):
        """Set property that sets the value for the _matched attribute.

        Args:
            theValue (int) : number of times the arguments was matched.

        Returns :
            None
        """
        self._matched = theValue

    @property
    def Completer(self):
        """Get property that returns the _completer attribute.

        Returns:
            object : argument completer instance.
        """
        return self._completer

    @Completer.setter
    def Completer(self, theValue):
        """Set property that sets the value for the _completer attribute.

        Args:
            theValue (object) : new completer instance.

        Returns :
            None
        """
        self._completer = theValue


class Arguments(object):
    """Arguments class will store all arguments for a given command.
    It is basically composed by every single attribute the command can have,
    so arguments can be handle in a better and more generic way.

    It basically contains two lists, _arguments with an ordered list for the
    every argument being entered, and _indexed a list indexed by the attribute
    name for fast searching.
    """

    def __init__(self):
        """Arguments class initialization method.

        Returns:
            None:
        """
        self._arguments = []
        self._indexed = None

    @property
    def Arguments(self):
        """Get property that returns _argument attribute.

        Returns:
            list : list with all command arguments.
        """
        return self._arguments

    @property
    def Indexed(self):
        """Get property that returns _indexed attribute.

        Returns:
            list: list will all arguments indexed by argument name.
        """
        return self._indexed

    @Indexed.setter
    def Indexed(self, theValue):
        """Set property that sets the value for the _indexed attribute.
        """
        self._indexed = theValue

    def addArgument(self, theArgument):
        """Method that add a new argument.

        Args:
            theArgument (Argument) : New argument to the added.
        """
        self.Arguments.append(theArgument)

    def insertArgument(self, theArgument):
        """Method that insert a new argument the first in the list.

        Args:
            theArgument (Argument) : New argument to be inserted first.
        """
        self.Arguments.insert(0, theArgument)

    def reversed(self):
        """Method that returns the list of arguments in reverse order.

        Returns:
            list : List of argument reversed.
        """
        return reversed(self.Arguments)

    def getArgoFromIndex(self, theIndex):
        """Method that returns an argument at a given index.

        Index is the place where the argument is defined at the command
        level. They are stored in _arguments attribute.

        Args:
            theIndex (int) : Index for the argument to be returned

        Returns:
            Argument : Argument at the given index.
    """
        return self.Arguments[theIndex]

    def getArgoFromName(self, theName):
        """Method that returns an argument for the given name.

        Arguments indexed by name are store in _indexed attribute.

        Args:
            theName (str) : Name of the attribute to be retrieved.

        Returns:
            Argument/None : Argument instance if the name is found, None
            if the name is not found.
        """
        return self.Indexed.get(theName, None)

    def index(self):
        """Method that index Arguments instance. This method is required to be
        called every time a command maps CLI arguments into command arguments.

        This method initializes some internal Argument attributes (like Value
        Matched), so it has to be called every time we are matching a command.

        Returns:
            None
        """
        self.Indexed = OrderedDict()
        for arg in self.Arguments:
            arg.Value = arg.Default
            arg.Matched = 0
            self.Indexed.update({arg.Name: arg})

    def setIndexedValueFromIndex(self, theIndex, theValue):
        """Method that sets a new value for an argument at the
        given index.

        Index is the place where the argument is defined at the command
        level. They are stored in _arguments attribute.

        Args:
            theIndex (int) : Index for the argument to be updated
            theValue (object) : New value for the argument.

        Returns:
            None
        """
        arg = self.getArgoFromIndex(theIndex)
        arg.Value = theValue

    def setIndexedValueFromName(self, theName, theValue):
        """Method that sets a new value for an argument for the
        given argument name.

        Arguments indexed by name are store in _indexed attribute.

        Args:
            theName (str) : Name of the attribute to be retrieved.
            theValue (object) : New value for the argument.

        Returns:
            None
        """
        arg = self.getArgoFromName(theName)
        arg.Value = theValue

    def getIndexedValues(self):
        """Method that returns all values indexed by the argument name.

        Returns:
            list : List with all value indexed by the argument name.
        """
        return [arg.Value for name, arg in self.Indexed.items()]

    def getNames(self):
        """Method that returns the list with all indexed argumetns.

        Returns:
            list : List with all arguments indexed by argument name.
        """
        return list(self.Indexed)
