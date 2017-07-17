class CliType(object):

    def __init__(self, inpos=False, noname=False, cte=False, seq=False):
        self._inpos = inpos
        self._noname = noname
        self._cte = cte
        self._seq = seq

    @staticmethod
    def help(text):
        return '\nEnter a string'

    @staticmethod
    def complete(text):
        return None

    @staticmethod
    def type():
        return str


class Int(object):

    @staticmethod
    def _(val):
        return int(val)

    @staticmethod
    def help(text):
        return '\nEnter a number'

    @staticmethod
    def complete(text):
        return None

    @staticmethod
    def type():
        return int


class Str(object):

    @staticmethod
    def _(val):
        return str(val)

    @staticmethod
    def help(text):
        return '\nEnter a string'

    @staticmethod
    def complete(text):
        return None

    @staticmethod
    def type():
        return str
