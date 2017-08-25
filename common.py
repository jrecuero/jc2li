from collections import OrderedDict


ARGOS_ATTR = '_Arguments'
RULES_ATTR = '_Rules'
SYNTAX_ATTR = '_Syntax'
CMD_ATTR = '_Cmd'
TREE_ATTR = '_Tree'


def _HANDLE_ERROR(st):
    """
    """
    print(st)
    return None


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


class RuleHandler(object):
    """RuleHandler class is a helper class that only contains static methods
    which are being used for handling rules dictionary. Rules dictionary is
    the output generated by the syntax parsing.
    """

    @staticmethod
    def checkForInnerRule(theRule):
        """Static method that check if a rule has other rules inside.

        Args:
            theRule (dict): dictionary with the given rule to check.

        Returns:
            boolean : True if the has same inner rules, False else.
        """
        return theRule['type'] in '?*+' or type(theRule['args']) == list

    @staticmethod
    def checkArgNameInRule(theRule, theArgName):
        """Static method that checks if an argument has a given name.

        It only checks when the rule type is "1" (argument names are only
        set for this type).

        Args:
            theRule (dict): dictionary with the given rule to check.
            theArgName (str) L String with the argument name to check.

        Returns:
            boolean : True if the arguments matches the given name, False else.
        """
        if theRule['type'] == '1' and theRule['args'] == theArgName:
            return True
        return False

    @staticmethod
    def syntaxMinArgs(theRules):
        """Static method that returns the minimum number of arguemnt to be
        entered by the user for a given command.

        All argument which main rule type is "1" are required arguments, and
        all arguements which main rule type is "+" are named arguments that
        have to appear at leas one time.

        Args:
            theRule (dict): dictionary with the given rule to check.

        Returns:
            int : number of minimum arguments to be entered at the CLI.
        """
        counter = sum([1 if rule['type'] in '1+' else 0 for rule in theRules])
        return counter

    @staticmethod
    def getArgsFromRuleAsList(theRule):
        """Static method that return a list with all rules contained in the
        'args' entry for the rules dictionary

        Args:
            theRule (dict): dictionary with the given rule to check.

        Returns:
            list : list with all rules contained in 'args' entry.
        """
        return theRule['args'] if type(theRule['args']) == list else [theRule, ]

    @staticmethod
    def getArgsFromRule(theRule):
        """Static method that returns the value for the 'args' entry in the
        rules dictionary.

        Args:
            theRule (dict): dictionary with the given rule to check.

        Returns:
            list/str : content of 'args' entry, it could be a list with more
            rules or a string with the argument name.
        """
        return theRule['args']

    @staticmethod
    def getCounterFromRule(theRule):
        """Static method that returns the value for the 'counter' entry in the
        rules dictionary.

        Counter stores the rule order in relation with all other rules.

        Args:
            theRule (dict): dictionary with the given rule to check.

        Returns:
            int : rule counter number.
        """
        return theRule['counter']

    @staticmethod
    def traverseArgsInRule(theRule):
        """Static method that traverses all entries in 'args' entry for the
        rules dictionary.

        Args:
            theRule (dict): dictionary with the given rule to check.

        Returns:
            dict : yield with a rule.
        """
        for rule in theRule['args']:
            yield rule

    @staticmethod
    def isOnlyOneRule(theRule):
        """Static method that checks if the rule contains an argument name.

        Args:
            theRule (dict): dictionary with the given rule to check.

        Returns:
            boolean : True if the argument contains an argument name, False else
        """
        return theRule['type'] == '1'

    @staticmethod
    def isEndRule(theRule):
        """Static method that checks if the rule contains the last rule for the
        command.

        Args:
            theRule (dict): dictionary with the given rule to check.

        Returns:
            boolean : True if the argument contains the last rule, False else
        """
        return theRule['type'] == '0'

    @staticmethod
    def isZeroOrOneRule(theRule):
        """Static method that checks if the rule contains an argument that can
        be entered zero or one time.

        Args:
            theRule (dict): dictionary with the given rule to check.

        Returns:
            boolean : True if the argument can be entered zero or one, False else
        """
        return theRule['type'] == '?'

    @staticmethod
    def isZeroOrMoreRule(theRule):
        """Static method that checks if the rule contains an argument that can
        be entered zero or more times.

        Args:
            theRule (dict): dictionary with the given rule to check.

        Returns:
            boolean : True if the argument can be entered zero or more, False else
        """
        return theRule['type'] == '*'

    @staticmethod
    def isOneOrMoreRule(theRule):
        """Static method that checks if the rule contains an argument that can
        be entered one or more times.

        Args:
            theRule (dict): dictionary with the given rule to check.

        Returns:
            boolean : True if the argument can be entered one or more, False else
        """
        return theRule['type'] == '+'


if __name__ == '__main__':
    pass
