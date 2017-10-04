import loggerator

MODULE = 'ARGTYPES'


logger = loggerator.getLoggerator(MODULE)


class CliType(object):
    """CliType class is the base class for any command argument.
    """

    def __init__(self, **kwargs):
        """CliType class initialization method.

        Keyword Args:
            inpos (boolean) : argument position.
            cte (boolean) : constant argument.
            seq (boolean): argument is a sequence.
            label (str) : label to be used by the type.
        """
        self.argo = kwargs.get('argo', None)
        self.label = kwargs.get('label', None)

    @property
    def journal(self):
        """Get property that returns the argument journal.

        Returns:
            Journal : journal instance.
        """
        return self.argo.journal

    def store(self, value, matched=False):
        """Stores a value in the argument for the type.

        Args:
            value (object) : Value to store in the argument.

            matched (bool) : True is argument was already matched and found\
                    in the command line entry.

        Returns:
            None
        """
        if matched:
            if type(self.argo.value) == list:
                self.argo.value.append(value)
            else:
                self.argo.value = [self.argo.value, value]
        else:
            self.argo.value = value

    @staticmethod
    def _(val):
        """Method that types any value as Tenant.

        Args:
            val (object): value to be typed as Tenant.

        Returns:
            str : String with the typed value.
        """
        return str(val)

    def _help_str(self):
        """Method that should return default string to be displayed as help.

        Returns:
            str : string with default help.
        """
        return ''

    def help(self, text):
        """Method that returns the help for the given argument.

        Args:
            text (str): last token in the line being entered.

        Returns:
            str : string with help to send to the display.
        """
        return self._help_str()

    def get_complete_list(self, document, text):
        """Gets a list with all possible options to be included in complete.

        Args:
            document (object) : document object with all command line
            input data.

            text (str): last token in the line being entered.

        Returns:
            list : list with possible complete options
        """
        return None

    def complete(self, document, text):
        """Method that returns the completion for the given argument.

        Args:
            document (object) : document object with all command line
            input data.

            text (str): last token in the line being entered.

        Returns:
            str : string with completion to send to the display.
        """
        options = self.get_complete_list(document, text)
        if options:
            if text in [' ', '']:
                return [x for x in options]
            else:
                return [x for x in options if x.startswith(text)]
        return None

    @staticmethod
    def type():
        """Method that returns the type used for the given argument.

        Returns:
            type : argument type.
        """
        return str


class Prefix(CliType):
    """Prefix class derived from CliType and is the type to be used for prefix
    nodes.
    """

    @property
    def journal(self):
        """Get property that returns the argument journal.

        Returns:
            Journal : journal instance.
        """
        return None

    def store(self, value, matched=False):
        """Stores a value in the argument for the type.

        Args:
            value (object) : Value to store in the argument.

            matched (bool) : True is argument was already matched and found\
                    in the command line entry.

        Returns:
            None
        """
        pass

    @staticmethod
    def _(val):
        """Method that types any value as Tenant.

        Args:
            val (object): value to be typed as Tenant.

        Returns:
            str : Sring with the typed value.
        """
        return str(val)

    def _help_str(self):
        """Method that should return default string to be displayed as help.

        Returns:
            str : string with default help.
        """
        return '-{0}'.format(self.label)

    def help(self, text):
        """Method that returns the help for the given argument.

        Args:
            text (str): last token in the line being entered.

        Returns:
            str : string with help to send to the display.
        """
        return self._help_str()

    def complete(self, document, text):
        """Method that returns the completion for the given argument.

        Args:
            document (object) : document object with all command line
            input data.

            text (str): last token in the line being entered.

        Returns:
            str : string with completion to send to the display.
        """
        return ['-{0}'.format(self.label), ]

    @staticmethod
    def type():
        """Method that returns the type used for the given argument.

        Returns:
            type : argument type.
        """
        return str


class Int(CliType):
    """Int class is the class for any integer argument.
    """

    @staticmethod
    def _(val):
        """Method that types any value as integer.

        Args:
            val (object): value to be typed as integer.

        Returns:
            int : Integer with the typed value.
        """
        return int(val)

    def _help_str(self):
        """Method that should return default string to be displayed as help.

        Returns:
            str : string with default help.
        """
        return 'Enter a number'

    @staticmethod
    def type():
        """Method that returns the type used for the given argument.

        Returns:
            type : argument type.
        """
        return int


class Str(CliType):
    """Str class is the class for any string argument.
    """

    def _help_str(self):
        """Method that should return default string to be displayed as help.

        Returns:
            str : string with default help.
        """
        return 'Enter a string'


class Dicta(Str):
    """Dicta class is the class for any dictionary argument.
    """

    def store(self, value, matched=False):
        """Stores a value in the argument for the type.

        Args:
            value (object) : Value to store in the argument.

            matched (bool) : True is argument was already matched and found\
                    in the command line entry.

        Returns:
            None
        """
        name, val = value.split('=')
        if matched:
            self.argo.value.update({name: val})
        else:
            self.argo.value = {name: val}
