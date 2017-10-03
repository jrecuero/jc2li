import sys

cliPath = '.'
sys.path.append(cliPath)

from base import Cli
from decorators import argo, setsyntax, syntax
from argtypes import Str, Dicta


class CliTestWorkClass(Cli):

    @setsyntax
    @syntax('setsyntax f1 [dicta]@')
    @argo('f1', Str, None)
    @argo('dicta', Dicta, {})
    def do_test_syntax_work(self, f1, dicta):
        return f1, dicta


def test_decorator_setsyntax_work():
    cli = CliTestWorkClass()
    assert cli.do_test_syntax_work('10 one=1') == ('10', {'one': '1'})
    assert cli.do_test_syntax_work('10 one=1 two=2') == ('10', {'one': '1', 'two': '2'})
