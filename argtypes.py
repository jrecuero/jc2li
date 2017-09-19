import loggerator

MODULE = 'ARGTYPES'


logger = loggerator.getLoggerator(MODULE)


class CliType(object):
    """CliType class is the base class for any command argument.
    """

    def __init__(self, **kwargs):
        """CliType class initialization method.

        Args:
            inpos (boolean) : argument position.
            cte (boolean) : constant argument.
            seq (boolean): argument is a sequence.
        """
        self._argo = kwargs.get('theArgo', None)
        self._prefix = '{}='.format(self._argo.Name) if self._argo.Default is not None else None

    @property
    def Argo(self):
        """Get property that returns attribute _argo

        Returns:
            Argument : argument instance
        """
        return self._argo

    @property
    def Journal(self):
        """Get property that returns the argument journal.

        Returns:
            Journal : journal instance.
        """
        return self.Argo.Journal

    @staticmethod
    def _(val):
        """Method that types any value as Tenant.

        Args:
            val (object): value to be typed as Tenant.
        """
        return str(val)

    def _helpStr(self):
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
        if not self._prefix:
            return self._helpStr()
        if self._prefix and self._prefix in text:
            return self._helpStr()
        if self._prefix and self._prefix not in text\
                and (text == ' ' or self._prefix.startswith(text)):
            return 'Enter "{}"'.format(self._prefix)
        return ""

    def complete(self, document, text):
        """Method that returns the completion for the given argument.

        Args:
            document (object) : document object with all command line
            input data.

            text (str): last token in the line being entered.

        Returns:
            str : string with completion to send to the display.
        """
        if self._prefix and self._prefix not in text\
                and (text == ' ' or self._prefix.startswith(text)):
            return [self._prefix, ]
        return None

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
        """
        return int(val)

    def _helpStr(self):
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

    def _helpStr(self):
        """Method that should return default string to be displayed as help.

        Returns:
            str : string with default help.
        """
        return 'Enter a string'
