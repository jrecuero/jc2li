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

    def _helpStr(self):
        return ''

    def help(self, text):
        """Method that returns the help for the given argument.

        Args:
            text (str): last token in the line being entered.

        Returns:
            str : string with help to send to the display.
        """
        if self._prefix:
            if self._prefix in text:
                return self._helpStr()
            else:
                return 'Enter {}'.format(self._prefix)
        return None

    def complete(self, text):
        """Method that returns the completion for the given argument.

        Args:
            text (str): last token in the line being entered.

        Returns:
            str : string with completion to send to the display.
        """
        if self._prefix and self._prefix not in text:
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

    @staticmethod
    def _(val):
        """Method that types any value as string.

        Args:
            val (object): value to be typed as string.
        """
        return str(val)

    def _helpStr(self):
        return 'Enter a string'

    @staticmethod
    def type():
        """Method that returns the type used for the given argument.

        Returns:
            type : argument type.
        """
        return str
