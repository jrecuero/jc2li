import sys

cliPath = '.'
sys.path.append(cliPath)

from cli import Cli
from decorators import argo, setsyntax, syntax
from argtypes import Str


class CliTestWorkClass(Cli):

    @setsyntax
    @syntax('setsyntax f1 [f2]?')
    @argo('f1', Str, None)
    @argo('f2', Str, 'None')
    def do_test_syntax_work(self, f1, f2):
        return f1, f2


def test_decorator_setsyntax_work():
    cli = CliTestWorkClass()
    assert cli.do_test_syntax_work('10 -f2 one') == ('10', 'one')
