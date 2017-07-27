class CliType(object):
    """CliType class is the base class for any command argument.
    """

    def __init__(self, inpos=False, cte=False, seq=False):
        """CliType class initialization method.

        Args:
            inpos (boolean) : argument position.
            cte (boolean) : constant argument.
            seq (boolean): argument is a sequence.
        """
        self._inpos = inpos
        self._cte = cte
        self._seq = seq

    @staticmethod
    def help(text):
        """Method that returns the help for the given argument.

        Args:
            text (str): last token in the line being entered.

        Returns:
            str : string with help to send to the display.
        """
        return '\nEnter a string'

    @staticmethod
    def complete(text):
        """Method that returns the completion for the given argument.

        Args:
            text (str): last token in the line being entered.

        Returns:
            str : string with completion to send to the display.
        """
        return None

    @staticmethod
    def type():
        """Method that returns the type used for the given argument.

        Returns:
            type : argument type.
        """
        return str


class Int(object):
    """Int class is the class for any integer argument.
    """

    @staticmethod
    def _(val):
        """Method that types any value as integer.

        Args:
            val (object): value to be typed as integer.
        """
        return int(val)

    @staticmethod
    def help(text):
        """Method that returns the help for the given argument.

        Args:
            text (str): last token in the line being entered.

        Returns:
            str : string with help to send to the display.
        """
        return '\nEnter a number'

    @staticmethod
    def complete(text):
        """Method that returns the completion for the given argument.

        Args:
            text (str): last token in the line being entered.

        Returns:
            str : string with completion to send to the display.
        """
        return None

    @staticmethod
    def type():
        """Method that returns the type used for the given argument.

        Returns:
            type : argument type.
        """
        return int


class Str(object):
    """Str class is the class for any string argument.
    """

    @staticmethod
    def _(val):
        """Method that types any value as string.

        Args:
            val (object): value to be typed as string.
        """
        return str(val)

    @staticmethod
    def help(text):
        """Method that returns the help for the given argument.

        Args:
            text (str): last token in the line being entered.

        Returns:
            str : string with help to send to the display.
        """
        return '\nEnter a string'

    @staticmethod
    def complete(text):
        """Method that returns the completion for the given argument.

        Args:
            text (str): last token in the line being entered.

        Returns:
            str : string with completion to send to the display.
        """
        return None

    @staticmethod
    def type():
        """Method that returns the type used for the given argument.

        Returns:
            type : argument type.
        """
        return str
