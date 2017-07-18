import sys

cliPath = '.'
sys.path.append(cliPath)

from base import CliBase
from decorators import params, arguments, defaults, argo, setargos, setdictos, syntax, setsyntax
from decorators import command, mode
from argtypes import Int, Str


class CliTestModeClass(CliBase):

    def cmdloop(self):
        pass


class CliTestClass(CliBase):

    @params('field 1', 'field 2')
    def do_test_params(self, f1, f2):
        return f1, f2

    @arguments(Int, Str)
    def do_test_arguments(self, f1, f2):
        return f1, f2

    @defaults((Str, 'field'), (Int, 101))
    def do_test_defaults(self, f1, f2):
        return f1, f2

    @setargos
    @argo('f1', Int, 0)
    @argo('f2', Str, 'field 2')
    def do_test_argo_setargos(self, f1, f2):
        return f1, f2

    @setdictos
    @argo('f1', Str, 'field 1')
    @argo('f2', Int, 1)
    def do_test_argo_setdictos(self, f1, f2):
        return f1, f2

    @setsyntax
    @syntax('setsyntax f1 [f2]?')
    @argo('f1', Int, None)
    @argo('f2', Str, 'field 2')
    def do_test_syntax_zero_or_one(self, f1, f2):
        return f1, f2

    @setsyntax
    @syntax('setsyntax f1 [f2 | f3]?')
    @argo('f1', Int, None)
    @argo('f2', Str, 'field 2')
    @argo('f3', Int, 1)
    def do_test_setsyntax_zero_or_one_logic_or(self, f1, f2, f3):
        return f1, f2, f3

    @setsyntax
    @syntax('setsyntax f1 [f2]*')
    @argo('f1', Str, None)
    @argo('f2', Int, 0)
    def do_test_syntax_zero_or_more(self, f1, f2):
        return f1, f2

    @setsyntax
    @syntax('setsyntax f1 [f2 | f3]*')
    @argo('f1', Str, None)
    @argo('f2', Int, 0)
    @argo('f3', Str, 'field 3')
    def do_test_syntax_zero_or_more_logic_or(self, f1, f2, f3):
        return f1, f2, f3

    @setsyntax
    @syntax('setsyntax f1 [f2]+')
    @argo('f1', Str, None)
    @argo('f2', Int, None)
    def do_test_syntax_one_or_more(self, f1, f2):
        return f1, f2


@command(CliBase)
def local_command(self, line):
    return 'local cmd command'


@mode(CliBase, CliTestModeClass)
def local_mode(self, line):
    return 'local cmd mode'


@command(CliBase)
@setsyntax
@syntax('local name [id]?')
@argo('name', Str, None)
@argo('id', Int, 0)
def local(self, name, id):
    return 'local cmd command: {}'.format(name), id


@mode(CliBase, CliTestModeClass)
@setsyntax
@syntax('lmode name [id]?')
@argo('name', Str, None)
@argo('id', Int, 0)
def localmode(self, name, id):
    return 'local cmd mode: {}'.format(name), id


def test_decorator_params():
    cli = CliTestClass()
    assert cli.do_test_params('') == ('field 1', 'field 2')
    assert cli.do_test_params('"custom f1"') == ('custom f1', 'field 2')
    assert cli.do_test_params('"custom f1" "custom f2"') == ('custom f1', 'custom f2')


def test_decorator_arguments():
    cli = CliTestClass()
    assert cli.do_test_arguments('100 "custom field"') == (100, 'custom field')
    assert cli.do_test_arguments('cien "custom field"') is None


def test_decorator_defaults():
    cli = CliTestClass()
    assert cli.do_test_defaults('') == ('field', 101)
    assert cli.do_test_defaults('"custom field"') == ('custom field', 101)
    assert cli.do_test_defaults('"custom field" 202') == ('custom field', 202)


def test_decorator_argo_setargos():
    cli = CliTestClass()
    assert cli.do_test_argo_setargos('') == (0, 'field 2')
    assert cli.do_test_argo_setargos('50') == (50, 'field 2')
    assert cli.do_test_argo_setargos('101 "custom f2"') == (101, 'custom f2')


def test_decorator_argo_setdictos():
    cli = CliTestClass()
    assert cli.do_test_argo_setdictos('') == ('field 1', 1)
    assert cli.do_test_argo_setdictos('"custom f1"') == ('custom f1', 1)
    assert cli.do_test_argo_setdictos('"custom f1" 103') == ('custom f1', 103)
    assert cli.do_test_argo_setdictos('f1="custom f1"') == ('custom f1', 1)
    assert cli.do_test_argo_setdictos('f1="custom f1" f2=104') == ('custom f1', 104)
    assert cli.do_test_argo_setdictos('f2=105') == ('field 1', 105)
    assert cli.do_test_argo_setdictos('f2=106 f1="custom f1"') == ('custom f1', 106)


def test_decorator_setsyntax_zero_or_one():
    cli = CliTestClass()
    assert cli.do_test_syntax_zero_or_one('50') == (50, 'field 2')
    assert cli.do_test_syntax_zero_or_one('101 f2="custom f2"') == (101, 'custom f2')


def test_decorator_setsyntax_zero_or_one_logic_or():
    cli = CliTestClass()
    assert cli.do_test_setsyntax_zero_or_one_logic_or('50') == (50, 'field 2', 1)
    assert cli.do_test_setsyntax_zero_or_one_logic_or('101 f2="custom f2"') == (101, 'custom f2', 1)
    assert cli.do_test_setsyntax_zero_or_one_logic_or('101 f3=100') == (101, 'field 2', 100)
    assert cli.do_test_setsyntax_zero_or_one_logic_or('101 f2="garbage" f3=100') is None


def test_decorator_setsyntax_zero_or_more():
    cli = CliTestClass()
    assert cli.do_test_syntax_zero_or_more('myshelf') == ('myshelf', 0)
    assert cli.do_test_syntax_zero_or_more('myshelf f2=100') == ('myshelf', 100)


def test_decorator_setsyntax_zero_or_more_logic_or():
    cli = CliTestClass()
    assert cli.do_test_syntax_zero_or_more_logic_or('myshelf') == ('myshelf', 0, 'field 3')
    assert cli.do_test_syntax_zero_or_more_logic_or('myshelf f2=100') == ('myshelf', 100, 'field 3')
    assert cli.do_test_syntax_zero_or_more_logic_or('myshelf f3="custom f3"') == ('myshelf', 0, 'custom f3')
    assert cli.do_test_syntax_zero_or_more_logic_or('myshelf f2=100 f3="custom f3"') == ('myshelf', 100, 'custom f3')


def test_decorator_setsyntax_one_or_more():
    cli = CliTestClass()
    assert cli.do_test_syntax_one_or_more('myshelf') is None
    assert cli.do_test_syntax_one_or_more('myshelf f2=100') == ('myshelf', 100)


def test_decorator_command():
    cli = CliTestClass()
    assert cli.do_local_command('') == 'local cmd command'


def test_decorator_command_with_syntax():
    cli = CliTestClass()
    assert cli.do_local('"shelf"') == ('local cmd command: shelf', 0)


def test_decorator_mode():
    cli = CliTestClass()
    assert cli.do_local_mode('') == 'local cmd mode'


def test_decorator_mode_with_syntax():
    cli = CliTestClass()
    assert cli.do_localmode('"shelf"') == ('local cmd mode: shelf', 0)
