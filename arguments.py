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

    def __init__(self, name, argtype, **kwargs):
        """Argument class initialization method.

        Args:
            name (str) : String with the argument name.
            argtype (type) : Argument type (class name).
            default (object) : Default value for the argument.
            completer (object) : Argument completer instance.
            completer_kwargs (:class:`dict`) : Dictionary with\
                    completer arguments

        Returns:
            None
        """
        self.name = name
        self.type = argtype
        self.default = kwargs.get('default', None)
        self.value = kwargs.get('default', None)
        completer_class = kwargs.get('completer', None)
        completer_kwargs = kwargs.get('completer_kwargs', {})
        if completer_class:
            self.completer = completer_class(argo=self, **completer_kwargs)
        else:
            self.completer = argtype(argo=self, **completer_kwargs)
        self.matched = 0
        self.journal = None


class Arguments(object):
    """Arguments class will store all arguments for a given command.
    It is basically composed by every single attribute the command can have,
    so arguments can be handle in a better and more generic way.

    It basically contains two lists, _arguments with an ordered list for the
    every argument being entered, and indexed a list indexed by the attribute
    name for fast searching.
    """

    def __init__(self):
        """Arguments class initialization method.

        Returns:
            None:
        """
        self.arguments = []
        self.indexed = None

    def traverse(self):
        """Returns the list with all arguments.

        Returns:
            :any:`list` : List with all arguments.
        """
        return self.arguments

    def add_argument(self, argument):
        """Method that add a new argument.

        Args:
            argument (Argument) : New argument to the added.

        Returns:
            :any:`None`
        """
        self.arguments.append(argument)

    def insert_argument(self, argument):
        """Method that insert a new argument the first in the list.

        Args:
            argument (Argument) : New argument to be inserted first.

        Returns:
            :any:`None`
        """
        self.arguments.insert(0, argument)

    def reversed(self):
        """Method that returns the list of arguments in reverse order.

        Returns:
            list : List of argument reversed.
        """
        return reversed(self.arguments)

    def get_argo_from_index(self, index):
        """Method that returns an argument at a given index.

        Index is the place where the argument is defined at the command
        level. They are stored in _arguments attribute.

        Args:
            index (int) : Index for the argument to be returned

        Returns:
            Argument : Argument at the given index.
    """
        return self.arguments[index]

    def get_argo_from_name(self, name):
        """Method that returns an argument for the given name.

        Arguments indexed by name are store in indexed attribute.

        Args:
            name (str) : Name of the attribute to be retrieved.

        Returns:
            Argument : Argument instance if the name is found, None\
                    if the name is not found.
        """
        return self.indexed.get(name, None)

    def index(self):
        """Method that index Arguments instance. This method is required to be
        called every time a command maps CLI arguments into command arguments.

        This method initializes some internal Argument attributes (like Value
        Matched), so it has to be called every time we are matching a command.

        Returns:
            None
        """
        self.indexed = OrderedDict()
        for arg in self.arguments:
            arg.value = arg.default
            arg.matched = 0
            self.indexed.update({arg.name: arg})

    def set_indexed_value_from_index(self, index, value):
        """Method that sets a new value for an argument at the
        given index.

        Index is the place where the argument is defined at the command
        level. They are stored in _arguments attribute.

        Args:
            index (int) : Index for the argument to be updated
            value (object) : New value for the argument.

        Returns:
            None
        """
        arg = self.get_argo_from_index(index)
        arg.value = value

    def set_indexed_value_from_name(self, name, value):
        """Method that sets a new value for an argument for the
        given argument name.

        Arguments indexed by name are store in indexed attribute.

        Args:
            name (str) : Name of the attribute to be retrieved.
            value (object) : New value for the argument.

        Returns:
            None
        """
        arg = self.get_argo_from_name(name)
        arg.value = value

    def get_indexed_values(self):
        """Method that returns all values indexed by the argument name.

        Returns:
            list : List with all value indexed by the argument name.
        """
        return [arg.value for name, arg in self.indexed.items()]

    def get_names(self):
        """Method that returns the list with all indexed argumetns.

        Returns:
            list : List with all arguments indexed by argument name.
        """
        return list(self.indexed)
