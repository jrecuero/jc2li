import sys

cliPath = '.'
sys.path.append(cliPath)

from base import Cli
from decorators import argo, syntax, setsyntax
from argtypes import Str


class CliTestWorkClass(Cli):

    @setsyntax
    @syntax('multi f1 [f2 f3 f4]+')
    @argo('f1', Str, None)
    @argo('f2', Str, 'F2')
    @argo('f3', Str, 'F3')
    @argo('f4', Str, 'F4')
    def do_test_syntax_sequence_multiple(self, f1, f2, f3, f4):
        return f1, f2, f3, f4


def test_decorator_setsyntax_work():
    CliTestWorkClass()
